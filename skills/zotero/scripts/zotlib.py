# -*- coding: utf-8 -*-
"""
zotlib.py — Zotero 로컬 라이브러리 조회 도구 (읽기 전용, 표준 라이브러리만 사용)

zotero.sqlite를 임시 폴더로 복사해 읽으므로 Zotero 실행 여부와 무관하며
원본 DB를 절대 건드리지 않는다.
(파일명은 표준 모듈 zlib 과 충돌하지 않도록 zotlib 으로 고정한다.)

사용법:
  python zotlib.py stats                        라이브러리 개요
  python zotlib.py collections                  컬렉션 트리
  python zotlib.py search <검색어> [-n 30]       제목/저자/초록/출판물 검색
  python zotlib.py show <itemID|key>            항목 상세 + 첨부 경로
  python zotlib.py list [-c 컬렉션ID] [-n 50]    항목 목록
  python zotlib.py diag [-c 컬렉션ID]            서지 품질 진단 리포트
  python zotlib.py orphans [-n 300]             부모 없는 독립 첨부(인용 불가) 목록
  python zotlib.py dups                         중복 후보
  python zotlib.py bib [-c 컬렉션ID] [-o out.bib]  BibTeX 내보내기
  python zotlib.py csv [-c 컬렉션ID] [-o out.csv]  표 내보내기
  python zotlib.py pdf <itemID|key>             해당 항목의 PDF 실제 경로 출력
  python zotlib.py pdfs [-c 컬렉션ID]            PDF 전체 경로 목록

공통 옵션: --json (기계 판독용), --data-dir <경로>
"""
from __future__ import annotations

import argparse
import csv as csvmod
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
from collections import Counter, defaultdict

DEFAULT_DATA_DIR = os.path.join(os.path.expanduser("~"), "Zotero")
try:  # paper-toolkit 공용 설정에 zotero_dir가 있으면 그 값을 기본으로
    import json as _json
    with open(os.environ.get("PAPER_TOOLKIT_CONFIG") or os.path.join(os.path.expanduser("~"), ".config", "paper-toolkit", "config.json"), encoding="utf-8") as _f:
        DEFAULT_DATA_DIR = _json.load(_f).get("zotero_dir") or DEFAULT_DATA_DIR
except (OSError, ValueError):
    pass
NON_BIB = ("attachment", "note", "annotation")


# ─────────────────────────────────────────── DB

def open_db(data_dir: str) -> sqlite3.Connection:
    src = os.path.join(data_dir, "zotero.sqlite")
    if not os.path.exists(src):
        sys.exit(f"[!] zotero.sqlite 없음: {src}\n    Zotero를 설치했는지 확인하세요(zotero.org). 데이터 폴더가 다른 곳이면: zotlib.py --data-dir <폴더> <명령>")
    tmp = os.path.join(tempfile.gettempdir(), "zlib_snapshot.sqlite")
    for suffix in ("", "-wal", "-shm"):
        s = src + suffix
        if os.path.exists(s):
            shutil.copy2(s, tmp + suffix)
        elif os.path.exists(tmp + suffix):
            os.remove(tmp + suffix)
    db = sqlite3.connect(f"file:{tmp}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    return db


def q(db, sql, params=()):
    return db.execute(sql, params).fetchall()


# ─────────────────────────────────────────── 조회 헬퍼

def bib_item_ids(db, collection_id=None, recursive=True):
    """서지 항목(첨부/노트 제외) itemID 목록."""
    sql = f"""
      SELECT i.itemID FROM items i
      JOIN itemTypes it ON it.itemTypeID = i.itemTypeID
      LEFT JOIN deletedItems d ON d.itemID = i.itemID
      WHERE d.itemID IS NULL AND it.typeName NOT IN ({','.join('?' * len(NON_BIB))})
    """
    params = list(NON_BIB)
    if collection_id:
        ids = collection_tree_ids(db, collection_id) if recursive else [collection_id]
        sql += f" AND i.itemID IN (SELECT itemID FROM collectionItems WHERE collectionID IN ({','.join('?' * len(ids))}))"
        params += ids
    return [r["itemID"] for r in q(db, sql, params)]


def collection_tree_ids(db, root_id):
    out, stack = [], [int(root_id)]
    while stack:
        cid = stack.pop()
        out.append(cid)
        stack += [r["collectionID"] for r in
                  q(db, "SELECT collectionID FROM collections WHERE parentCollectionID=?", (cid,))]
    return out


def fields_of(db, item_ids):
    """{itemID: {fieldName: value}}"""
    if not item_ids:
        return {}
    out = defaultdict(dict)
    for chunk in _chunks(item_ids, 800):
        rows = q(db, f"""
            SELECT idt.itemID, f.fieldName fn, idv.value v
            FROM itemData idt
            JOIN fields f ON f.fieldID = idt.fieldID
            JOIN itemDataValues idv ON idv.valueID = idt.valueID
            WHERE idt.itemID IN ({','.join('?' * len(chunk))})""", chunk)
        for r in rows:
            out[r["itemID"]][r["fn"]] = r["v"]
    return out


def creators_of(db, item_ids):
    """{itemID: [(creatorType, 표시이름, lastName, firstName, fieldMode)]}

    fieldMode==1 이면 기관/단체 저자(lastName 한 칸에 전체 이름). 튜플 뒤에
    덧붙인 값이라 앞 4개만 쓰는 기존 호출부(record 등)는 영향 없음."""
    if not item_ids:
        return {}
    out = defaultdict(list)
    for chunk in _chunks(item_ids, 800):
        rows = q(db, f"""
            SELECT ic.itemID, ct.creatorType ct, c.lastName ln, c.firstName fn, c.fieldMode fm
            FROM itemCreators ic
            JOIN creators c ON c.creatorID = ic.creatorID
            JOIN creatorTypes ct ON ct.creatorTypeID = ic.creatorTypeID
            WHERE ic.itemID IN ({','.join('?' * len(chunk))})
            ORDER BY ic.itemID, ic.orderIndex""", chunk)
        for r in rows:
            ln, fn = r["ln"] or "", r["fn"] or ""
            disp = ln if (r["fm"] == 1 or not fn) else f"{ln}, {fn}"
            out[r["itemID"]].append((r["ct"], disp, ln, fn, r["fm"]))
    return out


def meta_of(db, item_ids):
    """{itemID: {key, typeName, dateAdded}}"""
    if not item_ids:
        return {}
    out = {}
    for chunk in _chunks(item_ids, 800):
        for r in q(db, f"""
            SELECT i.itemID, i.key, i.dateAdded, it.typeName ty
            FROM items i JOIN itemTypes it ON it.itemTypeID = i.itemTypeID
            WHERE i.itemID IN ({','.join('?' * len(chunk))})""", chunk):
            out[r["itemID"]] = {"key": r["key"], "type": r["ty"], "dateAdded": r["dateAdded"]}
    return out


def attachments_of(db, item_ids, data_dir):
    """{parentItemID: [ {itemID,key,path,contentType,title,abspath} ]}"""
    if not item_ids:
        return {}
    out = defaultdict(list)
    for chunk in _chunks(item_ids, 800):
        for r in q(db, f"""
            SELECT ia.itemID, ia.parentItemID pid, ia.path, ia.contentType ct, ia.linkMode lm, i.key
            FROM itemAttachments ia
            JOIN items i ON i.itemID = ia.itemID
            LEFT JOIN deletedItems d ON d.itemID = ia.itemID
            WHERE d.itemID IS NULL AND ia.parentItemID IN ({','.join('?' * len(chunk))})""", chunk):
            out[r["pid"]].append(_att(r, data_dir))
    return out


def _att(r, data_dir):
    path, key = r["path"] or "", r["key"]
    abspath = None
    if path.startswith("storage:"):
        abspath = os.path.join(data_dir, "storage", key, path[len("storage:"):])
    elif path.startswith("attachments:"):
        abspath = path[len("attachments:"):]
    elif path:
        abspath = path
    return {"itemID": r["itemID"], "key": key, "path": path,
            "contentType": r["ct"], "abspath": abspath,
            "exists": bool(abspath and os.path.exists(abspath))}


def year_of(datestr):
    if not datestr:
        return None
    m = re.search(r"(1[6-9]\d{2}|20\d{2})", str(datestr))
    return int(m.group(1)) if m else None


def _chunks(seq, n):
    for i in range(0, len(seq), n):
        yield list(seq[i:i + n])


def record(db, item_ids, data_dir, with_att=True):
    """조회 결과를 dict 리스트로 조립."""
    F, C, M = fields_of(db, item_ids), creators_of(db, item_ids), meta_of(db, item_ids)
    A = attachments_of(db, item_ids, data_dir) if with_att else {}
    recs = []
    for iid in item_ids:
        f, m = F.get(iid, {}), M.get(iid, {})
        authors = [c[1] for c in C.get(iid, []) if c[0] in ("author", "editor", "contributor")]
        recs.append({
            "itemID": iid, "key": m.get("key"), "type": m.get("type"),
            "title": f.get("title") or f.get("caseName") or f.get("subject") or "",
            "authors": authors,
            "year": year_of(f.get("date")), "date": f.get("date") or "",
            "publication": f.get("publicationTitle") or f.get("bookTitle")
                           or f.get("university") or f.get("proceedingsTitle") or "",
            "volume": f.get("volume") or "", "issue": f.get("issue") or "",
            "pages": f.get("pages") or "", "DOI": f.get("DOI") or "",
            "url": f.get("url") or "", "language": f.get("language") or "",
            "abstract": f.get("abstractNote") or "",
            "publisher": f.get("publisher") or "", "place": f.get("place") or "",
            "dateAdded": m.get("dateAdded"),
            "attachments": A.get(iid, []),
        })
    return recs


def is_korean(rec):
    lang = (rec.get("language") or "").lower()
    if lang.startswith("ko"):
        return True
    if lang and not lang.startswith("ko"):
        return False
    return bool(re.search(r"[가-힣]", rec.get("title", "")))


# ─────────────────────────────────────────── 출력

def out(obj, as_json):
    if as_json:
        print(json.dumps(obj, ensure_ascii=False, indent=2, default=str))
        return True
    return False


def fmt_rec(r, idx=None):
    au = ", ".join(r["authors"][:3]) or "(저자없음)"
    if len(r["authors"]) > 3:
        au += " 외"
    head = f"[{r['itemID']}]" if idx is None else f"{idx:>3}. [{r['itemID']}]"
    pub = f" · {r['publication']}" if r["publication"] else ""
    npdf = sum(1 for a in r["attachments"] if (a["contentType"] or "").endswith("pdf"))
    flag = f" 📄{npdf}" if npdf else ""
    return f"{head} {r['year'] or '----'} {au}{flag}\n      {r['title'][:88]}{pub}"


# ─────────────────────────────────────────── 명령

def cmd_stats(db, a):
    dd = a.data_dir
    types = q(db, """SELECT it.typeName t, COUNT(*) n FROM items i
        JOIN itemTypes it ON it.itemTypeID=i.itemTypeID
        LEFT JOIN deletedItems d ON d.itemID=i.itemID
        WHERE d.itemID IS NULL GROUP BY it.typeName ORDER BY n DESC""")
    ids = bib_item_ids(db)
    recs = record(db, ids, dd)
    orphan = q(db, """SELECT COUNT(*) c FROM itemAttachments ia
        LEFT JOIN deletedItems d ON d.itemID=ia.itemID
        WHERE ia.parentItemID IS NULL AND d.itemID IS NULL""")[0]["c"]
    years = Counter(r["year"] for r in recs if r["year"])
    data = {
        "dataDir": dd, "서지항목": len(ids), "독립첨부": orphan,
        "타입별": {r["t"]: r["n"] for r in types},
        "한글문헌": sum(1 for r in recs if is_korean(r)),
        "연도범위": [min(years), max(years)] if years else None,
    }
    if out(data, a.json):
        return
    print(f"데이터 폴더 : {dd}")
    print(f"서지 항목   : {len(ids)}건   (한글 {data['한글문헌']} / 외국어 {len(ids)-data['한글문헌']})")
    print(f"독립 첨부   : {orphan}건  ← 부모 서지항목 없음 = 인용 불가")
    print("\n타입별:")
    for r in types:
        print(f"  {r['t']:<18} {r['n']:>5}")
    if years:
        print(f"\n연도: {min(years)}~{max(years)}   최근5년(2021~) "
              f"{sum(v for k,v in years.items() if k>=2021)}건")


def cmd_collections(db, a):
    rows = q(db, """SELECT c.collectionID id, c.collectionName nm, c.parentCollectionID pid,
        (SELECT COUNT(*) FROM collectionItems ci WHERE ci.collectionID=c.collectionID) n
        FROM collections c ORDER BY c.collectionName""")
    if out([dict(r) for r in rows], a.json):
        return
    kids = defaultdict(list)
    for r in rows:
        kids[r["pid"]].append(r)

    def walk(pid, depth):
        for r in kids.get(pid, []):
            bib = len(bib_item_ids(db, r["id"]))
            print(f"{'   ' * depth}{'└ ' if depth else ''}{r['nm']}  "
                  f"[전체 {r['n']} / 서지 {bib}]  id={r['id']}")
            walk(r["id"], depth + 1)
    walk(None, 0)


def cmd_list(db, a):
    ids = bib_item_ids(db, a.collection)
    recs = record(db, ids, a.data_dir)
    recs.sort(key=lambda r: (r["year"] or 0), reverse=True)
    recs = recs[:a.n]
    if out(recs, a.json):
        return
    for i, r in enumerate(recs, 1):
        print(fmt_rec(r, i))


def cmd_search(db, a):
    term = a.query.lower()
    ids = bib_item_ids(db, a.collection)
    recs = record(db, ids, a.data_dir)
    hits = [r for r in recs if term in " ".join([
        r["title"], " ".join(r["authors"]), r["publication"], r["abstract"]]).lower()]
    hits.sort(key=lambda r: (r["year"] or 0), reverse=True)
    hits = hits[:a.n]
    if out(hits, a.json):
        return
    print(f"'{a.query}' → {len(hits)}건\n")
    for i, r in enumerate(hits, 1):
        print(fmt_rec(r, i))


def cmd_show(db, a):
    iid = _resolve(db, a.ident)
    recs = record(db, [iid], a.data_dir)
    if not recs:
        sys.exit("[!] 항목 없음")
    r = recs[0]
    if out(r, a.json):
        return
    print(f"itemID {r['itemID']}  key {r['key']}  type {r['type']}")
    print(f"제목   {r['title']}")
    print(f"저자   {', '.join(r['authors']) or '(없음)'}")
    print(f"연도   {r['date'] or '(없음)'}")
    print(f"출처   {r['publication']} {r['volume']}({r['issue']}) {r['pages']}".rstrip())
    print(f"DOI    {r['DOI'] or '(없음)'}")
    print(f"언어   {r['language'] or '(없음)'}")
    if r["abstract"]:
        print(f"초록   {r['abstract'][:400]}")
    print("첨부:")
    for at in r["attachments"]:
        print(f"  {'OK ' if at['exists'] else '없음'} {at['contentType']}  {at['abspath']}")


def _resolve(db, ident):
    if str(ident).isdigit():
        return int(ident)
    rows = q(db, "SELECT itemID FROM items WHERE key=?", (ident,))
    if not rows:
        sys.exit(f"[!] key 못 찾음: {ident}")
    return rows[0]["itemID"]


def cmd_orphans(db, a):
    rows = q(db, """SELECT ia.itemID, i.key, ia.path, ia.contentType ct, i.dateAdded da
        FROM itemAttachments ia JOIN items i ON i.itemID=ia.itemID
        LEFT JOIN deletedItems d ON d.itemID=ia.itemID
        WHERE ia.parentItemID IS NULL AND d.itemID IS NULL
        ORDER BY i.dateAdded DESC""")
    items = []
    for r in rows[:a.n]:
        at = _att(r, a.data_dir)
        at["filename"] = os.path.basename(at["abspath"] or at["path"] or "")
        items.append(at)
    if out(items, a.json):
        return
    print(f"부모 서지항목 없는 첨부 {len(rows)}건 (표시 {len(items)}건)")
    print("→ 서지정보가 없어 인용·BibTeX 생성 불가. Zotero에서 'PDF 메타데이터 가져오기' 필요\n")
    for i, at in enumerate(items, 1):
        mark = "" if at["exists"] else "  [파일없음]"
        print(f"{i:>3}. [{at['itemID']}] {at['filename'][:84]}{mark}")


def cmd_dups(db, a):
    ids = bib_item_ids(db, a.collection)
    recs = record(db, ids, a.data_dir, with_att=False)
    buckets = defaultdict(list)
    for r in recs:
        k = re.sub(r"[^0-9a-z가-힣]", "", r["title"].lower())[:60]
        if k:
            buckets[k].append(r)
    dups = {k: v for k, v in buckets.items() if len(v) > 1}
    if out([[{"itemID": r["itemID"], "title": r["title"], "year": r["year"]} for r in v]
            for v in dups.values()], a.json):
        return
    print(f"중복 후보 {len(dups)}쌍\n")
    for v in dups.values():
        print(f"  ▸ {v[0]['title'][:72]}")
        for r in v:
            print(f"      itemID {r['itemID']}  {r['year'] or '----'}  "
                  f"{', '.join(r['authors'][:2]) or '(저자없음)'}")


def cmd_diag(db, a):
    ids = bib_item_ids(db, a.collection)
    recs = record(db, ids, a.data_dir)
    n = len(recs) or 1
    orphan = q(db, """SELECT COUNT(*) c FROM itemAttachments ia
        LEFT JOIN deletedItems d ON d.itemID=ia.itemID
        WHERE ia.parentItemID IS NULL AND d.itemID IS NULL""")[0]["c"]

    missing = {
        "저자": [r for r in recs if not r["authors"]],
        "연도": [r for r in recs if not r["year"]],
        "제목": [r for r in recs if not r["title"]],
        "학술지/출처": [r for r in recs if not r["publication"] and r["type"] == "journalArticle"],
        "페이지": [r for r in recs if not r["pages"] and r["type"] == "journalArticle"],
        "DOI": [r for r in recs if not r["DOI"] and r["type"] == "journalArticle"],
    }
    years = Counter(r["year"] for r in recs if r["year"])
    dated = sum(years.values()) or 1
    recent5 = sum(v for k, v in years.items() if k >= 2021)
    kor = sum(1 for r in recs if is_korean(r))
    buckets = defaultdict(list)
    for r in recs:
        k = re.sub(r"[^0-9a-z가-힣]", "", r["title"].lower())[:60]
        if k:
            buckets[k].append(r)
    ndup = sum(1 for v in buckets.values() if len(v) > 1)
    citable = [r for r in recs if r["authors"] and r["year"] and r["title"]]

    data = {
        "서지항목": len(recs), "인용가능": len(citable), "독립첨부": orphan,
        "결손": {k: len(v) for k, v in missing.items()},
        "중복쌍": ndup, "한글문헌": kor, "외국문헌": len(recs) - kor,
        "최근5년비율": round(recent5 * 100 / dated, 1),
    }
    if out(data, a.json):
        return

    def bar(x, tot, w=24):
        f = int(round(w * x / max(tot, 1)))
        return "█" * f + "·" * (w - f)

    print("=" * 66)
    print(" ZOTERO 서지 품질 진단" + (f"  (컬렉션 {a.collection})" if a.collection else "  (전체)"))
    print("=" * 66)
    print(f"\n 서지 항목        {len(recs):>4}건")
    print(f" 인용 가능        {len(citable):>4}건   {bar(len(citable), n)} {len(citable)*100//n}%")
    print(f"   └ 저자·연도·제목이 모두 있어야 인용문 생성 가능")
    print(f" 독립 첨부        {orphan:>4}건   ← 서지정보 없는 PDF, 인용 불가")

    print("\n 필드 결손")
    for k, v in missing.items():
        if v:
            print(f"   {k:<12} {len(v):>3}건 결손  {bar(n-len(v), n)}")
    if not any(missing.values()):
        print("   (없음)")

    print(f"\n 중복 후보        {ndup:>4}쌍")
    print(f" 한글 : 외국어    {kor} : {len(recs)-kor}")
    print(f" 최근 5년(2021~)  {data['최근5년비율']}%  (권장 30~40%)")

    print("\n 권고")
    if orphan:
        print(f"   1. 독립 첨부 {orphan}건에 메타데이터 부여  →  zlib.py orphans 로 목록 확인")
    if missing["저자"]:
        print(f"   2. 저자 결손 {len(missing['저자'])}건 보완 — 이대로는 참고문헌 목록에 못 올림")
    if ndup:
        print(f"   3. 중복 {ndup}쌍 병합  →  Zotero 좌측 '중복 항목' 창")
    if kor < 10:
        print(f"   4. 한글 선행연구 {kor}건 — KCI 등재지 기준 최소 10~15건 필요")
    if data["최근5년비율"] < 30:
        print(f"   5. 최근 5년 문헌 비율 {data['최근5년비율']}% — 연구 동향 미반영 지적 위험")


def _citekey(r, used):
    base = ""
    if r["authors"]:
        last = r["authors"][0].split(",")[0]
        base = re.sub(r"[^A-Za-z]", "", last)
        if not base:
            base = re.sub(r"[^0-9A-Za-z]", "", r["key"] or "")[:8]
    if not base:
        base = f"item{r['itemID']}"
    key = f"{base}{r['year'] or 'nd'}"
    k, i = key, 1
    while k in used:
        k = key + chr(ord('a') + i - 1)
        i += 1
    used.add(k)
    return k


BIB_TYPE = {"journalArticle": "article", "book": "book", "bookSection": "incollection",
            "thesis": "phdthesis", "conferencePaper": "inproceedings",
            "report": "techreport", "webpage": "misc", "document": "misc",
            "manuscript": "unpublished", "magazineArticle": "article",
            "newspaperArticle": "article"}


def cmd_bib(db, a):
    ids = bib_item_ids(db, a.collection)
    recs = record(db, ids, a.data_dir, with_att=False)
    recs.sort(key=lambda r: (r["authors"][0] if r["authors"] else "zzz", r["year"] or 0))
    used, chunks = set(), []
    for r in recs:
        ck = _citekey(r, used)
        ty = BIB_TYPE.get(r["type"], "misc")
        f = []

        def add(k, v):
            if v:
                f.append(f"  {k} = {{{v}}}")
        add("title", r["title"])
        add("author", " and ".join(r["authors"]))
        add("year", r["year"])
        if ty == "phdthesis":
            add("school", r["publication"])
        elif ty in ("incollection", "inproceedings"):
            add("booktitle", r["publication"])
        else:
            add("journal", r["publication"])
        add("volume", r["volume"]); add("number", r["issue"]); add("pages", r["pages"])
        add("doi", r["DOI"]); add("url", r["url"]); add("publisher", r["publisher"])
        add("address", r["place"]); add("language", r["language"])
        add("note", f"zotero:{r['key']}")
        chunks.append(f"@{ty}{{{ck},\n" + ",\n".join(f) + "\n}")
    text = ("% Zotero 라이브러리 내보내기 (zlib.py)\n"
            f"% 항목 {len(recs)}건\n"
            "% 주의: Better BibTeX 설치 후에는 BBT 자동 export를 정본으로 사용할 것\n\n"
            + "\n\n".join(chunks) + "\n")
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)) or ".", exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as fp:
            fp.write(text)
        print(f"[OK] {len(recs)}건 → {a.out}")
    else:
        print(text)


def cmd_csv(db, a):
    ids = bib_item_ids(db, a.collection)
    recs = record(db, ids, a.data_dir, with_att=False)
    recs.sort(key=lambda r: (r["year"] or 0), reverse=True)
    cols = ["itemID", "key", "type", "year", "authors", "title", "publication",
            "volume", "issue", "pages", "DOI", "language", "url"]
    rows = [{**r, "authors": "; ".join(r["authors"])} for r in recs]
    target = a.out or os.path.join(a.data_dir, "..", "zotero_export.csv")
    with open(target, "w", encoding="utf-8-sig", newline="") as fp:
        w = csvmod.DictWriter(fp, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"[OK] {len(rows)}건 → {os.path.abspath(target)}")


def cmd_pdf(db, a):
    iid = _resolve(db, a.ident)
    recs = record(db, [iid], a.data_dir)
    paths = [x["abspath"] for x in recs[0]["attachments"]
             if (x["contentType"] or "").endswith("pdf") and x["exists"]]
    if out(paths, a.json):
        return
    for p in paths:
        print(p)
    if not paths:
        print("(PDF 첨부 없음)")


def cmd_pdfs(db, a):
    ids = bib_item_ids(db, a.collection)
    recs = record(db, ids, a.data_dir)
    rows = []
    for r in recs:
        for at in r["attachments"]:
            if (at["contentType"] or "").endswith("pdf") and at["exists"]:
                rows.append({"itemID": r["itemID"], "year": r["year"],
                             "title": r["title"][:60], "path": at["abspath"]})
    if out(rows, a.json):
        return
    for x in rows:
        print(f"[{x['itemID']}] {x['year'] or '----'} {x['title']}\n    {x['path']}")
    print(f"\n총 {len(rows)}건")


# ─────────────────────────────────────────── main

def main():
    p = argparse.ArgumentParser(description="Zotero 로컬 라이브러리 조회 (읽기 전용)")
    p.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    p.add_argument("--json", action="store_true")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add(name, fn, *, coll=False, n=None, extra=None):
        s = sub.add_parser(name)
        s.set_defaults(fn=fn)
        if coll:
            s.add_argument("-c", "--collection", type=int, default=None)
        if n is not None:
            s.add_argument("-n", type=int, default=n)
        if extra:
            extra(s)
        return s

    add("stats", cmd_stats)
    add("collections", cmd_collections)
    add("list", cmd_list, coll=True, n=50)
    add("search", cmd_search, coll=True, n=30,
        extra=lambda s: s.add_argument("query"))
    add("show", cmd_show, extra=lambda s: s.add_argument("ident"))
    add("diag", cmd_diag, coll=True)
    add("orphans", cmd_orphans, n=300)
    add("dups", cmd_dups, coll=True)
    add("bib", cmd_bib, coll=True, extra=lambda s: s.add_argument("-o", "--out"))
    add("csv", cmd_csv, coll=True, extra=lambda s: s.add_argument("-o", "--out"))
    add("pdf", cmd_pdf, extra=lambda s: s.add_argument("ident"))
    add("pdfs", cmd_pdfs, coll=True)

    a = p.parse_args()
    if not hasattr(a, "collection"):
        a.collection = None
    db = open_db(a.data_dir)
    try:
        a.fn(db, a)
    finally:
        db.close()


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
