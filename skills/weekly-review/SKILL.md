---
name: weekly-review
description: 한 주를 데이터 기반으로 회고한다. LLM 위키의 세션 로그·질의 결과·새 자료와 옵시디언 모선 볼트의 이번 주 노트를 모아, 7 재활용 축(설교·목회·논문·강의·저술·AI시스템·인문교양)별 진척과 이번 주의 원싱, 다음 주 우선순위를 정리한다. "주간 회고", "이번 주 회고", "한 주 정리", "이번 주 뭐 했지", "weekly review", "월간 회고", "분기 회고" 에서 발동. 기억이나 추측이 아니라 실제 파일 변경 기록만 근거로 삼는다.
---

# weekly-review — 데이터 기반 주간 회고

## 원칙

> [!important] 추측 금지
> **실제로 조회한 파일과 타임스탬프만 근거로 삼는다.** "아마 이것도 하셨을 것"은 쓰지 않는다.
> 데이터가 없는 영역은 **"기록 없음"** 이라고 분명히 적는다 — 그것 자체가 회고의 재료다.

기억은 서사로 남고 디테일은 사라진다. 이 스킬의 목적은 **사라진 디테일을 데이터에서 복원해 서사에 붙이는 것**이다.

---

## 1. 기간을 확정한다

```bash
date +"%Y-%m-%d %H:%M"          # 오늘
date -d "7 days ago" +"%Y-%m-%d"  # 주간 회고 기준일
```

사용자가 월간·분기라고 하면 범위를 그에 맞춘다. 기간을 **명시적으로 보고**하고 시작한다.

---

## 2. 근거를 모은다 (전부 조회할 것)

### 2-1. 세션 로그 — 무엇을 했는가

```
%USERPROFILE%/DEV/my-llm-wiki/30. Queries/session-log.md
```

기간 내 `## [YYYY-MM-DD HH:MM]` 엔트리를 읽는다. 각 엔트리의 **한 것 / 판단 / 남은 것**이 회고의 뼈대다.
특히 이전 엔트리의 **"남은 것"이 이번 주에 처리됐는지** 대조한다 — 약속 이행률이 나온다.

### 2-2. 볼트 변경 이력

```bash
cd "%USERPROFILE%/DEV/my-llm-wiki"
git log --since="7 days ago" --oneline
git diff --stat @{7.days.ago} 2>/dev/null | tail -5
```

git 이력이 없거나 커밋이 없으면 파일 수정 시각으로 대신한다:

```bash
find "30. Queries" "20. Wiki" -name "*.md" -newermt "7 days ago" 2>/dev/null
find "10. Raw Sources" -name "*.md" -newermt "7 days ago" 2>/dev/null | wc -l
```

### 2-3. 모선 볼트의 이번 주 작업

```bash
find "C:/obsidian(종합j/Obsidian 2025" -name "*.md" -newermt "7 days ago" 2>/dev/null | head -40
```

경로에서 축을 읽어낸다 — `1004. sermon/` → 설교축, `002. Folder/강의/` → 강의축 등.

### 2-4. 프로젝트 작업 홈

```bash
for d in "설교연구소" "WisdomPress" "PaperLab"; do
  echo "=== $d ==="
  find "%USERPROFILE%/$d" -name "*.md" -newermt "7 days ago" 2>/dev/null | head -10
done
```

---

## 3. 7 재활용 축으로 분류한다

축의 단일 진실 원천은 `%USERPROFILE%/DEV/my-llm-wiki/Core Context.md` §2 다. **먼저 읽고** 최신 축 정의를 쓴다.

| # | 축 | 신호가 되는 경로 |
|:-:|----|----------------|
| 1 | 설교 · 강해 | `설교연구소/설교원고` · `설교연구소/성경연구` · 모선 `1004. sermon/` |
| 2 | 목회 · 교회 | `설교연구소/교회AI가이드` · 교회연구소 관련 |
| 3 | 학술 · 논문 | `PaperLab/` |
| 4 | 강의 · 교육 | `WisdomPress/사회복지정책론` · `청소년이해론` · 모선 `강의/` |
| 5 | 저술 · 출판 | `WisdomPress/` 나머지 |
| 6 | AI 시스템 · 하네스 | `.claude/skills/` · `.cys/` · my-llm-wiki 자체 |
| 7 | 인문 · 교양 | 위키 `MOC-Literature and Humanities` · 고전 관련 |

---

## 4. 회고를 작성한다

```markdown
# 주간 회고 — YYYY-MM-DD ~ YYYY-MM-DD

## 이번 주의 원싱
(가장 의미 있었던 한 가지. 분량이 아니라 무게로 고른다)

## 축별 진척

| 축 | 움직임 | 근거 |
|----|--------|------|
| 1 설교·강해 | (한 줄) | 실제 파일 경로 |
| ... | ... | ... |

움직임이 없던 축은 **"기록 없음"** 으로 남긴다. 빈 축이 보이는 것이 이 표의 핵심이다.

## 지난주 "남은 것" 대조
- [x] 처리됨: ...
- [ ] 이월: ... (몇 주째 이월인지 표시)

## 관찰
(데이터에서 드러난 패턴. 예: 특정 축에 3주 연속 기록 없음, 인제스트만 늘고 Queries 적립은 정체 등)

## 다음 주 우선순위
1. (이월 항목 중 가장 오래된 것)
2. (기록 없는 축 중 지금 필요한 것)
3. ...
```

---

## 5. 저장한다

```
%USERPROFILE%/DEV/my-llm-wiki/30. Queries/YYYY-MM-DD-review-weekly.md
```

frontmatter 는 볼트 스키마를 따른다 — **YAML 은 공백 2칸, 본문은 TAB**:

```yaml
---
type: query-result
aliases:
  - 주간 회고 YYYY-MM-DD
description: Data-based weekly review covering the 7 reuse axes, drawn from session logs, vault changes, and mothership notes.
author:
  - Claude
date created: YYYY-MM-DD
date modified: YYYY-MM-DD
tags:
  - review
  - weekly
status: active
---
```

월간·분기 회고는 **주간 회고들을 재료로** 쌓는다 — 원자료를 다시 훑지 말고 이미 정리된 주간 회고를 읽는다. 연간 회고는 분기 회고 4개로 만든다. 이 계단 구조가 서사를 만든다.

---

## 하지 말 것

- **기억으로 채우지 않는다.** 조회되지 않은 것은 없었던 것으로 처리한다.
- **모든 축을 억지로 채우지 않는다.** 빈 축은 비워 두는 것이 정보다.
- **칭찬으로 때우지 않는다.** "수고하셨습니다"는 회고가 아니다. 이월된 것, 3주째 안 움직인 축을 그대로 적는다.
- 회고 결과 자체가 `30. Queries` 적립분이다. 저장하지 않으면 다음 달 회고가 다시 백지에서 시작한다.

---

## 자동화하고 싶다면

이 스킬은 **호출할 때만** 실행된다 — 매주 자동 실행은 토큰을 계속 소모하므로 기본값으로 두지 않았다.
정기 실행을 원하면 `/schedule` 로 등록한다 (예: 매주 일요일 밤). 등록 전에 토큰 비용을 감안할 것.
