# OmniLNP 시연 튜토리얼 (Step-by-Step)

> **총 소요시간:** 15–20분 (5개 시나리오)
> **사전 준비:** 서버 실행 (`python manage.py runserver`), 브라우저에서 `http://127.0.0.1:8000/` 열기

---

## 사이드바 메뉴 구조 (참고)

화면 왼쪽에 항상 표시되는 사이드바 메뉴입니다. 각 시나리오에서 "사이드바에서 XXX 클릭"이라고 하면 여기를 말합니다.

```
OmniLNP
AI-Native Autonomous Lab

OVERVIEW
  └ Dashboard          ← 메인 화면

DATA
  ├ Lipid Explorer     ← Lipid 목록/검색
  ├ Formulations       ← 제형 목록 + Designer
  └ Experiments        ← 실험 결과

AI MODELS
  ├ Predict            ← AI 물성 예측
  ├ Generate           ← AI 구조 생성
  └ Optimize           ← 다목적 최적화

LAB
  ├ Equipment          ← 장비 모니터링
  └ Workflow           ← 파이프라인
```

---

## 시나리오 1: 로그인 → Dashboard 둘러보기 (3분)

### Step 1. 로그인

1. 브라우저에서 `http://127.0.0.1:8000/` 접속
2. 로그인 화면이 나타남 — 상단에 **"OmniLNP"** 로고와 **"Sign In"** 카드가 보임
3. **Username** 입력란에 사용자명 입력
4. **Password** 입력란에 비밀번호 입력
5. **`Sign In`** 버튼 클릭
6. → Dashboard 화면으로 자동 이동됨

> 로그인 후 오른쪽 상단에 사용자명과 역할(예: "Researcher")이 표시되는 것을 확인하세요.

---

### Step 2. Dashboard 상단 — 통계 카드 확인

로그인 직후 보이는 화면이 Dashboard입니다. 상단에 **5개 통계 카드**가 가로로 나열되어 있습니다.

왼쪽부터 순서대로 확인하세요:

| 카드 제목 | 무엇을 보여주나 |
|----------|---------------|
| **Total Records** | 19,797건 — 43개 논문에서 수집한 LNP 실험 결과 총 건수 |
| **Ionizable Lipids** | 13,339종 — 데이터베이스에 등록된 이온화 지질 종류 수 |
| **AI Models** | 등록된 AI 모델 수와 활성화된 모델 수 |
| **Equipment** | 연결된 장비 수와 현재 온라인 장비 수 |
| **Workflows** | 총 워크플로우 수와 현재 실행 중인 수 |

---

### Step 3. Dashboard 중단 — 파이프라인 개요

통계 카드 아래로 스크롤하면 **"Closed-loop Optimization Pipeline"** 섹션이 보입니다.

5단계 파이프라인이 화살표로 연결되어 있습니다:
```
AI Design → Synthesize → Formulate → Analyze → Learn
(Structure gen) (Liquid handler) (Microfluidic) (DLS + Plate) (Retrain AI)
```

> 이것이 OmniLNP의 핵심 — AI가 설계하고, 장비가 합성하고, 결과를 분석해서 AI가 다시 학습하는 자동화 루프입니다.

---

### Step 4. Dashboard 하단 — 위젯 확인

계속 아래로 스크롤하면 여러 위젯이 보입니다:

1. **Equipment Status** — 각 장비의 현재 상태 (Running/Idle/Maintenance 등). 오른쪽 **"View All"** 링크가 보이면 나중에 시나리오 5에서 자세히 봅니다.
2. **Workflow Runs** — 진행 중인 파이프라인 실행 상태
3. **Quick Actions** — 4개 바로가기 카드:
   - "Explore Lipids" → Lipid Explorer로 이동
   - "Design Formulation" → Formulation Designer로 이동
   - "Generate Structures" → AI Generate로 이동
   - "Optimize LNP" → AI Optimize로 이동
4. **Recent Data (LNPDB)** — 최근 실험 데이터 20건 미리보기 테이블

> 다음 단계로: 사이드바에서 **"Lipid Explorer"** 를 클릭하세요 (DATA 섹션 아래 첫 번째 메뉴).

---

## 시나리오 2: LNPDB 탐색 + Lipid 상세 분석 (4분)

### Step 5. Lipid Explorer — 전체 목록 확인

사이드바 **DATA** > **"Lipid Explorer"** 클릭 후 나타나는 화면입니다.

1. 페이지 상단에 **"Lipid Explorer"** 제목과 **"13,339 ionizable lipids"** 라고 총 개수가 표시됨
2. 아래에 테이블이 보임 — 컬럼: **Name | Head | MW | LogP | TPSA | HBD/HBA | Linker | SMILES**
3. 하단에 **"Page 1 of 267"** 같은 페이지네이션과 **Prev / Next** 버튼이 있음

> 50개씩 페이지가 나뉘어 있습니다. Next를 눌러 다음 페이지로 이동해 볼 수 있습니다.

---

### Step 6. Lipid Explorer — 검색해 보기

테이블 위에 검색/필터 영역이 있습니다.

1. **"Name or SMILES..."** 검색창에 `MC3` 입력
2. **`Filter`** 버튼 클릭
3. → MC3가 포함된 Lipid만 필터링되어 표시됨

추가 필터도 사용해 보세요:
- **Structure** 드롭다운: "All" → **"Ester"** 로 변경하면 에스테르 결합 Lipid만 표시
- **MW Min**: `500`, **MW Max**: `900` 입력 → 분자량 범위 필터
- **Sort** 드롭다운: **"MW Low-High"** 선택 → 분자량 오름차순 정렬

필터를 초기화하려면 **"Reset"** 링크를 클릭하세요.

---

### Step 7. Lipid 상세 페이지 진입

1. 테이블에서 아무 Lipid의 **이름(Name 컬럼)을 클릭** — 파란색 링크로 되어 있음
2. → 해당 Lipid의 상세 페이지(`/compounds/<id>/`)로 이동

---

### Step 8. Lipid 상세 — 구조 & 물성 확인

상세 페이지는 3개 영역으로 구성되어 있습니다.

**왼쪽 — 2D Structure 카드:**
- **"2D Structure"** 제목 아래 분자 구조 그림이 자동 렌더링됨
- 그 아래 SMILES 문자열 표시

**가운데/아래 — 물성 카드들:**

큰 카드 5개:
| 카드 | 의미 |
|------|------|
| **Molecular Weight** | 분자량 (Da) |
| **LogP** | 지용성 |
| **TPSA** | 극성 표면적 |
| **HBD / HBA** | 수소결합 공여체/수용체 수 |

작은 카드 6개: Rot. Bonds, Rings, Fsp3, Heavy Atoms, N Count, Molar Ref

**Structural Components** 카드에서 Head Group, Linker, Tail 1, Tail 2 정보 확인

---

### Step 9. Lipid 상세 — 레이더 차트 & 실험 결과

**오른쪽 — Descriptor Profile:**
- **"Descriptor Profile"** 카드에 11각형 레이더 차트가 표시됨
- 파란선 = 이 Lipid, 회색 영역 = LNPDB 전체 평균
- 어떤 물성이 평균보다 높고 낮은지 한눈에 비교 가능

**아래로 스크롤:**
- **"Experiment Results"** 테이블 — 이 Lipid가 사용된 LNP 제형의 실험 결과
  - 컬럼: LNP ID | Formulation | Cargo | Model | Method | Value
- **"By Assay Method"** 차트 — 측정 방법별 분포
- **"Value Distribution"** 차트 — 결과값 히스토그램

> 상세 페이지 상단의 **"Back to Explorer"** 버튼을 클릭하면 목록으로 돌아갑니다.

---

### Step 10. Lipid 비교 (Compare)

1. Lipid Explorer 목록으로 돌아옴 (Step 9에서 "Back to Explorer" 클릭)
2. 브라우저 주소창에 직접 `http://127.0.0.1:8000/compounds/compare/` 입력하여 이동
3. **"Lipid Comparison"** 페이지가 나타남 — **"Compare up to 4 ionizable lipids side-by-side"**
4. 상단 검색창 **"Search lipid by name or SMILES..."** 에서 Lipid 이름 입력
5. 검색 결과에서 Lipid를 클릭하면 비교 목록에 추가됨 (최대 4개)
6. 추가된 Lipid마다:
   - 2D 구조가 나란히 표시됨
   - **"Descriptor Overlay"** 레이더 차트에 모든 Lipid가 겹쳐 표시됨
   - **"Property Comparison"** 테이블에서 수치 비교
7. Lipid를 제거하려면 이름 옆 **x** 버튼 클릭

> 다음 단계로: 사이드바에서 **"Formulations"** 를 클릭하세요 (DATA 섹션 두 번째 메뉴).

---

## 시나리오 3: LNP 제형 설계 + AI 예측 (4분)

### Step 11. Formulations 목록 확인 (빠르게)

사이드바 **DATA** > **"Formulations"** 클릭

1. **19,797건**의 LNP 제형 목록이 표시됨
2. 각 제형은 Ionizable Lipid + Helper Lipid + Cholesterol + PEG-Lipid 4성분 조합
3. 검색/필터 사용 가능

> 이 목록은 참고만 하고, 핵심 기능인 Designer로 이동합니다.

---

### Step 12. Formulation Designer 진입

1. Formulations 목록 페이지 상단 또는 Dashboard의 Quick Actions에서 **"Design Formulation"** 클릭
2. 또는 브라우저 주소창에 `http://127.0.0.1:8000/formulations/designer/` 입력
3. **"Formulation Designer"** 페이지가 열림 — **"Design LNP composition and predict efficacy"**

---

### Step 13. Designer — Ionizable Lipid 선택

좌측 패널 **"1. Ionizable Lipid"** 섹션:

1. 검색창 **"Search by name or SMILES (e.g. MC3, ALC-0315)..."** 에 `ALC` 입력
2. → 검색 결과 목록이 아래에 나타남
3. 원하는 Lipid를 **클릭**하여 선택

또는 검색창 아래 **"Most Studied"** 영역에서 자주 연구된 Lipid 8개 중 하나를 바로 클릭해도 됩니다.

> 선택한 Lipid가 파란색으로 하이라이트되면 성공입니다.

---

### Step 14. Designer — 4성분 조성 슬라이더 조절

**"2. Molar Composition"** 섹션에 4개 슬라이더가 있습니다.

각 슬라이더를 드래그하여 아래 값으로 맞춰보세요:

| 슬라이더 | 색상 | 추천 값 |
|---------|------|--------|
| **Ionizable Lipid** | 파랑 | **50** |
| **Helper Lipid** | 보라 | **10** |
| **Cholesterol** | 노랑 | **38.5** |
| **PEG-Lipid** | 청록 | **1.5** |

확인할 것:
- 슬라이더 위의 **색상 바**가 실시간으로 비율에 따라 변함
- 맨 아래 **Total Ratio** 가 **100.0**이 되면 초록색으로 표시됨
- 100이 아니면 빨간색 — 합이 100%가 되도록 조절하세요

각 성분 옆 **드롭다운**으로 구체적인 성분을 선택할 수 있습니다:
- Helper Lipid 드롭다운 → **DOPE** 또는 **DSPC** 선택
- Cholesterol 드롭다운 → **Cholesterol** 선택
- PEG-Lipid 드롭다운 → **DMG-PEG2000** 선택

---

### Step 15. Designer — 추가 파라미터 설정

슬라이더 아래에 추가 설정이 있습니다:

1. **N/P Ratio** 슬라이더 → **6** 으로 설정
2. **Mixing Method** 라디오 버튼 → **"Microfluidics"** 선택

---

### Step 16. Designer — 도넛 차트 확인

우측 패널 상단에 **"Composition"** 도넛 차트가 있습니다.

- 슬라이더를 움직일 때마다 도넛 차트가 **실시간으로** 변함
- 4가지 색상이 각 성분 비율을 나타냄
- 중앙에 선택된 Lipid 정보가 표시됨

---

### Step 17. Designer — AI 예측 실행

1. 우측 패널에 **"AI Prediction"** 카드가 보임 — 처음에는 "Select lipid and composition"이라는 안내 문구
2. 페이지 상단 오른쪽의 **`Run AI Prediction`** 버튼 클릭
3. → 예측 결과가 표시됨:

| 예측 항목 | 의미 |
|----------|------|
| **Efficacy** | 효능 점수 (원형 게이지) |
| **Stability** | 안정성 점수 |
| **Safety** | 안전성 점수 |
| **Confidence** | 예측 신뢰도 |
| **Diameter** | 입자 크기 (nm) |
| **PDI** | 다분산 지수 |
| **Zeta Potential** | 표면 전위 (mV) |
| **Encapsulation** | 봉입 효율 (%) |

---

### Step 18. Designer — 유사 제형 검색

좌측 하단 **"Similar Formulations in LNPDB"** 섹션:

1. **`Find Similar`** 버튼 클릭
2. → 현재 설정과 유사한 조성의 기존 제형이 DB에서 검색되어 표시됨
3. 각 유사 제형의 실험 결과 값과 비교 가능

> 다음 단계로: 사이드바에서 **AI MODELS** 섹션 > **"Generate"** 를 클릭하세요.

---

## 시나리오 4: AI 신규 구조 생성 + 최적화 (4분)

### Step 19. AI Structure Generation 진입

사이드바 **AI MODELS** > **"Generate"** 클릭

페이지 제목: **"AI Structure Generation"** — *"Generate novel ionizable lipid candidates with target properties"*

---

### Step 20. Generate — 타겟 물성 범위 설정

좌측 패널 **"Target Properties"** 섹션에 6개 입력란이 있습니다.

아래 값을 입력하세요:

| 입력란 | 값 |
|-------|-----|
| **MW Min** | `500` |
| **MW Max** | `900` |
| **LogP Min** | `8` |
| **LogP Max** | `15` |
| **TPSA Min** | `30` |
| **TPSA Max** | `80` |

**"Structural Constraints"** 섹션:
- **"Require ester bond"** 체크박스를 선택해 볼 수 있음 (선택사항)

**"Generation Settings"** 섹션:
- **Number of Candidates**: **`10`** 버튼 클릭 (기본 선택됨)

---

### Step 21. Generate — 후보 생성 실행

1. **`Generate Candidates`** 버튼 클릭
2. → 우측 패널 **"Generated Candidates"** 에 10개 후보가 생성됨

각 후보 카드에서 확인할 내용:
- **Pareto rank 뱃지**: `#1`, `#2`, `#3`... — 다목적 최적화 순위
- **SMILES**: 생성된 분자 구조식
- **Efficacy / Stability / Safety**: 3개 점수가 컬러 바로 표시됨
- **`Select`** 버튼: 이 후보를 선택

> Pareto rank #1이 효능·안정성·안전성을 종합적으로 가장 잘 균형 잡은 후보입니다.

---

### Step 22. Predict 페이지에서 생성된 후보 검증

1. Step 21에서 마음에 드는 후보의 SMILES를 복사 (클릭하여 선택 후 Ctrl+C / Cmd+C)
2. 사이드바 **AI MODELS** > **"Predict"** 클릭
3. **"AI Property Prediction"** 페이지가 열림

좌측 패널:
4. **"SMILES String"** 텍스트 영역에 복사한 SMILES를 **붙여넣기** (Ctrl+V / Cmd+V)
5. → 아래 **"Structure Preview"** 에 2D 분자 구조가 자동으로 그려짐
6. **`Run Prediction`** 버튼 클릭

우측 패널 **"Prediction Results"**:
7. 예측 결과 확인:
   - **Confidence Score** 게이지
   - 물성 카드: MW, LogP, TPSA, HBD, HBA, RotBonds, Rings, Heavy Atoms, Fsp3, MR, N Count

> "Or Select Known Lipid" 섹션에서 DB의 기존 Lipid를 검색하여 예측할 수도 있습니다.

---

### Step 23. Multi-Objective Optimization

1. 사이드바 **AI MODELS** > **"Optimize"** 클릭
2. **"Multi-Objective Optimization"** 페이지가 열림

**왼쪽 — 삼각 다이어그램 (Ternary Plot):**
3. **"Composition Space (IL-HL-Chol)"** 카드에 삼각형 차트가 표시됨
   - 꼭짓점 3개: **IL** (위), **HL** (왼쪽 아래), **Chol** (오른쪽 아래)
   - 각 점 = LNPDB의 실험 제형 하나
   - 점의 색상 = 실험 결과값 (높을수록 진한 색)
   - **"LNPDB Avg"** 마커 = 데이터베이스 평균 조성 위치
4. 점 위에 마우스를 올리면 해당 제형의 상세 정보가 툴팁으로 나타남

**왼쪽 아래 — Pareto Front 차트:**
5. **"Pareto Front"** 카드에서 효능 vs 안전성 트레이드오프 시각화
6. **"Efficacy vs Safety"** / **"Efficacy vs Stability"** 버튼으로 전환 가능

**오른쪽 — 최적화 설정:**
7. **Objective** 드롭다운: **"Balanced (Multi-Objective)"** 선택
8. **Algorithm** 드롭다운: **"Bayesian Optimization"** 선택
9. **Iterations** 입력란에 반복 횟수 입력
10. **Constraints** 섹션에서 IL/HL/Chol의 Min/Max 범위 설정
11. **`Run Optimization`** 버튼 클릭
12. → **"Optimization Progress"** 차트에 반복별 최적 점수 추이가 표시됨

> 다음 단계로: 사이드바에서 **LAB** 섹션 > **"Equipment"** 를 클릭하세요.

---

## 시나리오 5: 자율실험실 — 장비 + 워크플로우 (3분)

### Step 24. Equipment Monitor

사이드바 **LAB** > **"Equipment"** 클릭

페이지 제목: **"Equipment Monitor"** — 연결된 장비 수가 표시됨

**장비 카드 그리드 확인:**

각 장비 카드에서 확인할 항목:

| 위치 | 내용 |
|------|------|
| 카드 왼쪽 상단 | 상태 표시등 (초록=Running, 노랑=Maintenance, 빨강=Error, 회색=Offline) |
| 카드 제목 | 장비명 (예: Synthesis Reactor) + 타입 |
| 오른쪽 뱃지 | 통신 프로토콜 — **REST API** / **MQTT** / **OPC UA** |
| **Status** 줄 | 현재 상태 뱃지 (running, idle, maintenance, error, offline) |
| 상태 메시지 | 최근 로그 메시지 내용 |
| 카드 하단 | **"Connected"** 또는 **"Disconnected"** + 마지막 업데이트 시간 |

**장비 제어:**
- 각 카드를 확장하면 **"Send Command"** 입력란이 나타남
- 명령어 예시: `start`, `calibrate`, `measure` 등 입력 가능
- **`Send`** 버튼으로 장비에 명령 전송

**Status Timeline:**
- 페이지 하단에 **"Status Timeline"** 섹션 — 모든 장비의 상태 변경 이력이 시간순으로 표시됨

---

### Step 25. Workflow Pipeline

1. 사이드바 **LAB** > **"Workflow"** 클릭
2. **"Workflow Pipeline"** 페이지가 열림 — *"Closed-loop optimization: Design → Synthesize → Formulate → Analyze → Learn"*

**상단 통계 카드 3개:**

| 카드 | 의미 |
|------|------|
| **Total Runs** | 총 실행 횟수 (Optimization cycles) |
| **Active** | 현재 실행 중인 수 (Currently running) |
| **Completed** | 완료된 수 (Finished cycles) |

**워크플로우 런 카드:**

각 런 카드에서 확인할 항목:
- **런 이름** + **"Iteration X"** (반복 횟수)
- 상태 뱃지: completed / running / failed / queued
- **진행률 바**: X% 표시
- **5단계 파이프라인 표시**: 각 단계가 원으로 표시됨
  - ✓ = 완료, ▶ = 진행 중, 숫자 = 대기 중
  - 단계 이름: Design → Synthesize → Formulate → Analyze → Learn
  - 각 단계 아래에 담당 장비명이 표시됨

---

### Step 26. 새 워크플로우 생성

1. Workflow Pipeline 페이지에서 **`New Workflow`** 버튼 클릭
2. 아래 정보 입력:
   - **Name**: `LNP Optimization Demo`
   - **Description**: `시연용 최적화 사이클`
   - **AI Model**: 드롭다운에서 `LNP-Efficacy-RF` 선택
3. **`Create`** 버튼 클릭
4. → Workflow 상세 페이지로 자동 이동
5. Step 1 (Design)이 **"Awaiting Approval"** 상태로 표시됨

---

### Step 27. 5단계 파이프라인 실행 (핵심 시연)

각 단계마다 **Approve → Simulate** 2번 클릭으로 진행합니다.

**Step 1: AI Design**
1. Step 1 카드에서 **`Approve`** 버튼 클릭 → 상태가 "Running"으로 변경
2. **`Simulate`** 버튼 클릭 → 상태가 "Completed"로 변경
3. Output Data를 펼쳐 확인:
   - `top_candidate`: 선정된 이온화 지질 (이름, SMILES, 물성)
   - `candidates`: 8~15개 후보 리스트 (Pareto rank 포함)
   - `search_space`: 탐색 공간 통계 (MW 500-900 필터링)

**Step 2: Synthesize**
1. Step 2가 자동으로 "Awaiting Approval" 상태
2. **`Approve`** → **`Simulate`** 클릭
3. Output 확인:
   - `synthesis_conditions`: 온도, 반응시간, 용매, 촉매
   - `yield_pct` / `purity_pct`: 수율/순도
   - `qc`: MS, NMR, HPLC 확인 결과

**Step 3: Formulate**
1. **`Approve`** → **`Simulate`** 클릭
2. Output 확인:
   - `components`: IL:HL:Chol:PEG 4성분 조성 (mol%)
   - `composition_str`: 예) `50.2:9.8:38.4:1.6`
   - `np_ratio`: N/P 비율
   - DB에 실제 `LNPFormulation` 레코드가 생성됨

**Step 4: Analyze**
1. **`Approve`** → **`Simulate`** 클릭
2. Output 확인:
   - `measurements`: 입자 크기(nm), PDI, 제타 전위(mV), 캡슐화 효율(%)
   - `functional_assay`: luminescence 정규화 값
   - `db_benchmarks`: LNPDB 평균값 대비 비교
   - `qc_pass`: 품질 판정 (true/false)

**Step 5: Learn**
1. **`Approve`** → **`Simulate`** 클릭
2. Output 확인:
   - `performance`: AI 모델 R², RMSE (학습 전/후 비교)
   - `feature_importance`: 핵심 descriptor 기여도
   - `suggestions`: 다음 반복을 위한 구체적 권고사항
3. 모든 단계 완료 → 워크플로우 상태가 **"Completed"**로 변경

> 각 단계의 output이 다음 단계의 input으로 자동 전달되는 것을 **Input Data** 섹션에서 확인할 수 있습니다.

---

### Step 28. AI 보고서 생성

1. 워크플로우 상세 페이지 상단의 **`Generate AI Report`** 버튼 클릭
2. → 몇 초 후 AI가 전문 보고서를 생성
3. 보고서 내용 확인:
   - 이온화 지질 설계 및 선정 근거
   - FDA 승인 제형(Onpattro, Comirnaty, Spikevax) 대비 조성 비교
   - 물리화학적 특성 판정표 (입자 크기, PDI, 제타 전위, 캡슐화 효율)
   - 구조-활성 관계(SAR) 인사이트
   - 차기 반복 권고사항

> GROQ_API_KEY 환경변수가 설정되어 있어야 보고서 생성이 가능합니다.

---

### Step 29. Dashboard로 복귀

사이드바 **OVERVIEW** > **"Dashboard"** 클릭하여 메인 화면으로 돌아옵니다.

---

## 시연 마무리 요약 (1분)

Dashboard에서 전체 흐름을 한 문장씩 정리합니다:

| 방금 본 기능 | 핵심 |
|------------|------|
| **LNPDB** (시나리오 2) | 43개 논문, 19,797건 실험, 13,339종 Lipid 통합 데이터베이스 |
| **Formulation Designer** (시나리오 3) | 4성분 슬라이더로 제형 설계 + AI 실시간 물성 예측 |
| **AI Generate** (시나리오 4) | 타겟 조건에 맞는 신규 Lipid 구조를 AI가 자동 생성 |
| **Optimize** (시나리오 4) | 삼각 다이어그램 + Pareto front로 다목적 최적화 + 최적 조성 도출 |
| **Workflow** (시나리오 5) | 5단계 Closed-loop 파이프라인으로 자율 실험 수행 |
| **AI Report** (시나리오 5) | LNP 논문 수준의 전문 보고서 자동 생성 (FDA 벤치마크 포함) |

---

## 부록: 전체 페이지 경로 맵

| # | 사이드바 메뉴 | 경로 | 이동 방법 |
|---|-------------|------|----------|
| 1 | — | `/accounts/login/` | 브라우저에서 직접 접속 |
| 2 | Dashboard | `/` | OVERVIEW > Dashboard 클릭 |
| 3 | Lipid Explorer | `/compounds/` | DATA > Lipid Explorer 클릭 |
| 4 | (Lipid 상세) | `/compounds/<id>/` | Lipid Explorer에서 이름 클릭 |
| 5 | (Lipid 비교) | `/compounds/compare/` | 주소창에 직접 입력 |
| 6 | (Helper Lipids) | `/compounds/helpers/` | 주소창에 직접 입력 |
| 7 | Formulations | `/formulations/` | DATA > Formulations 클릭 |
| 8 | (Designer) | `/formulations/designer/` | Formulations 페이지 또는 Dashboard Quick Actions |
| 9 | Experiments | `/experiments/` | DATA > Experiments 클릭 |
| 10 | Predict | `/ai/predict/` | AI MODELS > Predict 클릭 |
| 11 | Generate | `/ai/generate/` | AI MODELS > Generate 클릭 |
| 12 | Optimize | `/ai/optimize/` | AI MODELS > Optimize 클릭 |
| 13 | Equipment | `/equipment/` | LAB > Equipment 클릭 |
| 14 | Workflow | `/workflow/` | LAB > Workflow 클릭 |
| 15 | (Workflow 상세) | `/workflow/<id>/` | Workflow 페이지에서 Details 클릭 |
