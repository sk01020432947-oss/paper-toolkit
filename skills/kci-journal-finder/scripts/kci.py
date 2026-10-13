#!/usr/bin/env python3
"""KCI 등재지 2,888종 검색 (자료: nonwan-kci.netlify.app, 원출처 한국연구재단 KCI 학술지정보).

예)  kci.py -q 상담
     kci.py --mid 교육학 --grade 등재 --freq-min 4 --extra
     kci.py --mid 사회복지학 --grad          # 대학원생 감면 언급 학술지
     kci.py --free                            # 게재료·심사료 모두 무료
     kci.py --id 12292400                     # 상세
"""
import argparse, json, os, re, sys, time, urllib.request, urllib.parse

SITE = "https://nonwan-kci.netlify.app/"
HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, "..", "data", "kci.json")
COLS = ["id", "명", "영문명", "등급", "분야", "대분류", "중분류", "창간", "연간횟수", "발행", "언어", "발행기관", "소속대학", "발행주체", "kci_id", "kci_id2"]
EXTRA_KEYS = ["홈페이지", "투고시스템", "게재료", "심사료", "심사기간", "투고마감", "질적연구", "메모"]


def fetch():
    html = urllib.request.urlopen(SITE, timeout=30).read().decode("utf-8")
    out = {}
    for name in ("DATA", "EXTRA"):
        i = html.index("const %s = " % name) + len("const %s = " % name)
        out[name], _ = json.JSONDecoder().raw_decode(html[i:])
    out["fetched"] = time.strftime("%Y-%m-%d")
    return out


def load(refresh=False):
    stale = refresh or not os.path.exists(DATA_PATH) or time.time() - os.path.getmtime(DATA_PATH) > 30 * 86400
    if stale:
        try:
            d = fetch()
            os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
            tmp_path = DATA_PATH + ".tmp"  # 쓰다 끊겨도 깨진 파일이 남지 않게
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False)
            os.replace(tmp_path, DATA_PATH)
            return d
        except Exception as e:  # ponytail: 네트워크 실패 시 스냅샷 사용
            if not os.path.exists(DATA_PATH):
                sys.exit("다운로드 실패: %s" % e)
            print("경고: 갱신 실패, 저장본 사용 (%s)" % e, file=sys.stderr)
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def rows(d):
    ex = d["EXTRA"]
    for r in d["DATA"]:
        j = dict(zip(COLS, r))
        j["extra"] = ex.get(j["id"], {})
        yield j


def fee_text(j):
    e = j["extra"]
    return " ".join(e.get(k, "") for k in ("게재료", "심사료", "메모"))


def is_free(j):
    e = j["extra"]
    return all(re.search(r"없음|무료", e.get(k, "")) for k in ("게재료", "심사료"))


def match(j, a):
    if a.q and a.q not in (j["명"] + j["영문명"] + j["발행기관"]).lower(): return False
    if a.major and j["대분류"] != a.major: return False
    if a.mid and a.mid not in j["중분류"]: return False
    if a.grade and j["등급"] != a.grade: return False
    if a.freq_min and j["연간횟수"] < a.freq_min: return False
    if a.org and j["발행주체"] != a.org: return False
    if a.lang == "ko" and "한국어" not in j["언어"]: return False
    if a.lang == "en" and j["언어"] != "영어": return False
    if a.extra and not j["extra"]: return False
    if a.free and not is_free(j): return False
    if a.grad and not re.search(r"대학원|재학생|비전임|학생", fee_text(j)): return False
    return True


def site_url(a):
    p = {k: v for k, v in [("q", a.q), ("major", a.major), ("mid", a.mid), ("grade", a.grade),
                           ("freq", a.freq_min or ""), ("org", a.org), ("lang", a.lang),
                           ("extra", "1" if a.extra else ""), ("sort", a.sort if a.sort != "name" else "")] if v}
    return SITE + ("?" + urllib.parse.urlencode(p) if p else "")


def show(j, detail=False):
    e = j["extra"]
    tag = " [정보있음]" if e else ""
    print(f"{j['id']}  {j['명']}  ({j['발행기관']}, {j['등급']}, {j['발행']}, {j['중분류']}){tag}")
    if detail or e:
        for k in EXTRA_KEYS:
            if e.get(k): print(f"      {k}: {e[k]}")
    if detail:
        print(f"      영문명: {j['영문명']}  창간: {j['창간']}  언어: {j['언어']}  발행주체: {j['발행주체']}  KCI: https://www.kci.go.kr/kciportal/po/search/poSereArtiList.kci?sereId={j['kci_id']}")


def selftest():
    d = load()
    js = list(rows(d))
    assert len(js) == 2888 and len(d["EXTRA"]) >= 215
    free = [j["명"] for j in js if is_free(j)]
    assert {"특수교육연구", "고등교육", "장애와 고용"} <= set(free), free
    edu = [j for j in js if j["중분류"] == "교육학"]
    assert len(edu) == 197
    print("selftest ok:", len(js), "journals,", len(free), "free")


def main():
    for stream in (sys.stdout, sys.stderr):  # 윈도우 콘솔(cp949)에서 한글이 깨지지 않게
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-q", default="", help="이름·영문명·발행기관 검색")
    ap.add_argument("--major", default="", help="대분류: 사회과학 인문학 의약학 공학 예술체육학 복합학 자연과학 농수해양학")
    ap.add_argument("--mid", default="", help="중분류 (부분일치): 교육학 심리과학 사회복지학 행정학 간호학 체육 ...")
    ap.add_argument("--grade", default="", choices=["", "우수등재", "등재", "등재후보"])
    ap.add_argument("--freq-min", type=int, default=0, help="연 발행 횟수 이상")
    ap.add_argument("--org", default="", choices=["", "학회", "대학부설연구소", "일반기관"])
    ap.add_argument("--lang", default="", choices=["", "ko", "en"], help="ko=한국어 투고 가능, en=영어 전용")
    ap.add_argument("--extra", action="store_true", help="게재료·심사 정보 채워진 것만")
    ap.add_argument("--free", action="store_true", help="게재료·심사료 모두 무료")
    ap.add_argument("--grad", action="store_true", help="대학원생·비전임 감면 언급")
    ap.add_argument("--sort", default="name", choices=["name", "freq", "old", "new"])
    ap.add_argument("--limit", type=int, default=40)
    ap.add_argument("--id", help="학술지 id 상세")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--refresh", action="store_true", help="사이트에서 다시 내려받기")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest: return selftest()
    d = load(a.refresh)
    js = list(rows(d))
    if a.id:
        j = next((j for j in js if j["id"] == a.id), None)
        return show(j, True) if j else sys.exit("없음: " + a.id)
    a.q = a.q.lower()
    hit = [j for j in js if match(j, a)]
    key = {"name": lambda j: j["명"], "freq": lambda j: -j["연간횟수"], "old": lambda j: j["창간"], "new": lambda j: "" if not j["창간"] else "-" + j["창간"]}[a.sort]
    hit.sort(key=key, reverse=(a.sort == "new"))
    if a.json:
        return print(json.dumps(hit[:a.limit], ensure_ascii=False, indent=1))
    for j in hit[:a.limit]: show(j)
    print(f"\n{len(hit)}종 중 {min(len(hit), a.limit)}종 표시 (자료 {d.get('fetched', '스냅샷 2026-09')}). 규정은 바뀌므로 투고 전 학회 홈페이지 재확인.")
    print("사이트에서 보기:", site_url(a))


if __name__ == "__main__":
    main()
