# 붙여넣기 설치문

아래 상자 안의 글을 **통째로 복사해서 Claude Code 대화창에 붙여 넣고 Enter**를 누르면 설치됩니다. 중간에 "이 명령을 실행해도 될까요?"라고 물으면 허용해 주세요.

## ① 인터넷으로 설치 (대부분 이것)

```text
논문 도구 묶음 paper-toolkit을 내 Claude Code에 설치해 줘.

저장소: https://github.com/sk01020432947-oss/paper-toolkit

1. 터미널에서 아래 두 명령을 차례로 실행해.
   claude plugin marketplace add sk01020432947-oss/paper-toolkit
   claude plugin install paper-toolkit@paper-toolkit
   이미 설치돼 있다고 나오면 대신 이 두 명령으로 최신판으로 올려 줘.
   claude plugin marketplace update paper-toolkit
   claude plugin update paper-toolkit@paper-toolkit
2. 1번이 실패하면 저장소를 내 홈 폴더의 paper-toolkit 폴더로 git clone 한 다음,
   그 폴더에서 python3 skills/paper-start/scripts/ptk.py install 을 실행해.
   (윈도우에서 python3가 없으면 python)
3. 설치가 끝나면 설치된 폴더에서 ptk.py 파일을 찾아
   python3 <경로>/ptk.py doctor 를 실행하고 결과를 표로 정리해 줘.
4. 내 기존 스킬과 설정은 지우거나 덮어쓰지 마.
   프로그램 설치나 API 키가 필요한 항목은 설치하지 말고 목록만 알려 줘.
5. 마지막에 무엇이 설치됐는지 요약하고,
   "Claude Code를 다시 시작한 뒤 /paper-start 를 입력하세요"라고 안내해 줘.
```

## ② ZIP 파일로 받았을 때

ZIP의 압축을 풉니다. 아래 글을 붙여 넣은 다음, **맨 끝에 푼 폴더의 경로를 덧붙이고** Enter를 누릅니다. 폴더를 대화창에 끌어다 놓으면 경로가 입력됩니다. 경로를 모르겠으면 "다운로드 폴더에 있어"처럼 말로 적어도 됩니다.

```text
논문 도구 묶음 paper-toolkit을 내 Claude Code에 설치해 줘.

1. 아래에 적은 폴더에서 AGENT-INSTALL.md를 찾아 읽고, 그 안의 "방법 B. 복사 설치"대로 설치해 줘.
   skills 폴더가 바로 보이지 않으면 한 겹 안쪽 폴더를 찾아봐.
2. 내 기존 스킬과 설정은 지우거나 덮어쓰지 마.
   프로그램 설치나 API 키가 필요한 항목은 설치하지 말고 목록만 알려 줘.
3. 설치가 끝나면 점검(ptk.py doctor)을 실행해서 결과를 표로 정리해 줘.
4. 마지막에 무엇이 설치됐는지 요약하고,
   "Claude Code를 다시 시작한 뒤 /paper-start 를 입력하세요"라고 안내해 줘.

압축을 푼 폴더:
```

설치가 끝나면 압축을 푼 폴더는 지워도 됩니다. 스킬은 내 컴퓨터의 Claude 폴더로 복사됩니다.

## 설치한 다음

1. Claude Code를 완전히 종료했다가 다시 엽니다.
2. `/paper-start`를 입력합니다. 논문 폴더와 위키 폴더를 한 번 정하고 나면, 지금 상황에 맞는 스킬을 알려 줍니다.
3. 사용 설명서는 [MANUAL.md](MANUAL.md)입니다.

## 직접 입력해서 설치하고 싶다면

Claude Code 대화창에 두 줄을 차례로 입력합니다.

```
/plugin marketplace add sk01020432947-oss/paper-toolkit
/plugin install paper-toolkit@paper-toolkit
```
