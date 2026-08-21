#!/usr/bin/env python3
"""zot2bbt: Zotero sqlite -> Better BibTeX 형태 JSON 배열.

Better BibTeX 확장 없이 zotero.sqlite에서 직접 뽑아, ARS의
scripts/adapters/zotero.py 가 먹는 BBT JSON export 모양으로 내보낸다.

  python zot2bbt.py --collection 4 --out bbt.json
  python zot2bbt.py --selftest

ARS 어댑터가 실제로 읽는 필드만 채운다(어댑터 main() 기준):
  citationKey / itemID / key / itemType / title / creators[] / date
  publicationTitle|proceedingsTitle|bookTitle / DOI / tags[] / abstractNote
"""
from __future__ import annotations
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from zotlib import (  # noqa: E402
    DEFAULT_DATA_DIR, open_db, q, bib_item_ids, fields_of, creators_of,
    meta_of, year_of, _chunks, _citekey,
)

# 학위논문은 Zotero가 학교명을 university 필드에 넣는데 ARS 어댑터의 venue
# 후보(publicationTitle/proceedingsTitle/bookTitle)에는 없다. thesis 한정으로
# university를 publicationTitle 자리에 실어 venue를 살린다.
VENUE_FALLBACK = {"thesis": "university"}


def tags_of(db, item_ids):
    """{itemID: [tagName]}"""
    if not item_ids:
        return {}
    out = defaultdict(list)
    for chunk in _chunks(item_ids, 800):
        rows = q(db, f"""
            SELECT it.itemID, t.name nm
            FROM itemTags it JOIN tags t ON t.tagID = it.tagID
            WHERE it.itemID IN ({','.join('?' * len(chunk))})
            ORDER BY it.itemID, t.name""", chunk)
        for r in rows:
            out[r["itemID"]].append(r["nm"])
    return out


def to_bbt(item_id, key, item_type, f, creators, tags, citekey):
    """(순수 함수) 한 항목을 BBT JSON dict로. f=fieldName->value 매핑."""
    item = {
        "itemID": item_id,
        "key": key,
        "itemType": item_type,
        "citationKey": citekey,
        "title": f.get("title") or f.get("caseName") or f.get("subject") or "",
        "date": f.get("date") or "",
        "creators": [
            # fieldMode==1 = 기관/단체 저자 -> BBT의 name 형태(어댑터가 literal로 받음).
            # 여기서 lastName으로 내리면 개인명 {family:...}이 되어 기관명이 성으로 둔갑한다.
            {"creatorType": ct, "name": ln} if fm == 1
            else {"creatorType": ct, "lastName": ln, "firstName": fn}
            for ct, _disp, ln, fn, fm in creators
        ],
    }
    venue = f.get("publicationTitle") or f.get(VENUE_FALLBACK.get(item_type, ""), "")
    if venue:
        item["publicationTitle"] = venue
    for src, dst in (("proceedingsTitle", "proceedingsTitle"), ("bookTitle", "bookTitle")):
        if f.get(src):
            item[dst] = f[src]
    if f.get("DOI"):
        item["DOI"] = f["DOI"]
    if f.get("abstractNote"):
        item["abstractNote"] = f["abstractNote"]
    if tags:
        item["tags"] = [{"tag": t} for t in tags]
    return item


def build(db, data_dir, collection):
    ids = bib_item_ids(db, collection)
    F, C, M, T = fields_of(db, ids), creators_of(db, ids), meta_of(db, ids), tags_of(db, ids)
    # citekey는 저자/연도 기반이라 순서가 바뀌면 접미사(a/b)가 흔들린다.
    # 안정적 출력을 위해 itemID 순으로 고정해 부여한다.
    used, items = set(), []
    for iid in sorted(ids):
        f, m = F.get(iid, {}), M.get(iid, {})
        creators = C.get(iid, [])
        shim = {
            "authors": [c[1] for c in creators if c[0] in ("author", "editor", "contributor")],
            "key": m.get("key"), "year": year_of(f.get("date")), "itemID": iid,
        }
        items.append(to_bbt(iid, m.get("key"), m.get("type"), f, creators,
                            T.get(iid, []), _citekey(shim, used)))
    return items


def selftest():
    f = {"title": "다문화 교육 정책 연구", "date": "2019-03", "abstractNote": "요약",
         "university": "서울대학교", "DOI": "10.1234/x"}
    creators = [("author", "국가인권위원회", "국가인권위원회", "", 1),
                ("author", "김철수", "김", "철수", 0),
                ("editor", "박영희", "박", "영희", 0)]
    it = to_bbt(11, "ABCD1234", "thesis", f, creators, ["인권", "다문화"], "nhrc2019")
    assert it["creators"][0] == {"creatorType": "author", "name": "국가인권위원회"}, it["creators"][0]
    assert it["creators"][1] == {"creatorType": "author", "lastName": "김", "firstName": "철수"}
    assert it["publicationTitle"] == "서울대학교", "thesis venue fallback 실패"
    assert it["tags"] == [{"tag": "인권"}, {"tag": "다문화"}]
    assert it["DOI"] == "10.1234/x" and it["date"] == "2019-03"

    # journalArticle은 university fallback을 타면 안 된다
    j = to_bbt(12, "K2", "journalArticle", {"title": "T", "university": "X"}, [], [], "k2")
    assert "publicationTitle" not in j, j

    # 필수값이 비면 빈 문자열로 흘려보내고 판정은 ARS 어댑터의 rejection_log에 맡긴다
    e = to_bbt(13, "K3", "book", {}, [], [], "k3")
    assert e["title"] == "" and e["creators"] == [] and e["date"] == ""
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--collection", type=int, help="컬렉션 id (생략 시 전체 서재)")
    ap.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    ap.add_argument("--out", type=Path, help="출력 JSON 경로 (생략 시 stdout)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return 0
    db = open_db(a.data_dir)
    items = build(db, a.data_dir, a.collection)
    text = json.dumps(items, ensure_ascii=False, indent=1)
    if a.out:
        a.out.write_text(text, encoding="utf-8")
        print(f"{len(items)} items -> {a.out}", file=sys.stderr)
    else:
        sys.stdout.buffer.write(text.encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
