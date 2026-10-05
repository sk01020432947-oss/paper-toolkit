---
name: reporting-guideline-router
description: "논문 투고 직전, reporting guideline(CONSORT·STROBE·PRISMA·SRQR·COREQ·TRIPOD+AI 등)을 '유명한 checklist 고르기'가 아니라 '연구 설계와 보고 항목의 대응 증명'으로 선택하게 하는 라우팅 스킬. 사용자가 \"reporting guideline 골라줘\", \"어떤 체크리스트 써야 해\", \"CONSORT/STROBE/PRISMA 맞나\", \"체크리스트 대응표\", \"보고 지침\", \"EQUATOR\", \"투고 전 checklist 점검\"을 언급하거나, 원고·연구 설계를 주며 투고용 guideline 판정을 요청할 때 발동한다. 역할 분리: paper-writing-order는 기획, paper-critical-review는 심사 시뮬레이션, ARS는 파이프라인 — 이 스킬은 '설계↔guideline 대응 증명과 router 표 작성' 전담이다."
---

# Reporting Guideline Router

## 핵심 원칙

**guideline을 하나만 검색해서 바로 고르지 않는다.** 좋은 선택은 유명한 checklist를 고르는 일이 아니라 연구 설계와 보고 항목의 대응을 증명하는 일이다. 사용자가 "왜 이 guideline인가"를 설명할 수 있게 되는 것이 산출물이다.

절대 하지 말 것: 원고를 보자마자 guideline 이름 하나를 답으로 던지기. 반드시 아래 3단계를 거친다.

## 3단계 게이트

### 1단계 — 연구 설계·산출물 분류
원고(또는 설계 설명)에서 다음을 먼저 표로 확정한다:
- 설계 유형: 실험(RCT/준실험) / 관찰(코호트·환자대조·단면·2차자료) / 질적 / 혼합 / 리뷰(체계적·스코핑) / 모형 개발·검증 / 증례 / QI / 프로토콜
- 주요 산출물: 효과 추정치, 연관성, 주제 분석, 예측모형 성능, 통합 근거 등
- 데이터·분석의 특이점: AI/ML 사용 여부(→ -AI 확장판 후보), 2차자료, 다국면 설계

설계가 모호하면 사용자에게 물어서 확정한 뒤 진행한다. 분류 없이 2단계로 가지 않는다.

### 2단계 — 후보 guideline 적용 범위(scope) 비교
후보를 **최소 2개** 올리고, 각 guideline이 명시한 scope와 1단계 분류를 대조한다. 카탈로그(아래)로 후보를 좁히되, 판정 근거는 guideline 원문 scope 문구다(필요 시 WebFetch로 equator-network.org 확인).

### 3단계 — Router 표 (6열)
선택된 후보에 대해 필수 항목 전수를 다음 6열로 매핑한다:

| study design | scope | required item | manuscript location | missing evidence | not-applicable reason |
|---|---|---|---|---|---|

- **manuscript location**: 원고의 절·문단 번호까지 특정. "어딘가 있음"은 무효.
- **missing evidence**: 그대로 수정 작업 목록이 된다 — 표 완성 후 우선순위를 매겨 제시.
- **not-applicable reason**: 빈칸 금지. N/A면 이유를 반드시 기록(심사자 대응 근거).

표가 완성되면 판정한다:
- **대응 증명됨** — scope 일치 + evidence 연결 완료 → checklist를 투고 패키지에 포함하라고 안내
- **근거 부족** — scope는 맞으나 missing evidence 존재 → missing 열을 작업 목록으로 전환
- **선택 무효** — 대응을 설명 못함 → 1단계로 회귀

## 설계별 카탈로그 (후보 좁히기용, 2026 기준)

| 설계 | Guideline | 비고 |
|---|---|---|
| RCT | CONSORT 2025 | AI 개입 시 CONSORT-AI |
| 관찰연구 | STROBE | 설문·2차자료 등 사회과학 관찰설계 준용 가능 |
| 체계적 문헌고찰 | PRISMA 2020 | 스코핑 리뷰는 PRISMA-ScR |
| 질적 연구 | SRQR / COREQ | COREQ는 인터뷰·FGI 특화 |
| 혼합방법 | GRAMMS | 통합 정당화가 핵심 |
| 예측모형 | TRIPOD+AI (2024) | ML 포함 |
| 진단 정확도 | STARD 2015 | |
| 증례 보고 | CARE | |
| 경제성 평가 | CHEERS 2022 | |
| QI 연구 | SQUIRE 2.0 | |
| 프로토콜 | SPIRIT / PRISMA-P | |

## 한국 사회과학·교육학 맥락 (이 사용자의 주 투고처)

- KCI 저널 다수는 guideline 제출 의무가 없다. 그래도 방법 절 투명성 기준으로 자체 적용을 권하고, "심사 지적 선제 차단 + 국제 저널 전환 시 재사용"을 근거로 설명한다.
- 담론분석·법제 비교·정책 문서 분석처럼 맞는 guideline이 없는 설계는 억지로 끼워 맞추지 않는다. "해당 설계용 guideline 부재를 확인함"이라는 기록 자체가 reporting plan이다. STROBE 등을 '참고 구조'로만 부분 차용할 수는 있으나 checklist 준수를 주장하지 않게 한다.

## 참고

- 정본 안내서: `~/Documents/reporting-guideline-router.html`
- EQUATOR Network: https://www.equator-network.org/reporting-guidelines/
