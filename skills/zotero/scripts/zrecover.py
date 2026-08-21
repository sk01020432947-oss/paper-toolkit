# -*- coding: utf-8 -*-
"""
zrecover.py — 서지정보 없는 독립 PDF의 메타데이터 복구 보조

Zotero 내장 'PDF 메타데이터 가져오기'가 실패한 파일(특히 한글 논문)을 대상으로
파일명을 정제해 Crossref·OpenAlex에 질의하고, 확신 매칭은 RIS로,
나머지는 검토용 작업목록으로 내보낸다.

사용법:
  python zrecover.py scan                     고아 PDF 목록 + 정제된 검색어
  python zrecover.py match [-n 40] [--min 0.72]   온라인 조회 후 매칭 결과
  python zrecover.py export -o 결과폴더        RIS + 작업목록 CSV 생성

주의: RIS를 Zotero로 가져오면 '새 항목'이 생긴다. 기존 PDF는 자동으로 붙지 않으므로
      가져온 항목 위로 해당 PDF를 끌어다 놓아야 한다. 작업목록 CSV에 파일 경로가 있다.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from difflib import SequenceMatcher

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from zotlib import open_db, q, _att, DEFAULT_DATA_DIR  # noqa: E402

MAILTO = os.environ.get("CROSSREF_MAILTO", "")  # Crossref polite pool용 — 본인 이메일을 환경변수로
UA = f"zrecover/1.0 (research reference recovery; mailto:{MAILTO})" if MAILTO else "zrecover/1.0 (research reference recovery)"

# 파일명에서 걷어낼 잡음
NOISE = [
    r"_?20\d{6}\d*",                 # 20240120095416 형태 타임스탬프
    r"\[[^\]]{1,24}\]",              # [RM 2023-18]
    r"\(\s*\d+\s*\)$",               # (1)
    r"\b(pdf|PDF)\b",
    r"[_\-]{2,}",
]


def clean_name(fn: str) -> str:
    s = os.path.splitext(fn)[0]
    for pat in NOISE:
        s = re.sub(pat, " ", s)
    s = s.replace("_", " ").replace(".", " ")
    s = re.sub(r"\s+", " ", s).strip(" -–—·")
    return s


def is_korean(s: str) -> bool:
    return bool(re.search(r"[가-힣]", s))


def norm(s: str) -> str:
    return re.sub(r"[^0-9a-z가-힣]", "", (s or "").lower())


def sim(a: str, b: str) -> float:
    return SequenceMatcher(None, norm(a), norm(b)).ratio()


def fetch(url: str, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


# ─────────────────────────────────────────── 외부 조회

def crossref(title: str, rows=3):
    url = ("https://api.crossref.org/works?"
           + urllib.parse.urlencode({"query.bibliographic": title, "rows": rows, "mailto": MAILTO}))
    try:
        items = fetch(url).get("message", {}).get("items", [])
    except Exception as e:
        return [], f"crossref: {e}"
    out = []
    for it in items:
        t = (it.get("title") or [""])[0]
        au = []
        for a in it.get("author", []) or []:
            fam, giv = a.get("family", ""), a.get("given", "")
            au.append(f"{fam}, {giv}".strip(", ") or a.get("name", ""))
        dp = it.get("issued", {}).get("date-parts", [[None]])[0]
        out.append({
            "src": "crossref", "title": t, "authors": au,
            "year": dp[0] if dp else None,
            "journal": (it.get("container-title") or [""])[0],
            "volume": it.get("volume", ""), "issue": it.get("issue", ""),
            "pages": it.get("page", ""), "doi": it.get("DOI", ""),
            "url": it.get("URL", ""), "type": it.get("type", ""),
            "publisher": it.get("publisher", ""),
        })
    return out, None


def kci(title: str, rows=3):
    """KCI Open API 제목 검색. 국내 학술지 전용 — 한글 논문 적중률의 핵심.

    활성 조건: 환경변수 KCI_API_KEY (없으면 조용히 건너뜀).
    엔드포인트는 KCI_API_URL 로 덮어쓸 수 있다.
    ※ 이 백엔드는 인증키 발급 전이라 실호출 검증이 되지 않았다.
      첫 사용 시 --probe 로 응답을 눈으로 확인할 것.
    """
    key = os.environ.get("KCI_API_KEY", "").strip()
    if not key:
        return [], None
    base = os.environ.get("KCI_API_URL", "https://open.kci.go.kr/po/openapi/openApiSearch.kci")
    url = base + "?" + urllib.parse.urlencode({
        "apiCode": "articleSearch", "key": key, "title": title, "displayCount": rows})
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=25) as r:
            raw = r.read().decode("utf-8", "replace")
    except Exception as e:
        return [], f"kci: {e}"
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(raw)
    except Exception as e:
        return [], f"kci-parse: {e}"

    def text(node, *names):
        for n in names:
            el = node.find(f".//{n}")
            if el is not None and (el.text or "").strip():
                return el.text.strip()
        return ""

    out = []
    for rec in root.iter():
        if rec.tag.lower() not in ("record", "item", "article"):
            continue
        t = text(rec, "article-title", "articleTitle", "title")
        if not t:
            continue
        authors = [a.text.strip() for a in rec.iter()
                   if a.tag.lower() in ("author-name", "authorname", "author") and (a.text or "").strip()]
        out.append({
            "src": "kci", "title": t, "authors": authors,
            "year": (text(rec, "pub-year", "pubYear", "year") or "")[:4] or None,
            "journal": text(rec, "journal-name", "journalName", "journal"),
            "volume": text(rec, "volume"), "issue": text(rec, "issue"),
            "pages": text(rec, "pages", "page"), "doi": text(rec, "doi", "DOI"),
            "url": text(rec, "url", "articleUrl"), "type": "journal-article",
            "publisher": text(rec, "institution-name", "institutionName"),
        })
    return out[:rows], None


def openalex(title: str, rows=3):
    url = ("https://api.openalex.org/works?"
           + urllib.parse.urlencode({"search": title, "per-page": rows, "mailto": MAILTO}))
    try:
        items = fetch(url).get("results", [])
    except Exception as e:
        return [], f"openalex: {e}"
    out = []
    for it in items:
        loc = (it.get("primary_location") or {}).get("source") or {}
        bib = it.get("biblio") or {}
        out.append({
            "src": "openalex", "title": it.get("title") or "",
            "authors": [a.get("author", {}).get("display_name", "")
                        for a in (it.get("authorships") or [])],
            "year": it.get("publication_year"),
            "journal": loc.get("display_name", "") or "",
            "volume": bib.get("volume") or "", "issue": bib.get("issue") or "",
            "pages": "-".join(x for x in (bib.get("first_page"), bib.get("last_page")) if x),
            "doi": (it.get("doi") or "").replace("https://doi.org/", ""),
            "url": it.get("doi") or it.get("id") or "",
            "type": it.get("type") or "", "publisher": "",
        })
    return out, None


# ─────────────────────────────────────────── 데이터 수집

def orphan_list(data_dir):
    db = open_db(data_dir)
    try:
        rows = q(db, """SELECT ia.itemID, i.key, ia.path, ia.contentType ct, i.dateAdded
                        FROM itemAttachments ia JOIN items i ON i.itemID = ia.itemID
                        LEFT JOIN deletedItems d ON d.itemID = ia.itemID
                        WHERE ia.parentItemID IS NULL AND d.itemID IS NULL
                          AND ia.contentType = 'application/pdf'
                        ORDER BY i.dateAdded DESC""")
        out = []
        for r in rows:
            at = _att(r, data_dir)
            fn = os.path.basename(at["abspath"] or at["path"] or "")
            if not fn:
                continue
            out.append({"itemID": r["itemID"], "key": r["key"], "filename": fn,
                        "query": clean_name(fn), "path": at["abspath"],
                        "exists": at["exists"], "korean": is_korean(fn)})
        return out
    finally:
        db.close()


def backends(korean: bool):
    """한글 파일명이면 KCI를 먼저 조회한다."""
    return (kci, crossref, openalex) if korean else (crossref, openalex, kci)


def match_one(o, min_score):
    cands = []
    for fn in backends(o.get("korean")):
        res, err = fn(o["query"])
        if err:
            o.setdefault("errors", []).append(err)
        cands += res
        time.sleep(0.35)
    best, bs = None, 0.0
    for c in cands:
        s = sim(o["query"], c["title"])
        if s > bs:
            best, bs = c, s
    o["score"] = round(bs, 3)
    o["best"] = best
    o["verdict"] = ("확신" if bs >= 0.85 else "검토" if bs >= min_score else "수동")
    return o


# ─────────────────────────────────────────── RIS

RIS_TYPE = {"journal-article": "JOUR", "article": "JOUR", "book": "BOOK",
            "book-chapter": "CHAP", "proceedings-article": "CONF",
            "dissertation": "THES", "posted-content": "GEN", "report": "RPRT"}


def to_ris(o):
    b = o["best"]
    L = [f"TY  - {RIS_TYPE.get(b.get('type',''), 'JOUR')}"]
    L.append(f"TI  - {b['title']}")
    for a in b["authors"]:
        if a:
            L.append(f"AU  - {a}")
    if b.get("year"):
        L.append(f"PY  - {b['year']}")
    for tag, k in (("JO", "journal"), ("VL", "volume"), ("IS", "issue"),
                   ("DO", "doi"), ("UR", "url"), ("PB", "publisher")):
        if b.get(k):
            L.append(f"{tag}  - {b[k]}")
    if b.get("pages"):
        pp = str(b["pages"]).split("-")
        L.append(f"SP  - {pp[0]}")
        if len(pp) > 1:
            L.append(f"EP  - {pp[1]}")
    L.append(f"N1  - [복구] 원본파일: {o['filename']}")
    L.append("ER  - ")
    return "\n".join(L)


# ─────────────────────────────────────────── 명령

def cmd_scan(a):
    orphans = orphan_list(a.data_dir)
    kor = sum(1 for o in orphans if o["korean"])
    if a.json:
        print(json.dumps(orphans, ensure_ascii=False, indent=2))
        return
    print(f"서지정보 없는 PDF {len(orphans)}건  (한글 파일명 {kor} / 그 외 {len(orphans)-kor})\n")
    for i, o in enumerate(orphans[:a.n], 1):
        print(f"{i:>3}. [{o['itemID']}] {o['filename'][:70]}")
        print(f"      → 검색어: {o['query'][:70]}")
    if len(orphans) > a.n:
        print(f"\n... 외 {len(orphans)-a.n}건 (-n 으로 조절)")
    print("\n[참고] 먼저 Zotero 내장 '메타데이터 가져오기'를 돌려 처리 가능한 건을 걷어낸 뒤")
    print("       남은 것에 match 를 쓰는 편이 정확하고 빠릅니다.")


def cmd_match(a):
    orphans = orphan_list(a.data_dir)[:a.n]
    print(f"{len(orphans)}건 온라인 조회 시작 (Crossref + OpenAlex)\n", file=sys.stderr)
    done = []
    for i, o in enumerate(orphans, 1):
        match_one(o, a.min)
        done.append(o)
        print(f"  {i}/{len(orphans)} {o['verdict']} {o['score']:.2f}  {o['filename'][:52]}",
              file=sys.stderr)
    if a.json:
        print(json.dumps(done, ensure_ascii=False, indent=2))
        return
    tally = {}
    for o in done:
        tally[o["verdict"]] = tally.get(o["verdict"], 0) + 1
    print("\n=== 매칭 결과 ===")
    for k in ("확신", "검토", "수동"):
        print(f"  {k}: {tally.get(k,0)}건")
    print()
    for o in done:
        if o["verdict"] == "수동":
            continue
        b = o["best"]
        print(f"[{o['verdict']} {o['score']:.2f}] {o['filename'][:64]}")
        print(f"    → {b['title'][:78]}")
        print(f"      {', '.join(b['authors'][:3])} ({b.get('year')}) {b.get('journal','')[:40]}")
        if b.get("doi"):
            print(f"      doi:{b['doi']}")
        print()


def cmd_export(a):
    outdir = a.out or os.path.join(os.path.expanduser("~"), "Documents", "research", "recovery")
    os.makedirs(outdir, exist_ok=True)
    orphans = orphan_list(a.data_dir)[:a.n]
    print(f"{len(orphans)}건 조회 중...", file=sys.stderr)
    for i, o in enumerate(orphans, 1):
        match_one(o, a.min)
        if i % 10 == 0:
            print(f"  {i}/{len(orphans)}", file=sys.stderr)

    ris_items = [o for o in orphans if o["verdict"] == "확신"]
    ris_path = os.path.join(outdir, "recovered.ris")
    with open(ris_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(to_ris(o) for o in ris_items))

    csv_path = os.path.join(outdir, "worklist.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["판정", "점수", "itemID", "원본파일명", "제안 제목", "제안 저자",
                    "연도", "학술지", "DOI", "PDF경로"])
        for o in orphans:
            b = o.get("best") or {}
            w.writerow([o["verdict"], o.get("score", 0), o["itemID"], o["filename"],
                        b.get("title", ""), "; ".join(b.get("authors", []))[:120],
                        b.get("year", ""), b.get("journal", ""), b.get("doi", ""),
                        o["path"]])
    print(f"\n[OK] RIS  {len(ris_items)}건 → {ris_path}")
    print(f"[OK] 작업목록 {len(orphans)}건 → {csv_path}")
    print("\n다음 순서:")
    print("  1) Zotero → 파일 → 가져오기 → recovered.ris")
    print("  2) 가져온 항목 위로 worklist.csv의 PDF경로에 있는 파일을 끌어다 놓기")
    print("  3) '검토' 판정 건은 CSV에서 제안값을 확인하고 맞으면 수기 입력")


def main():
    p = argparse.ArgumentParser(description="Zotero 고아 PDF 메타데이터 복구")
    p.add_argument("--data-dir", default=DEFAULT_DATA_DIR)
    p.add_argument("--json", action="store_true")
    s = p.add_subparsers(dest="cmd", required=True)

    a1 = s.add_parser("scan"); a1.set_defaults(fn=cmd_scan); a1.add_argument("-n", type=int, default=40)
    a2 = s.add_parser("match"); a2.set_defaults(fn=cmd_match)
    a2.add_argument("-n", type=int, default=40); a2.add_argument("--min", type=float, default=0.72)
    a3 = s.add_parser("export"); a3.set_defaults(fn=cmd_export)
    a3.add_argument("-n", type=int, default=300); a3.add_argument("--min", type=float, default=0.72)
    a3.add_argument("-o", "--out")

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
