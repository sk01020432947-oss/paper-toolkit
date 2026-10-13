#!/usr/bin/env python3
"""ptk — paper-toolkit 공용 도우미 (표준 라이브러리만, 맥·윈도우·리눅스 공통).

  ptk.py doctor [--json]          설치·의존성 점검표
  ptk.py config show              설정 보기
  ptk.py config set KEY VALUE     설정 쓰기 (paper_dir, wiki_dir, notes_dirs, zotero_dir, field)
  ptk.py wiki-init [DIR]          논문 위키 폴더 뼈대 만들기 (index.md, papers/, concepts/, inbox/)
  ptk.py recall 단어 [단어...]     위키·노트 폴더에서 관련 노트 찾기
  ptk.py week [--days 7]          최근 N일 동안 바뀐 연구 파일과 Zotero 추가분
  ptk.py install [--force]        (플러그인을 못 쓸 때) 스킬·에이전트를 ~/.claude 에 복사
  ptk.py selftest                 자체 점검

설정 파일: ~/.config/paper-toolkit/config.json
"""
import argparse, json, os, re, shutil, sqlite3, subprocess, sys, time, unicodedata

HOME = os.path.expanduser("~")
CONFIG_PATH = os.environ.get("PAPER_TOOLKIT_CONFIG") or os.path.join(HOME, ".config", "paper-toolkit", "config.json")
CLAUDE_DIR = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(HOME, ".claude")
HERE = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.normpath(os.path.join(HERE, "..", ".."))  # .../skills
DEFAULTS = {"paper_dir": "", "wiki_dir": "", "notes_dirs": [], "zotero_dir": os.path.join(HOME, "Zotero"), "field": ""}
LIST_KEYS = {"notes_dirs"}
RESEARCH_EXT = {".md", ".docx", ".hwpx", ".hwp", ".pdf", ".tex", ".bib", ".csv", ".xlsx", ".txt"}
BUNDLE = ["humanize", "humanize-korean", "humanize-redo", "hwpx-mouseco", "kci-journal-finder", "keris-academic-search",
          "korean-character-count", "korean-law-search", "korean-spell-check", "notebooklm", "paper-critical-review", "paper-start",
          "paper-study", "paper-writing-order", "read-hwp", "ref-toolkit", "reporting-guideline-router", "toego-korean",
          "weekly-review", "wiki-recall", "zotero"]
SKIP_DIRS = {".git", ".obsidian", "node_modules", ".trash", "__pycache__", ".qmd"}


def nfc(s):
    return unicodedata.normalize("NFC", s)  # 맥은 한글 파일명을 자소 분리(NFD)로 저장한다


def top_roots(dirs):
    """다른 폴더의 하위 폴더는 뺀다(같은 파일을 두 번 세지 않게)."""
    real = [os.path.realpath(d) for d in dirs]
    return [d for d, r in zip(dirs, real) if not any(r != o and r.startswith(o + os.sep) for o in real)]


def expand(p):
    return os.path.abspath(os.path.expanduser(p)) if p else ""


def load_config():
    cfg = dict(DEFAULTS)
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, encoding="utf-8") as f:
            cfg.update(json.load(f))
    return cfg


def save_config(cfg):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def config_set(key, value):
    if key not in DEFAULTS:
        sys.exit("모르는 설정: %s (쓸 수 있는 것: %s)" % (key, ", ".join(DEFAULTS)))
    cfg = load_config()
    if key in LIST_KEYS:
        cfg[key] = [expand(v.strip()) for v in value.split(",") if v.strip()]
    elif key.endswith("_dir"):
        cfg[key] = expand(value)
    else:
        cfg[key] = value
    save_config(cfg)
    return cfg


def search_dirs(cfg):
    dirs = [cfg.get("wiki_dir")] + list(cfg.get("notes_dirs") or [])
    return [d for d in dirs if d and os.path.isdir(d)]


def walk(root, exts):
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in files:
            if os.path.splitext(fn)[1].lower() in exts:
                yield os.path.join(base, fn)


# ---------- wiki-init ----------
INDEX_MD = """# 논문 위키

읽은 논문과 개념을 쌓아 두는 곳. `/paper-study`가 여기에 노트를 만든다.

## 논문
(아직 없음 — `inbox/`에 PDF를 넣고 "/paper-study 이 논문 같이 공부하자"로 시작)

## 개념
(아직 없음)

## 읽을 것
(찾아봤지만 아직 노트가 없는 주제를 여기에 적는다)
"""


def wiki_init(path):
    path = expand(path)
    for d in ("papers", "concepts", "inbox"):
        os.makedirs(os.path.join(path, d), exist_ok=True)
    idx = os.path.join(path, "index.md")
    if not os.path.exists(idx):
        with open(idx, "w", encoding="utf-8") as f:
            f.write(INDEX_MD)
    return path


# ---------- recall ----------
def recall(words, dirs, limit=15):
    # ponytail: 매번 전체 .md를 읽는 선형 검색. 노트가 수만 건이면 qmd 같은 색인 도구로 바꿀 것.
    words = [nfc(w).lower() for w in words if w.strip()]
    hits = []
    for root in dirs:
        for path in walk(root, {".md"}):
            try:
                if os.path.getsize(path) > 2_000_000:
                    continue
                with open(path, encoding="utf-8", errors="ignore") as f:
                    text = nfc(f.read())
            except OSError:
                continue
            low, name = text.lower(), nfc(os.path.basename(path)).lower()
            matched = [w for w in words if w in low or w in name]
            if not matched:
                continue
            score = sum(low.count(w) for w in words) + 5 * sum(w in name for w in words) + 20 * len(matched)
            title = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), nfc(os.path.splitext(os.path.basename(path))[0]))
            lines = [l.strip()[:160] for l in text.splitlines() if any(w in l.lower() for w in words) and not l.startswith("#")][:2]
            hits.append((score, len(matched), path, title, lines))
    hits.sort(key=lambda h: (-h[1], -h[0]))
    return hits[:limit]


# ---------- week ----------
def changed_files(dirs, days):
    cutoff = time.time() - days * 86400
    out = {}
    for root in dirs:
        rows = []
        for path in walk(root, RESEARCH_EXT):
            try:
                m = os.path.getmtime(path)
            except OSError:
                continue
            if m >= cutoff:
                rows.append((m, path))
        out[root] = sorted(rows, reverse=True)
    return out


def zotero_db(zdir):
    db = os.path.join(zdir or "", "zotero.sqlite")
    if not os.path.exists(db):
        return None
    uri = "file:" + db.replace("\\", "/").replace("?", "%3f").replace("#", "%23") + "?mode=ro&immutable=1"
    return sqlite3.connect(uri, uri=True)


def zotero_recent(zdir, days):
    con = zotero_db(zdir)
    if not con:
        return None
    since = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(time.time() - days * 86400))
    try:
        return con.execute(
            """SELECT substr(i.dateAdded,1,10), COALESCE(v.value,'(제목 없음)')
               FROM items i JOIN itemTypes t ON t.itemTypeID=i.itemTypeID
               LEFT JOIN itemData d ON d.itemID=i.itemID AND d.fieldID=(SELECT fieldID FROM fields WHERE fieldName='title')
               LEFT JOIN itemDataValues v ON v.valueID=d.valueID
               WHERE i.dateAdded>=? AND t.typeName NOT IN ('attachment','note','annotation')
                 AND i.itemID NOT IN (SELECT itemID FROM deletedItems)
               ORDER BY i.dateAdded DESC""", (since,)).fetchall()
    finally:
        con.close()


# ---------- doctor ----------
def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20).stdout.strip()
    except Exception:
        return ""


def read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def has_mcp(name):
    data = read_json(os.path.join(HOME, ".claude.json")) or read_json(os.path.join(CLAUDE_DIR, ".claude.json"))
    servers = dict(data.get("mcpServers") or {})
    for proj in (data.get("projects") or {}).values():
        servers.update(proj.get("mcpServers") or {})
    return any(name in k for k in servers)


def has_plugin(name):
    data = read_json(os.path.join(CLAUDE_DIR, "plugins", "installed_plugins.json"))
    return any(name in k for k in (data.get("plugins") or data))


def riss_key():
    if os.environ.get("KSKILL_RISS_API_KEY") or os.environ.get("RISS_API_KEY"):
        return True
    try:
        with open(os.path.join(HOME, ".config", "k-skill", "secrets.env"), encoding="utf-8") as f:
            return bool(re.search(r"RISS_API_KEY\s*=\s*\S", f.read()))
    except OSError:
        return False


def doctor():
    cfg = load_config()
    rows = []  # (상태, 항목, 내용, 쓰는 곳, 해결)

    def add(ok, item, detail, used, fix=""):
        rows.append({"status": "ok" if ok else "todo", "item": item, "detail": detail, "used_by": used, "fix": "" if ok else fix})

    missing = [n for n in BUNDLE if not os.path.exists(os.path.join(SKILLS_DIR, n, "SKILL.md"))]
    add(not missing, "이 묶음의 스킬", "%d / %d개 (%s)%s" % (len(BUNDLE) - len(missing), len(BUNDLE), SKILLS_DIR, (" 없음: " + ", ".join(missing)) if missing else ""),
        "전체", "저장소를 다시 받아 설치")
    agents_ok = has_plugin("paper-toolkit") or os.path.exists(os.path.join(CLAUDE_DIR, "agents", "humanize-monolith.md"))
    add(agents_ok, "humanize 에이전트", "설치됨" if agents_ok else "없음", "humanize", "플러그인으로 설치하거나 install.sh / install.ps1 실행")
    add(sys.version_info >= (3, 8), "Python", sys.version.split()[0], "zotero, kci-journal-finder, keris, 맞춤법", "python.org에서 3.8 이상 설치")
    node = run(["node", "--version"]) if shutil.which("node") else ""
    add(bool(node), "Node.js", node or "없음", "글자수 세기, korean-law MCP, kordoc", "nodejs.org에서 LTS 설치")
    add(bool(shutil.which("git")), "git", "있음" if shutil.which("git") else "없음", "업데이트", "git-scm.com에서 설치")

    add(os.path.exists(CONFIG_PATH), "설정 파일", CONFIG_PATH if os.path.exists(CONFIG_PATH) else "없음", "paper-start, paper-study, wiki-recall, weekly-review", "Claude에게 \"/paper-start 처음 설정해줘\"")
    wd = cfg.get("wiki_dir")
    add(bool(wd) and os.path.isdir(wd), "논문 위키 폴더", wd or "미설정", "paper-study, wiki-recall", "Claude에게 \"/paper-start 처음 설정해줘\"")

    try:
        con = zotero_db(cfg.get("zotero_dir"))
        n = con.execute("SELECT count(*) FROM items").fetchone()[0] if con else None
    except sqlite3.Error:
        n = None
    add(n is not None, "Zotero 서재", ("%s (항목 %d)" % (cfg.get("zotero_dir"), n)) if n is not None else "%s 에 zotero.sqlite 없음" % cfg.get("zotero_dir"),
        "zotero", "zotero.org에서 설치. 데이터 폴더가 다르면: ptk.py config set zotero_dir <경로>")
    add(riss_key(), "RISS API 키", "설정됨" if riss_key() else "없음", "keris-academic-search",
        "riss.kr/apicenter 에서 발급(대학·비영리 기관) → 환경변수 KSKILL_RISS_API_KEY. 없어도 Claude가 웹 검색으로 대신할 수 있음")
    add(has_mcp("korean-law"), "korean-law MCP", "등록됨" if has_mcp("korean-law") else "없음", "korean-law-search",
        "open.law.go.kr 에서 키 발급 → claude mcp add korean-law -e LAW_OC=<키> -- npx -y --ignore-scripts --omit=optional korean-law-mcp@latest")
    add(bool(shutil.which("kordoc")) or bool(node), "kordoc (HWP 읽기)", "설치됨" if shutil.which("kordoc") else ("npx로 실행 가능" if node else "없음"), "read-hwp", "npm i -g kordoc")
    try:
        import lxml  # noqa: F401
        lx = True
    except ImportError:
        lx = False
    add(lx, "lxml (Python)", "있음" if lx else "없음", "hwpx-mouseco", "python3 -m pip install --user lxml (윈도우: python -m pip install lxml)")
    add(bool(shutil.which("pandoc")), "Pandoc", "있음" if shutil.which("pandoc") else "없음", "md → Word 변환", "pandoc.org 설치 (맥: brew install pandoc)")
    add(bool(shutil.which("notebooklm")), "notebooklm CLI", "있음" if shutil.which("notebooklm") else "없음", "notebooklm", "pip install notebooklm-py 후 notebooklm login")
    add(has_plugin("academic-research-skills"), "ARS 플러그인", "설치됨" if has_plugin("academic-research-skills") else "없음", "/ars-* 명령(개요·초안·인용검증·심사)",
        "claude plugin marketplace add Imbad0202/academic-research-skills && claude plugin install academic-research-skills@academic-research-skills")
    return rows


def print_doctor(rows):
    print("paper-toolkit 점검  (✅ 준비됨 / ➖ 선택 사항, 필요할 때 설치)\n")
    for r in rows:
        print("%s %-18s %s" % ("✅" if r["status"] == "ok" else "➖", r["item"], r["detail"]))
        if r["fix"]:
            print("      쓰는 곳: %s\n      해결: %s" % (r["used_by"], r["fix"]))
    ok = sum(r["status"] == "ok" for r in rows)
    print("\n준비됨 %d / %d. ➖ 항목은 해당 스킬을 쓸 때만 필요합니다." % (ok, len(rows)))


# ---------- install ----------
def install(force=False, dest=None):
    """저장소의 skills/*, agents/*.md 를 ~/.claude 로 복사. 이미 있으면 건너뛰고, --force면 기존 것을 백업 폴더로 옮긴 뒤 덮어쓴다."""
    dest = dest or CLAUDE_DIR
    repo = os.path.dirname(SKILLS_DIR)
    backup = os.path.join(dest, "backup-paper-toolkit-" + time.strftime("%Y%m%d-%H%M%S"))
    done, skipped = [], []
    jobs = [("skills", n) for n in sorted(os.listdir(SKILLS_DIR)) if os.path.exists(os.path.join(SKILLS_DIR, n, "SKILL.md"))]
    agents_dir = os.path.join(repo, "agents")
    if os.path.isdir(agents_dir):
        jobs += [("agents", n) for n in sorted(os.listdir(agents_dir)) if n.endswith(".md")]
    for kind, name in jobs:
        src, dst = os.path.join(repo, kind, name), os.path.join(dest, kind, name)
        if os.path.abspath(src) == os.path.abspath(dst):
            sys.exit("이미 %s 안에서 실행 중입니다. 내려받은 저장소 폴더에서 실행하세요." % dest)
        if os.path.lexists(dst):
            if not force:
                skipped.append("%s/%s" % (kind, name)); continue
            os.makedirs(os.path.join(backup, kind), exist_ok=True)
            shutil.move(dst, os.path.join(backup, kind, name))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.isdir(src):
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", ".DS_Store", "data"))
        else:
            shutil.copy2(src, dst)
        done.append("%s/%s" % (kind, name))
    return done, skipped, backup if os.path.isdir(backup) else None


# ---------- selftest ----------
def selftest():
    import tempfile
    global CONFIG_PATH
    tmp = tempfile.mkdtemp()
    CONFIG_PATH = os.path.join(tmp, "cfg", "config.json")
    wiki = wiki_init(os.path.join(tmp, "wiki"))
    assert os.path.isdir(os.path.join(wiki, "papers")) and os.path.exists(os.path.join(wiki, "index.md"))
    cfg = config_set("wiki_dir", wiki)
    cfg = config_set("notes_dirs", "%s, %s" % (tmp, wiki))
    assert load_config()["wiki_dir"] == wiki and len(cfg["notes_dirs"]) == 2
    with open(os.path.join(wiki, "papers", "2021-banks.md"), "w", encoding="utf-8") as f:
        f.write("# Banks 2021\n다문화교육과 인권교육의 통합을 다룬다.\n")
    with open(os.path.join(wiki, "concepts", "other.md"), "w", encoding="utf-8") as f:
        f.write("# 무관\n아무 내용\n")
    hits = recall(["다문화교육", "인권"], [wiki])
    assert len(hits) == 1 and hits[0][3] == "Banks 2021", hits
    assert recall(["없는단어xyz"], [wiki]) == []
    nfd = unicodedata.normalize("NFD", "사례관리")
    with open(os.path.join(wiki, "concepts", nfd + ".md"), "w", encoding="utf-8") as f:
        f.write(unicodedata.normalize("NFD", "장기요양 메모\n"))
    assert len(recall(["사례관리"], [wiki])) == 1 and len(recall(["장기요양"], [wiki])) == 1  # NFD 파일명·본문
    os.remove(os.path.join(wiki, "concepts", nfd + ".md"))
    assert top_roots([tmp, wiki]) == [tmp] and top_roots([wiki]) == [wiki]
    ch = changed_files([wiki], 1)
    assert len(ch[wiki]) == 3, ch  # index.md + 노트 2개
    old = os.path.join(wiki, "papers", "2021-banks.md")
    os.utime(old, (time.time() - 30 * 86400,) * 2)
    assert len(changed_files([wiki], 7)[wiki]) == 2
    assert zotero_recent(tmp, 7) is None
    assert isinstance(doctor(), list)
    done, skipped, backup = install(dest=os.path.join(tmp, "claude"))
    assert len(done) >= 20 and not skipped and backup is None, (done, skipped)
    assert os.path.exists(os.path.join(tmp, "claude", "skills", "paper-start", "scripts", "ptk.py"))
    done2, skipped2, _ = install(dest=os.path.join(tmp, "claude"))
    assert not done2 and len(skipped2) == len(done)
    done3, _, backup3 = install(force=True, dest=os.path.join(tmp, "claude"))
    assert len(done3) == len(done) and backup3 and os.path.isdir(os.path.join(backup3, "skills", "zotero"))
    shutil.rmtree(tmp)
    print("selftest OK")


def main():
    for stream in (sys.stdout, sys.stderr):  # 윈도우 콘솔(cp949)에서 한글·기호가 깨지지 않게
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="paper-toolkit 공용 도우미")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("doctor"); d.add_argument("--json", action="store_true")
    c = sub.add_parser("config"); c.add_argument("action", choices=["show", "set"]); c.add_argument("key", nargs="?"); c.add_argument("value", nargs="?")
    w = sub.add_parser("wiki-init"); w.add_argument("dir", nargs="?")
    r = sub.add_parser("recall"); r.add_argument("words", nargs="+"); r.add_argument("-n", type=int, default=15)
    k = sub.add_parser("week"); k.add_argument("--days", type=int, default=7)
    i = sub.add_parser("install"); i.add_argument("--force", action="store_true")
    sub.add_parser("selftest")
    a = ap.parse_args()

    if a.cmd == "selftest":
        return selftest()
    if a.cmd == "install":
        done, skipped, backup = install(a.force)
        for x in done:
            print("설치    " + x)
        for x in skipped:
            print("건너뜀  %s (이미 있음. 덮어쓰려면 --force)" % x)
        if backup:
            print("기존 것은 여기로 옮겼습니다: " + backup)
        print("\n완료: 설치 %d · 건너뜀 %d → %s\nClaude Code를 다시 시작한 뒤 /paper-start 를 입력하세요." % (len(done), len(skipped), CLAUDE_DIR))
        return
    cfg = load_config()
    if a.cmd == "doctor":
        rows = doctor()
        print(json.dumps(rows, ensure_ascii=False, indent=2)) if a.json else print_doctor(rows)
    elif a.cmd == "config":
        if a.action == "set":
            if not a.key or a.value is None:
                sys.exit("사용법: ptk.py config set KEY VALUE")
            cfg = config_set(a.key, a.value)
        print(json.dumps(cfg, ensure_ascii=False, indent=2))
        print("(설정 파일: %s%s)" % (CONFIG_PATH, "" if os.path.exists(CONFIG_PATH) else " — 아직 없음"))
    elif a.cmd == "wiki-init":
        target = a.dir or cfg.get("wiki_dir") or sys.exit("폴더를 지정하세요: ptk.py wiki-init <폴더>")
        path = wiki_init(target)
        config_set("wiki_dir", path)
        print("위키 폴더 준비됨: %s (설정 wiki_dir에 저장)" % path)
    elif a.cmd == "recall":
        dirs = top_roots(search_dirs(cfg))
        if not dirs:
            sys.exit("검색할 폴더가 없습니다. 먼저: ptk.py config set wiki_dir <폴더>  (또는 notes_dirs)")
        hits = recall(a.words, dirs, a.n)
        print("검색 폴더: %s\n검색어: %s\n" % (", ".join(dirs), " ".join(a.words)))
        if not hits:
            print("축적분 없음 — 이 주제의 노트를 찾지 못했습니다.")
        for score, nm, path, title, lines in hits:
            print("[%d/%d 단어] %s\n    %s" % (nm, len(a.words), title, path))
            for l in lines:
                print("    · " + l)
    elif a.cmd == "week":
        dirs = top_roots([d for d in dict.fromkeys([cfg.get("paper_dir")] + search_dirs(cfg)) if d and os.path.isdir(d)])
        print("기간: 최근 %d일 (%s 이후)\n" % (a.days, time.strftime("%Y-%m-%d", time.localtime(time.time() - a.days * 86400))))
        if not dirs:
            print("살펴볼 폴더가 없습니다. 먼저: ptk.py config set paper_dir <논문 폴더>")
        for root, rows in changed_files(dirs, a.days).items():
            print("## %s — %d개 변경" % (root, len(rows)))
            for m, path in rows[:60]:
                print("  %s  %s" % (time.strftime("%m-%d %H:%M", time.localtime(m)), nfc(os.path.relpath(path, root))))
            if len(rows) > 60:
                print("  … 외 %d개" % (len(rows) - 60))
        z = zotero_recent(cfg.get("zotero_dir"), a.days)
        print("\n## Zotero 새 문헌 — %s" % ("서재 없음" if z is None else "%d건" % len(z)))
        for date, title in (z or [])[:40]:
            print("  %s  %s" % (date, title))


if __name__ == "__main__":
    main()
