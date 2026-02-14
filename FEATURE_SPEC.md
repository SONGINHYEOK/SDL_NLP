# OmniLNP 플랫폼 기능설명서

> **문서 버전**: 1.0
> **최종 수정일**: 2026-02-13
> **대상**: SI 팀, 개발자, 과제 관리자

---

## 1. 플랫폼 개요

### 1.1 목적

OmniLNP는 LNP(Lipid Nanoparticle, 지질 나노입자) 기반 핵산 약물 전달 시스템의 개발을 가속화하기 위한 AI-Native 자율실험실 통합 플랫폼입니다.

**핵심 가치:**
- 19,797건의 LNP 실험 데이터(LNPDB)를 기반으로 한 데이터 기반 의사결정
- AI 모델을 통한 물성 예측, 구조 생성, 다목적 최적화
- 5단계 Closed-loop 파이프라인(Design→Synthesize→Formulate→Analyze→Learn)으로 자율 실험 수행
- 장비 모니터링 및 원격 제어 인터페이스

### 1.2 데이터 출처

| 항목 | 수치 |
|------|------|
| 원본 데이터 | LNPDB (Song, Baek & Seo, 2026, Scientific Data) |
| 실험 결과 | 19,797건 (43개 논문) |
| 이온화 지질 | 13,339종 (17개 분자 기술자) |
| Head Group | 771종 |
| Linker | 38종 |
| Tail | 374종 |
| Helper Lipid | 7종 (DOPE, DSPC, DOTAP 등) |
| Cholesterol | 16종 |
| PEG-Lipid | 15종 (DMG-PEG2000 등) |
| 실험 모델 | 43개 (in vitro/in vivo) |
| 측정 방법 | 10종 (luminescence, diameter, zeta 등) |

### 1.3 기술 스택

| 구분 | 기술 |
|------|------|
| 백엔드 | Django 5.x, Django REST Framework |
| 데이터베이스 | SQLite 3 (16MB, 사전 구축) |
| 프론트엔드 | Tailwind CSS (CDN), HTMX, Chart.js 4.x |
| 분자 시각화 | SmilesDrawer v2.1.7 |
| AI 보고서 | Groq API (Llama 3.3 70B) |
| 인증 | Django Session Auth (Role 기반) |
| 디자인 | Dark Theme (#0f1117 base), Plus Jakarta Sans + JetBrains Mono |

---

## 2. 사용자 인증

### 2.1 로그인 (`/accounts/login/`)

| 항목 | 설명 |
|------|------|
| 인증 방식 | Django 세션 기반 인증 |
| 사용자 모델 | Custom AbstractUser (accounts.User) |
| 역할(Role) | admin, researcher, operator, viewer |
| 추가 필드 | organization, bio |
| 미인증 접근 | 모든 페이지에서 `/accounts/login/`으로 리다이렉트 |

### 2.2 화면 구성

- 다크 테마 로그인 폼 (Username + Password)
- "OmniLNP" 로고 및 "AI-Native Autonomous Lab" 서브 타이틀
- 로그인 성공 시 Dashboard(`/`)로 이동
- 상단 우측에 사용자명 및 역할 표시

---

## 3. Dashboard (`/`)

### 3.1 기능 요약

메인 대시보드. 플랫폼 전체 현황을 한눈에 파악할 수 있는 통합 뷰.

### 3.2 화면 구성

#### 3.2.1 통계 카드 (상단, 5개)

| 카드 | 표시 데이터 | 데이터 소스 |
|------|-----------|-----------|
| Total Records | 실험 결과 총 건수 | `ExperimentResult.count()` |
| Ionizable Lipids | 이온화 지질 종류 수 | `IonizableLipid.count()` |
| AI Models | 등록/활성 모델 수 | `AIModel.count()` / `is_active=True` |
| Equipment | 전체/연결 장비 수 | `Equipment.count()` / `is_connected=True` |
| Workflows | 전체/실행중 워크플로우 수 | `WorkflowRun.count()` / `status=running` |

#### 3.2.2 Closed-loop Pipeline 시각화 (중단)

5단계 파이프라인 다이어그램:
```
AI Design → Synthesize → Formulate → Analyze → Learn
```
각 단계 아래에 담당 장비 및 역할 표시.

#### 3.2.3 하단 위젯

| 위젯 | 설명 |
|------|------|
| Equipment Status | 각 장비 현재 상태 (Running/Idle/Error 등) |
| Workflow Runs | 진행 중인 파이프라인 상태 |
| Quick Actions | 4개 바로가기 (Explore Lipids, Design Formulation, Generate Structures, Optimize LNP) |
| Recent Data | 최근 실험 데이터 20건 테이블 |

---

## 4. Lipid Explorer (`/compounds/`)

### 4.1 기능 요약

13,339종 이온화 지질 데이터베이스 탐색. 검색, 필터, 정렬, 페이지네이션 지원.

### 4.2 검색 및 필터

| 필터 항목 | 타입 | 설명 |
|----------|------|------|
| 검색 | 텍스트 | 이름 또는 SMILES 검색 |
| Structure | 드롭다운 | All / Ester / Carbonate / Disulfide |
| MW Min / Max | 숫자 | 분자량 범위 필터 |
| Sort | 드롭다운 | MW Low-High, MW High-Low, LogP, TPSA, Formulation Count |

### 4.3 데이터 테이블

| 컬럼 | 설명 |
|------|------|
| Name | 지질 이름 (클릭 시 상세 페이지 이동) |
| Head | Head Group 이름 |
| MW | 분자량 (Da) |
| LogP | 지용성 계수 |
| TPSA | 위상 극성 표면적 (A²) |
| HBD/HBA | 수소결합 공여체/수용체 수 |
| Linker | 링커 타입 태그 (Ester=green, Carbonate=blue, Disulfide=rose) |
| SMILES | 분자 구조식 (truncated) |

- 페이지당 50건, 총 267 페이지
- Reset 버튼으로 필터 초기화

---

## 5. Lipid Detail (`/compounds/<pk>/`)

### 5.1 기능 요약

개별 이온화 지질의 구조, 물성, 실험 결과를 종합적으로 분석하는 상세 페이지.

### 5.2 화면 구성

#### 5.2.1 2D Structure 카드

- SmilesDrawer 라이브러리로 SMILES → 2D 분자 구조 실시간 렌더링
- SMILES 문자열 표시

#### 5.2.2 물성 카드

**대형 카드 (4개):**
- Molecular Weight (Da)
- LogP
- TPSA (A²)
- HBD / HBA

**소형 카드 (6개):**
- Rotatable Bonds, Rings, Fsp3, Heavy Atoms, Nitrogen Count, Molar Refractivity

**Structural Components 카드:**
- Head Group, Linker, Tail 1~4

#### 5.2.3 Descriptor Profile (레이더 차트)

- 11축 레이더 차트 (Chart.js)
- 파란선: 현재 지질 값
- 회색 영역: LNPDB 전체 평균
- 축: MW, LogP, TPSA, HBD, HBA, RotBonds, Rings, Fsp3, MolarRef, HeavyAtoms, N_Count
- 0-1 정규화 (DB 전체 범위 기준)

#### 5.2.4 Experiment Results

- 이 지질이 사용된 LNP 제형의 실험 결과 테이블 (최대 50건)
- 컬럼: LNP ID, Formulation, Cargo, Model, Method, Value
- Assay Method별 분포 차트
- Value Distribution 히스토그램

---

## 6. Lipid Compare (`/compounds/compare/`)

### 6.1 기능 요약

최대 4개 이온화 지질을 병렬 비교하는 페이지.

### 6.2 주요 기능

| 기능 | 설명 |
|------|------|
| 지질 검색 추가 | 이름/SMILES 검색 → 클릭으로 비교 목록에 추가 (최대 4개) |
| 2D 구조 비교 | 선택된 지질의 2D 구조를 나란히 표시 |
| 레이더 차트 오버레이 | 모든 지질의 descriptor를 하나의 레이더 차트에 겹쳐 표시 |
| 속성 비교 테이블 | 17개 descriptor 수치 비교 |
| 지질 제거 | 이름 옆 x 버튼으로 비교 목록에서 제거 |

---

## 7. Formulations (`/formulations/`)

### 7.1 Formulation List

19,797건의 LNP 제형 목록 조회. 검색 및 mixing method 필터 지원.

| 필터 | 설명 |
|------|------|
| 검색 | Formulation ID, 지질 이름 |
| Mixing Method | Microfluidics / Handmixed |

### 7.2 Formulation Designer (`/formulations/designer/`)

#### 7.2.1 기능 요약

4성분 LNP 제형을 인터랙티브하게 설계하고 AI 물성 예측을 실행하는 핵심 기능.

#### 7.2.2 좌측 패널 — 제형 설계

**1단계: 이온화 지질 선택**
- 실시간 검색 API (`/formulations/api/search-lipids/?q=`)
- "Most Studied" 영역에서 상위 8개 지질 원클릭 선택
- 선택 시 파란색 하이라이트

**2단계: Molar Composition 슬라이더**

| 성분 | 색상 | 범위 | 기본값 |
|------|------|------|--------|
| Ionizable Lipid | 파랑 | 10-80 | 50 |
| Helper Lipid | 보라 | 0-50 | 10 |
| Cholesterol | 노랑 | 0-60 | 38.5 |
| PEG-Lipid | 청록 | 0-10 | 1.5 |

- 실시간 색상 바: 각 성분 비율에 따라 변화
- Total Ratio 검증: 합계 100.0 = 초록색, 아닌 경우 = 빨간색
- 각 성분 드롭다운: Helper Lipid(7종), Cholesterol(16종), PEG-Lipid(15종)

**3단계: 추가 파라미터**
- N/P Ratio 슬라이더 (1-20, 기본 6)
- Mixing Method 라디오: Microfluidics / Hand-mixed

#### 7.2.3 우측 패널 — 결과

**Composition 도넛 차트**
- 4성분 비율 실시간 업데이트

**AI Prediction 패널** (Run AI Prediction 버튼 클릭 시)

| 예측 항목 | 표시 형태 |
|----------|----------|
| Efficacy | 원형 게이지 (0-1) |
| Stability | 원형 게이지 |
| Safety | 원형 게이지 |
| Confidence | 신뢰도 수치 |
| Diameter | nm |
| PDI | 다분산 지수 |
| Zeta Potential | mV |
| Encapsulation | % |

**Similar Formulations** (Find Similar 버튼 클릭 시)
- DB에서 동일 지질의 유사 조성 제형 검색 (`/formulations/api/similar/`)
- 실험 결과 값과 비교 가능

---

## 8. Experiments (`/experiments/`)

### 8.1 기능 요약

19,797건 실험 결과 조회. 다중 필터 지원.

### 8.2 필터

| 필터 | 타입 | 옵션 |
|------|------|------|
| 검색 | 텍스트 | LNP ID, 지질 이름 |
| Method | 드롭다운 | 10종 (luminescence_normalized, diameter, zeta_potential 등) |
| Cargo | 드롭다운 | mRNA, siRNA, pDNA |
| Model | 드롭다운 | 실험 모델명 (HEK293T, HeLa 등) |

### 8.3 데이터 테이블

| 컬럼 | 설명 |
|------|------|
| LNP ID | 고유 식별자 |
| Lipid | 이온화 지질 이름 (상세 페이지 링크) |
| Cargo | mRNA=blue, siRNA=violet, pDNA=teal 태그 |
| Model | 실험 모델명 |
| Method | 측정 방법 |
| Value | 측정값 (색상 코딩: ≥1.0 green, ≥0.5 amber, <0.5 gray) |

---

## 9. AI Predict (`/ai/predict/`)

### 9.1 기능 요약

SMILES 문자열 또는 DB 지질을 선택하여 17개 분자 물성을 AI로 예측.

### 9.2 좌측 패널 — 입력

| 입력 방법 | 설명 |
|----------|------|
| SMILES 입력 | 텍스트 영역에 SMILES 문자열 직접 입력 |
| 구조 프리뷰 | SMILES 입력 시 2D 분자 구조 자동 렌더링 (SmilesDrawer) |
| DB 지질 검색 | "Or Select Known Lipid" 영역에서 DB 지질 검색/선택 |

### 9.3 우측 패널 — 결과

`Run Prediction` 버튼 클릭 시 표시:
- Confidence Score 게이지
- 물성 카드: MW, LogP, TPSA, HBD, HBA, Rotatable Bonds, Rings, Heavy Atoms, Fsp3, Molar Refractivity, Nitrogen Count

### 9.4 API

- `POST /ai/predict/api/`
- 입력: `{"smiles": "CCO..."}`
- 응답: 17개 descriptor 예측값 + confidence score
- 동작: DB에서 SMILES 매칭 → 없으면 유사 지질 평균값 반환

---

## 10. AI Generate (`/ai/generate/`)

### 10.1 기능 요약

타겟 물성 범위를 설정하여 신규 이온화 지질 후보를 AI로 생성.

### 10.2 좌측 패널 — 생성 조건

**Target Properties:**

| 입력 항목 | 설명 |
|----------|------|
| MW Min / Max | 분자량 범위 (예: 500-900) |
| LogP Min / Max | 지용성 범위 (예: 8-15) |
| TPSA Min / Max | 극성 표면적 범위 (예: 30-80) |

**Structural Constraints:**
- Require ester bond 체크박스

**Generation Settings:**
- Number of Candidates: 5 / 10 / 20

### 10.3 우측 패널 — 생성 결과

`Generate Candidates` 버튼 클릭 시 후보 카드 리스트 표시:

| 항목 | 설명 |
|------|------|
| Pareto Rank | #1, #2, #3... 다목적 최적화 순위 |
| SMILES | 생성된 분자 구조식 |
| Efficacy Score | 효능 점수 (컬러 바) |
| Stability Score | 안정성 점수 |
| Safety Score | 안전성 점수 |
| Select 버튼 | 후보 선택 |

---

## 11. AI Optimize (`/ai/optimize/`)

### 11.1 기능 요약

삼각 다이어그램과 Pareto front를 활용한 LNP 조성 다목적 최적화.

### 11.2 좌측 패널 (8 cols)

#### 11.2.1 Composition Space 삼각 다이어그램

- 3축: IL (상단), HL (좌하), Chol (우하)
- 각 점 = LNPDB의 실험 제형 하나 (최대 2,000개)
- 노란 마커: LNPDB 평균 조성 (IL:0.48, HL:0.20, Chol:0.32)
- 시안 마커: AI Optimal (최적화 실행 후 표시)
- PEG 고정값 입력 (기본 1.5 mol%)

#### 11.2.2 Pareto Front 차트

- X축: Efficacy, Y축: Safety 또는 Stability (토글 전환)
- 파란 점: 전체 제형, 노란 점+선: Pareto 최적 front
- Pareto front 위의 점 = 어떤 다른 점보다 모든 목적에서 우수한 해

### 11.3 우측 패널 (4 cols)

#### 11.3.1 최적화 설정

| 항목 | 옵션 |
|------|------|
| Objective | Maximize Efficacy / Maximize Safety / Balanced (Multi-Objective) |
| Algorithm | Bayesian Optimization / Genetic Algorithm (NSGA-II) / Random Search |
| Iterations | 10-500 (기본 50) |

#### 11.3.2 Constraints

| 성분 | Min | Max |
|------|-----|-----|
| IL | 20% | 70% |
| HL | 0% | 40% |
| Chol | 15% | 60% |

#### 11.3.3 Optimization Progress

`Run Optimization` 버튼 클릭 시:
- 반복별 Best Score 수렴 그래프 (line chart)
- 삼각 다이어그램에 "AI Optimal" 마커 추가

#### 11.3.4 Optimal Formulation 결과 카드

최적화 완료 시 표시:

| 섹션 | 내용 |
|------|------|
| Composition (mol%) | IL, HL, Chol, PEG 각각의 mol% + 비율 바 |
| 조성 문자열 | 예: `48.5 : 14.2 : 35.8 : 1.5` |
| Predicted Performance | Efficacy / Safety / Stability 점수 |
| Overall Score | 최적화 최종 점수 |

---

## 12. Equipment Monitor (`/equipment/`)

### 12.1 기능 요약

자율실험실 장비 5대의 상태 모니터링, 명령 전송, 이력 조회.

### 12.2 등록 장비

| 장비명 | 타입 | 프로토콜 | 역할 |
|--------|------|---------|------|
| Hamilton STAR | Liquid Handler | REST API | 합성 (Synthesize step) |
| NanoAssemblr Ignite | Microfluidic | REST API | 제형화 (Formulate step) |
| Zetasizer Ultra | DLS | Serial | 분석 (Analyze step) |
| Infinite M200 Pro | Plate Reader | REST API | 기능 분석 |
| Agilent 1260 Infinity | HPLC | OPC UA | 품질 관리 |

### 12.3 장비 카드

각 장비 카드에 표시되는 항목:

| 위치 | 내용 |
|------|------|
| 좌상단 | 상태 표시등 (Running=초록 pulse, Idle=초록, Maintenance=노랑, Error=빨강, Offline=회색) |
| 제목 | 장비명 + 타입 |
| 우측 뱃지 | 통신 프로토콜 (REST API / MQTT / OPC UA / Serial) |
| Status 줄 | 현재 상태 뱃지 |
| 메시지 | 최근 로그 메시지 |
| 하단 | Connected/Disconnected + 마지막 업데이트 시간 |

### 12.4 장비 제어

- 각 카드 확장 시 "Send Command" 입력란 표시
- 명령어 입력 (예: `start`, `calibrate`, `measure`) → `Send` 버튼
- API: `POST /api/equipment/devices/<pk>/command/`

### 12.5 Status Timeline

- 페이지 하단: 모든 장비의 상태 변경 이력 시간순 표시
- 장비명, 상태 변경, 메시지, 타임스탬프

### 12.6 REST API

| Endpoint | Method | 설명 |
|----------|--------|------|
| `/api/equipment/devices/` | GET | 전체 장비 목록 |
| `/api/equipment/devices/` | POST | 장비 등록 |
| `/api/equipment/devices/<pk>/` | GET/PUT/DELETE | 개별 장비 CRUD |
| `/api/equipment/devices/<pk>/command/` | POST | 명령 전송 |
| `/api/equipment/devices/<pk>/status/` | GET | 상태 이력 조회 |
| `/api/equipment/devices/<pk>/report_status/` | POST | 장비→플랫폼 상태 보고 |
| `/api/equipment/status/` | GET | 전체 상태 로그 |

---

## 13. Workflow Pipeline (`/workflow/`)

### 13.1 기능 요약

5단계 Closed-loop 최적화 파이프라인의 생성, 실행, 모니터링.

### 13.2 파이프라인 목록 화면

**상단 통계 카드 3개:**

| 카드 | 내용 |
|------|------|
| Total Runs | 총 워크플로우 실행 횟수 |
| Active | 현재 실행 중인 수 |
| Completed | 완료된 수 |

**워크플로우 카드:**
- 이름 + Iteration 번호 + 상태 뱃지
- 진행률 바 (X%)
- 5단계 파이프라인 시각화: Design → Synthesize → Formulate → Analyze → Learn
- 각 단계 상태: ✓ 완료, ▶ 진행중, 숫자 대기중
- "Details" 링크 → 상세 페이지

### 13.3 워크플로우 생성

`New Workflow` 버튼 → 생성 폼:

| 입력 | 설명 |
|------|------|
| Name | 워크플로우 이름 |
| Description | 설명 (선택) |
| AI Model | 사용할 AI 모델 선택 (드롭다운) |

생성 시 자동 동작:
- WorkflowRun 레코드 생성 (status=running)
- WorkflowStep 5개 생성 (design, synthesize, formulate, analyze, learn)
- Step 1(Design)을 awaiting_approval 상태로 설정
- 해당 step에 장비 자동 매핑 (synthesize→liquid_handler, formulate→microfluidic, analyze→dls)

---

## 14. Workflow Detail (`/workflow/<pk>/`)

### 14.1 기능 요약

개별 워크플로우 실행의 상세 뷰. 5단계 타임라인, 각 단계 입출력 데이터, 제어 버튼, AI 보고서.

### 14.2 상단 정보 카드

| 카드 | 내용 |
|------|------|
| Iteration | 현재 반복 차수 |
| Progress | 진행률 (%) |
| AI Model | 사용 중인 AI 모델명 |
| Created | 생성 시간 |

### 14.3 제어 버튼

| 버튼 | 조건 | 동작 |
|------|------|------|
| Pause | status=running | 실행 일시정지, running step → awaiting_approval |
| Resume | status=paused | 실행 재개 |
| Cancel | status≠completed,failed | 실행 취소, 미완료 step → skipped |

### 14.4 Step Timeline

각 단계(Step 1~5)에 표시되는 항목:

| 항목 | 설명 |
|------|------|
| 단계명 | Step N: Design/Synthesize/Formulate/Analyze/Learn |
| 상태 뱃지 | pending, awaiting_approval, running, completed, failed, skipped |
| 장비 | 연결된 장비명 (해당되는 경우) |
| 시작/완료 시간 | started_at, completed_at |
| Input Data | 이전 단계의 output이 자동 전달된 JSON (접기/펼치기) |
| Output Data | 이 단계의 실행 결과 JSON (접기/펼치기) |

### 14.5 단계별 제어

| 버튼 | 조건 | 동작 |
|------|------|------|
| Approve | status=awaiting_approval | 단계 승인 → running |
| Simulate | status=running | 단계 실행 (pipeline 엔진 호출) |
| Re-run | status=completed,failed | 단계 재실행 (output 초기화) |

### 14.6 파이프라인 실행 엔진 (`workflow/pipeline.py`)

각 단계의 simulate 실행 시 실제 DB 데이터를 활용한 의미있는 결과를 생성합니다.

#### Step 1: Design (AI 설계)

| 동작 | 설명 |
|------|------|
| 지질 필터링 | IonizableLipid에서 MW 500-900, 생분해성 링커(ester/disulfide) 우선 필터 |
| 후보 샘플링 | 8~15개 후보를 랜덤 샘플링 |
| Pareto rank | 각 후보에 efficacy, stability, safety 점수 부여 및 순위 매김 |
| DB 생성 | GeneratedCandidate x N개, Prediction x 1개 |
| Top 선정 | Pareto rank 1위를 selected 상태로 마킹 |

**Output 구조:**
```json
{
  "top_candidate": {
    "lipid_id": 8165,
    "name": "314-9",
    "smiles": "...",
    "mw": 742.5,
    "logp": 12.3,
    "efficacy_score": 0.87,
    "stability_score": 0.74,
    "safety_score": 0.82
  },
  "candidates": [...],
  "search_space": {"total_lipids": 7046, "filtered_pool": 5375, "sampled": 8}
}
```

#### Step 2: Synthesize (합성)

| 동작 | 설명 |
|------|------|
| 입력 | 이전 step의 `top_candidate.lipid_id`로 IonizableLipid 조회 |
| 합성 조건 산출 | MW, LogP 기반으로 온도, 시간, 용매, 촉매 결정 |
| 수율/순도 시뮬레이션 | MW에 반비례하는 수율 + noise |
| 장비 로그 | EquipmentStatus 2건 생성 (running → idle) |
| 상태 업데이트 | GeneratedCandidate.status → synthesized |

**Output 구조:**
```json
{
  "lipid_id": 8165,
  "batch_id": "BATCH-005-6300",
  "synthesis_conditions": {
    "temperature_c": 74.4,
    "reaction_time_h": 3.7,
    "solvent": "DCM / MeOH (3:1)",
    "catalyst": "HATU"
  },
  "yield_pct": 71.8,
  "purity_pct": 95.4,
  "qc": {"ms_confirmed": true, "nmr_purity": 94.2, "hplc_purity": 95.4}
}
```

#### Step 3: Formulate (제형화)

| 동작 | 설명 |
|------|------|
| 입력 | 이전 step의 `lipid_id` |
| 성분 선택 | DB에서 HelperLipid, Cholesterol, PEGLipid 랜덤 선택 |
| 몰비 생성 | DB 평균 기반 (IL:50, HL:10, Chol:38.5, PEG:1.5) ± perturbation, 합계 100 정규화 |
| DB 생성 | LNPFormulation 1건 (source="designed") |
| 장비 로그 | EquipmentStatus 2건 (microfluidic) |

**Output 구조:**
```json
{
  "formulation_pk": 19798,
  "formulation_id": "WF005-FCDC070",
  "components": {
    "ionizable_lipid": {"id": 8165, "name": "314-9", "ratio": 51.9},
    "helper_lipid": {"id": 3, "name": "MDOA", "ratio": 9.1},
    "cholesterol": {"id": 5, "name": "Stigmastanol", "ratio": 37.3},
    "peg_lipid": {"id": 8, "name": "DPG-PEG5000", "ratio": 1.7}
  },
  "composition_str": "51.9:9.1:37.3:1.7",
  "np_ratio": 5.0,
  "mixing_parameters": {"method": "microfluidics", "flow_rate_ml_min": 12.3, "tfr": 14.5, "frr": 3.2}
}
```

#### Step 4: Analyze (분석)

| 동작 | 설명 |
|------|------|
| 입력 | 이전 step의 `formulation_pk` |
| 실험 생성 | Experiment 1건 (HEK293T, in vitro, FLuc mRNA) |
| 측정 시뮬레이션 | diameter, zeta_potential, luminescence 값 생성 |
| DB 생성 | ExperimentResult 3건 (DLS, Zeta, Luminescence) |
| 벤치마크 | DB 기존 결과 평균과 비교 |
| 장비 로그 | EquipmentStatus 2건 (DLS) |
| QC 판정 | diameter<200 & PDI<0.3 & EE>80% |

**Output 구조:**
```json
{
  "experiment_id": "EXP-WF005-CF822F",
  "measurements": {
    "diameter_nm": 106.0,
    "pdi": 0.295,
    "zeta_potential_mV": -7.9,
    "encapsulation_efficiency_pct": 88.8
  },
  "functional_assay": {
    "luminescence_normalized": 0.973,
    "cell_line": "HEK293T",
    "cargo": "FLuc mRNA"
  },
  "db_benchmarks": {"diameter": 167.276, "zeta_potential": 2.234},
  "qc_pass": true
}
```

#### Step 5: Learn (학습)

| 동작 | 설명 |
|------|------|
| AI 모델 업데이트 | R² +0.005~0.02, RMSE -0.002~0.01 소폭 개선 |
| 학습 데이터 증가 | training_data_count +5~20 |
| Feature importance | 9개 descriptor별 기여도 생성 |
| 차기 권고 | 측정 결과 기반 개선 제안 생성 |

**권고 로직:**

| 조건 | 권고사항 |
|------|---------|
| PDI > 0.2 | PEG-lipid 몰비 0.3-0.5 증가 |
| Diameter > 120nm | 마이크로플루이딕 유속 증가 또는 IL 비율 감소 |
| Zeta > -10mV | N/P ratio 조정 |
| EE < 85% | N/P ratio 6-8로 최적화 |

**Output 구조:**
```json
{
  "ai_model": "LNP-Efficacy-RF",
  "performance": {
    "before": {"r2": 0.82, "rmse": 0.15},
    "after": {"r2": 0.832, "rmse": 0.1446},
    "training_data_count": 515
  },
  "feature_importance": {"molecular_weight": 0.15, "logp": 0.18, ...},
  "suggestions": ["Increase PEG-lipid molar ratio by 0.3-0.5 to reduce PDI"]
}
```

### 14.7 데이터 흐름 (Step 체이닝)

```
Design.output → Synthesize.input  (top_candidate.lipid_id)
    ↓
Synthesize.output → Formulate.input  (lipid_id)
    ↓
Formulate.output → Analyze.input  (formulation_pk)
    ↓
Analyze.output → Learn.input  (measurements, qc_pass)
```

각 step의 Input Data 섹션에서 이전 step output이 자동 전달된 것을 확인할 수 있습니다.

### 14.8 에러 처리

- step 실행 중 예외 발생 시: step.status → FAILED, 로그 기록
- FAILED 상태에서 Re-run 버튼으로 재실행 가능
- 전체 run 취소 시 미완료 step → SKIPPED

---

## 15. AI 보고서 생성

### 15.1 기능 요약

완료된 워크플로우에 대해 LNP 최적화 논문 수준의 전문 보고서를 AI(Groq API)로 자동 생성.

### 15.2 실행

- Workflow Detail 페이지에서 `Generate AI Report` 버튼 클릭
- API: `POST /assistant/api/report/<pk>/`
- 외부 API: Groq (Llama 3.3 70B, max_tokens=4096, temperature=0.3)
- 생성된 보고서는 `WorkflowRun.report_text`에 캐시됨

### 15.3 보고서 구조 (10개 섹션)

| # | 섹션 | 핵심 내용 |
|---|------|----------|
| 1 | 실행 개요 | 워크플로우명, iteration, 소요시간, AI 모델 |
| 2 | 이온화 지질 설계 및 선정 | MW, LogP, TPSA, 링커 생분해성, 탐색 전략, Pareto rank |
| 3 | 합성 가능성 평가 | 합성 조건, 수율(기준 >70%), 순도(기준 >95%), QC 결과 |
| 4 | LNP 제형 조성 분석 | 4성분 몰비, FDA 승인 제형 비교 (Onpattro/Comirnaty/Spikevax) |
| 5 | 물리화학적 특성 평가 | 입자 크기, PDI, 제타 전위, EE% — 판정 기준표 포함 |
| 6 | 기능성 평가 | Luminescence, transfection efficiency, 세포주/cargo |
| 7 | 구조-활성 관계(SAR) | Feature importance 기반 descriptor 분석, SAR 가설 |
| 8 | AI 모델 성능 | R²/RMSE 변화, 학습 데이터 증가, 수렴 추세 |
| 9 | 차기 반복 권고 | 조성비 조정, 구조 변경, 실험 조건 변경 구체적 수치 |
| 10 | 결론 | 성공/실패 판정, DDS 개발 가능성, 로드맵 |

### 15.4 벤치마크 데이터

보고서 생성 시 다음 참고 데이터가 AI에 함께 전달됩니다:

**FDA 승인 LNP 제형:**

| 제품명 | 이온화 지질 | IL:HL:Chol:PEG | 입자크기 | 적응증 |
|--------|-----------|---------------|---------|--------|
| Onpattro | MC3 | 50:10:38.5:1.5 | 60-100nm | hATTR (siRNA) |
| Comirnaty | ALC-0315 | 46.3:9.4:42.7:1.6 | ~80nm | COVID-19 (mRNA) |
| Spikevax | SM-102 | 50:10:38.5:1.5 | ~100nm | COVID-19 (mRNA) |

**물리화학적 특성 판정 기준:**

| 항목 | 우수 | 양호 | 주의 | 부적합 |
|------|------|------|------|--------|
| 입자 크기 (nm) | 60-100 | 100-150 | 150-200 | >200 |
| PDI | <0.1 | 0.1-0.2 | 0.2-0.3 | >0.3 |
| 제타 전위 (mV) | -30~-20 | -20~-10 | -10~0 | >0 or <-40 |
| 캡슐화 효율 (%) | >95 | 85-95 | 75-85 | <75 |

---

## 16. AI Assistant (채팅)

### 16.1 기능 요약

모든 페이지 우하단의 채팅 버튼으로 AI 어시스턴트와 대화. 현재 페이지 컨텍스트를 인식하여 관련 데이터 기반으로 응답.

### 16.2 동작

| 항목 | 설명 |
|------|------|
| 위치 | 모든 페이지 우하단 플로팅 버튼 |
| API | `POST /assistant/api/chat/` |
| 모델 | Groq (Llama 3.3 70B) |
| 컨텍스트 인식 | 현재 페이지에 따라 관련 DB 데이터 자동 조회 |
| 대화 이력 | 최근 20개 메시지 유지 |

### 16.3 페이지별 컨텍스트

| 페이지 | 자동 조회 데이터 |
|--------|----------------|
| Dashboard | 전체 통계 (레코드 수, 모델 수, 장비 수) |
| Compounds | 지질 라이브러리 통계 (총 수, 평균 물성) |
| Formulations | 제형 통계 (총 수, 평균 조성비) |
| Experiments | 실험 통계 (총 수, 방법별 분포) |
| AI Models | AI 모델 목록 및 성능 메트릭 |
| Equipment | 장비 상태 현황 |
| Workflow | 워크플로우 실행 현황 |

---

## 17. 데이터베이스 스키마 요약

### 17.1 ER 다이어그램

```
IonizableLipid (13,339) ──┐
  ├── HeadGroup (771)      │
  ├── Linker (38)          │
  └── Tail x4 (374)       │
                           │
HelperLipid (7) ──────────┤
Cholesterol (16) ─────────┼── LNPFormulation (19,797+) ── ExperimentResult (19,797+)
PEGLipid (15) ────────────┘        │                            │
                                    │                      Experiment (43+)
                                    │
AIModel (3) ── Prediction           │
            └── GeneratedCandidate  │
                                    │
Equipment (5) ── EquipmentStatus    │
                                    │
WorkflowRun ── WorkflowStep (5 per run)
```

### 17.2 주요 수치

| 모델 | 레코드 수 | 비고 |
|------|----------|------|
| IonizableLipid | 13,339 | 17개 분자 기술자 |
| LNPFormulation | 19,797+ | 파이프라인 실행 시 추가 생성 |
| ExperimentResult | 19,797+ | 파이프라인 실행 시 추가 생성 |
| Experiment | 43+ | 파이프라인 실행 시 추가 생성 |
| GeneratedCandidate | 0+ | Design step에서 생성 |
| EquipmentStatus | 5+ | 각 step 실행 시 로그 추가 |

---

## 18. 환경 설정

### 18.1 필수 의존성

```
Django>=5.0,<6.1
djangorestframework>=3.14
django-extensions>=3.2
requests>=2.31
```

### 18.2 환경변수

| 변수명 | 필수 | 설명 | 기본값 |
|--------|------|------|--------|
| `GROQ_API_KEY` | 선택 | AI 보고서 및 채팅 기능 | "" (미설정 시 해당 기능 비활성) |
| `DJANGO_SECRET_KEY` | 선택 | Django 시크릿 키 | dev용 기본값 내장 |
| `DJANGO_DEBUG` | 선택 | 디버그 모드 | "True" |
| `DJANGO_ALLOWED_HOSTS` | 선택 | 허용 호스트 | "*" |

### 18.3 설치 및 실행

```bash
git clone <repository-url>
cd omnilnp_django
pip install -r requirements.txt
# db.sqlite3 포함된 경우 바로 실행 가능
GROQ_API_KEY="gsk_..." python manage.py runserver
```

DB 초기화가 필요한 경우:
```bash
python manage.py migrate
python manage.py runscript seed_db          # LNPDB 19,797건 로딩 (~3분)
python manage.py runscript create_demo_data # 장비 5개, AI 모델 3개 생성
python manage.py createsuperuser
```

---

## 19. 전체 URL 경로 맵

| # | 경로 | 기능 | 메뉴 위치 |
|---|------|------|----------|
| 1 | `/accounts/login/` | 로그인 | — |
| 2 | `/` | Dashboard | OVERVIEW > Dashboard |
| 3 | `/compounds/` | Lipid Explorer | DATA > Lipid Explorer |
| 4 | `/compounds/<pk>/` | Lipid 상세 | Explorer에서 이름 클릭 |
| 5 | `/compounds/compare/` | Lipid 비교 | — |
| 6 | `/compounds/helpers/` | Helper Lipid 카탈로그 | — |
| 7 | `/formulations/` | Formulation 목록 | DATA > Formulations |
| 8 | `/formulations/designer/` | Formulation Designer | Quick Actions |
| 9 | `/experiments/` | Experiments | DATA > Experiments |
| 10 | `/ai/predict/` | AI 물성 예측 | AI MODELS > Predict |
| 11 | `/ai/generate/` | AI 구조 생성 | AI MODELS > Generate |
| 12 | `/ai/optimize/` | AI 다목적 최적화 | AI MODELS > Optimize |
| 13 | `/equipment/` | 장비 모니터링 | LAB > Equipment |
| 14 | `/workflow/` | 워크플로우 파이프라인 | LAB > Workflow |
| 15 | `/workflow/<pk>/` | 워크플로우 상세 | Workflow에서 Details 클릭 |
| 16 | `/admin/` | Django Admin | — |

---

## 20. 계획서 대응표 (인실리콕스 1차년도 과제)

| 계획서 항목 | 플랫폼 기능 | 구현 상태 |
|-----------|-----------|----------|
| 이온화지질 구조-LNP 조성-실험 설계 모델 정의 | Formulation Designer + AI Predict | 완료 |
| 학습 데이터 셋 구축 | LNPDB 19,797건 + Lipid Explorer | 완료 |
| 생성형 AI 기반 이온화지질 구조 설계 프로토타입 | AI Generate 페이지 | 완료 |
| LNP 제형 후보 설계 AI 모델 프로토타입 | AI Predict + Formulation Designer | 완료 |
| 생성형 AI 기반 실험 조건 제안 알고리즘 초기 모델 | AI Optimize 페이지 | 완료 |
| AI-자동화 장비 간 통신 인터페이스 설계 | Equipment REST API + Monitor | 완료 |
| 자동화 장비-로봇-AI 자율실험실 시스템 구현 | Workflow Pipeline (5단계 실행 엔진) | 완료 |
| 웹 기반 플랫폼 프로토타입 개발 | 전체 플랫폼 (16 pages + API) | 완료 |
