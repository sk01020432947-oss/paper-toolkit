#!/usr/bin/env python3
"""배포용 ZIP 만들기: git에 올라간 파일만, 한글 파일명은 NFC·UTF-8로(윈도우·맥에서 깨지지 않게).
사용: python3 tools/build/build-zip.py <출력.zip>"""
import os, subprocess, sys, unicodedata, zipfile

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
out = os.path.abspath(sys.argv[1])
files = subprocess.run(["git", "-c", "core.quotepath=false", "ls-files", "-z"], cwd=root, capture_output=True, check=True).stdout.decode().split("\0")
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for f in filter(None, files):
        z.write(os.path.join(root, f), "paper-toolkit/" + unicodedata.normalize("NFC", f))
print("%s (%d개 파일)" % (out, len([f for f in files if f])))
