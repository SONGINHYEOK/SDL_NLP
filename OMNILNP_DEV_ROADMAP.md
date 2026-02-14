# OmniLNP Platform - Development Roadmap

## 1. Project Overview

**OmniLNP**: AI-Native Autonomous Lab Platform for LNP (Lipid Nanoparticle) Development  
**Purpose**: 인실리콕스 1차년도 연구개발 과제의 "자율실험실 통합 관리 및 AI 모델 활용을 위한 웹 기반 플랫폼 프로토타입 개발"  
**Data**: LNPDB (Song, Baek & Seo, 2026, Scientific Data) - 19,797 records, 13,339 unique lipids

---

## 2. Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Django 6.0 + DRF (Django REST Framework) |
| DB | SQLite (16.4 MB, 프로토타입용) |
| Frontend | Tailwind CSS + HTMX + Chart.js + SmilesDrawer |
| Template | Django Templates (Jinja-like) |
| Design | Dark theme (#0f1117 base), Plus Jakarta Sans + JetBrains Mono |

---

## 3. Project Structure

```
omnilnp/
├── config/          # Django settings, urls, wsgi/asgi
├── accounts/        # User model (Custom AbstractUser)
├── dashboard/       # Main dashboard view
├── compounds/       # IonizableLipid, HeadGroup, Linker, Tail, HelperLipid, Cholesterol, PEGLipid
├── formulations/    # LNPFormulation (19,797 records)
├── experiments/     # Experiment (43), ExperimentResult (19,797)
├── ai_models/       # AIModel, Prediction, GeneratedCandidate
├── equipment/       # Equipment (5), EquipmentStatus + DRF API
├── workflow/        # WorkflowRun (2), WorkflowStep (10)
├── templates/
│   ├── base/base.html          # 공통 레이아웃 (sidebar nav + topbar)
│   ├── dashboard/index.html    # [DONE] 풀 구현
│   ├── compounds/
│   │   ├── list.html           # [DONE] Lipid Explorer
│   │   ├── detail.html         # [DONE] 2D구조 + Radar + 실험결과
│   │   ├── compare.html        # [SKELETON]
│   │   └── helpers.html        # [SKELETON]
│   ├── formulations/
│   │   ├── list.html           # [DONE] Formulation 리스트
│   │   └── designer.html       # [DONE] 4성분 슬라이더 + AI예측
│   ├── experiments/list.html   # [SKELETON] 7줄
│   ├── ai_models/
│   │   ├── predict.html        # [SKELETON] 7줄
│   │   ├── generate.html       # [SKELETON] 7줄
│   │   └── optimize.html       # [SKELETON] 7줄
│   ├── equipment/monitor.html  # [SKELETON] 7줄
│   └── workflow/
│       ├── pipeline.html       # [SKELETON] 7줄
│       └── run_detail.html     # [SKELETON] 7줄
├── db.sqlite3      # 16.4MB, 모든 데이터 시드 완료
└── manage.py
```

---

## 4. Completed Features (DONE)

### 4.1 Dashboard (`/`)
- LNPDB 통계 카드: Total Lipids, Formulations, Experiments, AI Models
- Top 10 Lipids by Formulation Count (horizontal bar chart)
- Cargo Distribution (mRNA/siRNA/pDNA doughnut chart)
- Experiment Method Distribution (bar chart)
- Recent Activity 타임라인 + Quick Actions

### 4.2 Lipid Explorer (`/compounds/`)
- 13,339 lipids 테이블 with pagination (50/page)
- 검색: name, SMILES
- 필터: has_ester, has_carbonate, has_disulfide
- 정렬: MW, LogP, TPSA, formulation count
- 각 행에서 Detail 페이지 링크

### 4.3 Lipid Detail (`/compounds/<pk>/`)
- **2D Structure Visualization**: SmilesDrawer v2.1.7로 SMILES -> 2D 구조 렌더링
- **11-Descriptor Radar Chart**: MW, LogP, TPSA, HBD, HBA, RotBonds, Rings, Fsp3, MolarRef, HeavyAtoms, N_Count
  - 이 lipid vs LNPDB 평균 비교 (Chart.js radar)
  - 0-1 정규화 (DB 전체 범위 기준)
- **Property Cards**: 대형(MW, LogP, TPSA, HBD/HBA) + 소형(6개) + 구조 컴포넌트(Head, Linker, Tails)
- **Experiment Charts**: Assay Method별 / Model System별 / Value Distribution 히스토그램
- **Results Table**: 최대 50개 실험결과 (LNP ID, Cargo tag, Model, Method, Value)
- Prev/Next 네비게이션

### 4.4 Formulation List (`/formulations/`)
- 19,797 formulations 테이블
- 검색 + Mixing method 필터

### 4.5 Formulation Designer (`/formulations/designer/`)
- **Ionizable Lipid 선택**: 실시간 검색 API (`/formulations/api/search-lipids/`) + Top 8 원클릭
- **4성분 Molar Composition 슬라이더**: IL(10-80), HL(0-50), Chol(0-60), PEG(0-10)
- **실시간 Composition Bar**: 컬러 바 + 합계 검증 (100 = green, else red)
- **Component Dropdowns**: Helper Lipid(7종), Cholesterol(16종), PEG(15종) - 사용빈도순
- **N/P Ratio 슬라이더** + **Mixing Method** 라디오
- **Donut Chart**: 4성분 비율 실시간 업데이트
- **AI Prediction 패널**: Efficacy score ring + Stability/Safety/Confidence + Diameter/PDI/Zeta/Encapsulation
- **Similar Formulations**: DB에서 동일 lipid의 유사 조성 검색 API (`/formulations/api/similar/`)
- **Design Summary** + **Save to Queue**

### 4.6 Equipment REST API (`/api/equipment/`)
- DRF ViewSet: GET/POST devices, command, report_status, status history

### 4.7 Base Template
- 다크 테마 사이드바 네비게이션 (3 sections: DATA, AI, LAB)
- Topbar with breadcrumb
- Chart.js CDN + Tailwind CDN
- HTMX ready

---

## 5. Remaining Tasks (TODO)

### Priority Legend
- **P0**: 데모 필수 (반드시 구현)
- **P1**: 높은 임팩트 (강력 권장)
- **P2**: 있으면 좋음 (시간 여유 시)

---

### 5.1 [P0] Experiment Explorer (`/experiments/`)

**현재**: View 로직은 있으나 템플릿이 7줄 스켈레톤  
**필요 작업**: `templates/experiments/list.html` 풀 구현

**레이아웃**:
- 상단: 통계 카드 (Total Results 19,797 / Methods 10종 / Models / Cargos)
- 필터 바: 검색(lnp_id, lipid name) + Method 드롭다운 + Cargo 드롭다운 + Model 드롭다운
- 결과 테이블: LNP ID, Lipid Name, Formulation Ratio, Cargo, Model, Method, Value
  - Value 색상 코딩 (>=1.0 green, >=0.5 amber, <0.5 gray)
  - Cargo 태그 (mRNA=blue, siRNA=violet, pDNA=teal)
- Pagination (50/page)
- HTMX partial reload for filters

**View 참고**: `experiments/views.py` - experiment_list() 이미 구현됨  
**Model**: ExperimentResult.Method choices 10종, Experiment.CargoType 3종

---

### 5.2 [P0] AI Predict (`/ai/predict/`)

**현재**: View 로직 + predict_api() 있으나 템플릿이 스켈레톤  
**필요 작업**: `templates/ai_models/predict.html` 풀 구현

**레이아웃**:
- 좌측 (8 cols): 입력 패널
  - SMILES 입력 (textarea) + 구조 미리보기 (SmilesDrawer)
  - OR Lipid 검색/선택 (compounds에서 가져옴)
  - Formulation 파라미터: 4성분 비율 간단 입력
  - "Predict" 버튼 -> POST `/ai/predict/api/`
- 우측 (4 cols): 결과 패널
  - 예측된 물성: Efficacy, Diameter, PDI, Zeta, Encapsulation
  - Confidence score
  - DB에서 유사 lipid 비교
- 하단: Recent Predictions 히스토리 테이블

**API**: `ai_models/views.py - predict_api()` - SMILES 매칭 or 평균값 반환 (demo)  
**참고**: Formulation Designer의 prediction 패널과 디자인 일관성 유지

---

### 5.3 [P0] Equipment Monitor (`/equipment/`)

**현재**: View에서 5개 장비 + 최신 상태 쿼리. 템플릿 스켈레톤  
**필요 작업**: `templates/equipment/monitor.html` 풀 구현

**장비 목록 (Equipment 모델, 5개 시드)**:
1. Liquid Handler (liquid_handler) - REST API
2. Microfluidic Mixer (microfluidic) - MQTT
3. DLS Analyzer (dls) - OPC-UA
4. Plate Reader (plate_reader) - REST API
5. Centrifuge (centrifuge) - Serial

**레이아웃**:
- 상단: 5개 장비 카드 그리드
  - 장비명 + 타입 + 프로토콜 배지
  - 상태 인디케이터 (idle=gray, running=green pulse, error=red, maintenance=amber, offline=dark)
  - 최근 메시지 + 타임스탬프
  - 메타데이터: temperature, humidity 등 (JSON)
- 중단: 타임라인/로그 뷰 (최근 status 변경 이력, 모든 장비 통합)
- 하단: 장비별 상세 패널 (클릭 시 확장)
  - Command 전송 (DRF API 연동 `/api/equipment/devices/{pk}/command/`)
  - Status history 차트 (최근 24h)

**핵심 포인트**: REST API는 이미 DRF로 구현됨 (`equipment/api_views.py`, `api_urls.py`, `serializers.py`)

---

### 5.4 [P0] Workflow Pipeline (`/workflow/`)

**현재**: View에서 2개 WorkflowRun + 10개 Steps 쿼리. 템플릿 스켈레톤  
**필요 작업**: `templates/workflow/pipeline.html` + `templates/workflow/run_detail.html` 풀 구현

**Workflow Run 구조**:
- 5 Step Types: Design -> Synthesize -> Formulate -> Analyze -> Learn (closed-loop)
- Status: designing / queued / running / analyzing / completed / failed
- progress_pct 프로퍼티 있음

**Pipeline 레이아웃**:
- 상단: "New Workflow" 버튼 + 통계 (Active / Completed / Failed)
- Workflow Run 카드 리스트:
  - Run 이름 + Iteration + Status 배지
  - Progress bar (step completion %)
  - 5-step 아이콘 행 (Design -> Synthesize -> Formulate -> Analyze -> Learn)
    - completed=green, running=blue pulse, pending=gray, failed=red
  - 타임스탬프 (created, completed)
  - "View Details" 링크

**Run Detail 레이아웃** (`/workflow/<pk>/`):
- 수직 또는 수평 스텝 타임라인
- 각 Step: 타입 아이콘 + 상태 + input_data / output_data JSON 뷰어
- Equipment 연결 표시 (어떤 장비가 사용되었는지)
- 실행 시간 (started_at ~ completed_at)

---

### 5.5 [P1] AI Generate (`/ai/generate/`)

**현재**: View에서 GeneratedCandidate 쿼리. 템플릿 스켈레톤  
**필요 작업**: `templates/ai_models/generate.html` 풀 구현

**레이아웃**:
- 좌측: 생성 조건 입력
  - Target properties: MW 범위, LogP 범위, TPSA 범위
  - Structural constraints: has_ester, has_disulfide 체크
  - Generation count (5/10/20)
  - "Generate" 버튼
- 우측: 생성된 후보 리스트
  - SMILES + 2D 구조 (SmilesDrawer)
  - Predicted properties
  - Multi-objective scores (Efficacy, Stability, Safety)
  - Pareto rank
  - Status 배지 (generated -> selected -> synthesized -> tested -> validated)
  - "Select for Synthesis" 버튼

**Model**: GeneratedCandidate - smiles, predicted_properties(JSON), efficacy/stability/safety scores, pareto_rank, status

---

### 5.6 [P1] AI Optimize (`/ai/optimize/`)

**현재**: 빈 뷰. 템플릿 스켈레톤  
**필요 작업**: `templates/ai_models/optimize.html` 풀 구현

**레이아웃**:
- **Ternary Diagram**: IL-HL-Chol 3성분 삼각 다이어그램
  - 기존 LNPDB formulations을 점으로 표시 (value로 색상 코딩)
  - AI 추천 조성을 별도 마커로 표시
  - PEG는 고정값 (슬라이더로 조절)
- **Pareto Front**: Efficacy vs Safety 또는 Efficacy vs Stability 2D scatter
  - Pareto optimal 포인트 강조
  - 클릭하면 해당 formulation 상세
- **Optimization Parameters**:
  - 목적함수 선택 (maximize efficacy, minimize toxicity, etc.)
  - Constraints (MW range, LogP range)
  - Algorithm (Bayesian Opt / Genetic Algorithm / Random Search)
- **Iteration History**: 각 최적화 round의 best score 추이 (line chart)

---

### 5.7 [P1] Lipid Compare (`/compounds/compare/`)

**현재**: URL 있으나 스켈레톤  
**필요 작업**: `templates/compounds/compare.html` 풀 구현

**레이아웃**:
- 2~4개 lipid 선택 (검색 + 추가)
- Side-by-side 비교:
  - 2D 구조 나란히
  - Radar chart 오버레이 (같은 차트에 여러 lipid)
  - Property table 비교
  - Experiment result 통계 비교

---

### 5.8 [P2] Dashboard 고도화

- Closed-loop iteration 진행 현황 위젯
- 최근 AI Prediction 결과 미니 차트
- Equipment 상태 요약 (5개 장비 미니 카드)
- Workflow 진행 중인 Run 표시

---

### 5.9 [P2] 로그인/인증

- accounts app의 Custom User 모델 활용
- 로그인 페이지 (다크 테마)
- @login_required decorator 적용
- 프로토타입이므로 단순 세션 인증

---

## 6. Design System Reference

### Color Palette
```
--dark-700: #0f1117   (page background)
--dark-600: #161b22   (card background)
--dark-500: #1c2333   (sidebar, hover)
--dark-400: #2d3548   (border)
--dark-300: #3d4a5c   (muted border)
--dark-200: #6b7b8f   (secondary text)
--dark-100: #9ca8c0   (body text)
--dark-50:  #c9d1d9   (primary text)

--blue-500: #3b82f6   (primary accent)
--violet-500: #8b5cf6 (helper lipid)
--amber-500: #f59e0b  (cholesterol)
--cyan-500: #22d3ee   (PEG)
--emerald-400: #34d399 (success/good values)
--rose-500: #f43f5e   (error/danger)
```

### Typography
- Headers: Plus Jakarta Sans, 700-800 weight
- Body: Plus Jakarta Sans, 400-500 weight
- Code/Data: JetBrains Mono, 400-500 weight
- 크기: 타이틀 22px, 카드 헤더 13px, 본문 12-13px, 라벨 10-11px

### Component Patterns
- Card: `bg-dark-600 border border-dark-400 rounded-xl`
- Card Header: `px-5 py-3 border-b border-dark-400`
- Badge/Tag: `px-2 py-0.5 rounded text-[9px] font-semibold`
- Button Primary: `px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-[12px] font-semibold`
- Input: `bg-dark-700 border border-dark-400 rounded-lg px-3.5 py-2 text-[13px] text-dark-50 placeholder-dark-200 focus:border-blue-500 focus:outline-none`
- Table Row Hover: `hover:bg-blue-500/[0.03]`
- Status Pulse: `animate-pulse` for running states

---

## 7. Data Schema Quick Reference

### Key Models & Counts
| Model | Count | Key Fields |
|-------|-------|-----------|
| IonizableLipid | 13,339 | name, smiles, MW, LogP, TPSA, HBD, HBA, 17 descriptors, has_ester/carbonate/disulfide |
| HeadGroup | 771 | name, smiles (FK from IonizableLipid) |
| Linker | 38 | name, smiles (FK from IonizableLipid) |
| Tail | 374 | name, smiles (M2M or FK from IonizableLipid) |
| HelperLipid | 7 | DOPE(9312), DSPC(5525), DOTAP(2470), MDOA, DDAB, 14PA, 18PG |
| Cholesterol | 16 | Cholesterol(19464), n-butyl lithocholate(35), Beta-Sitosterol, etc. |
| PEGLipid | 15 | DMG-PEG2000(11145), DMPE-PEG2000(6322), Unknown(1798), etc. |
| LNPFormulation | 19,797 | FK to IL/HL/CHL/PEG, il_molratio, hl_molratio, chl_molratio, peg_molratio, mixing_method |
| Experiment | 43 | experiment_id, model_name, model_type, route, cargo, dose_ug |
| ExperimentResult | 19,797 | lnp_id, FK to experiment+formulation, method(10종), value |
| AIModel | 3 | LNP-Efficacy-RF, LNP-Structure-VAE, LNP-Formulation-BO |
| Equipment | 5 | liquid_handler, microfluidic, dls, plate_reader, centrifuge |
| WorkflowRun | 2 | MC3-Optimization(running), Novel-Lipid-Discovery(completed) |
| WorkflowStep | 10 | 5 steps per run (design/synthesize/formulate/analyze/learn) |

### Average Molar Ratios (LNPDB)
- IL: 40.3, HL: 16.8, Chol: 40.0, PEG: 2.3
- N/P Ratio 평균: 5.0

### Experiment Methods (ExperimentResult.Method choices)
1. luminescence_normalized
2. luminescence_discretized_normalized
3. luminescence_relative_to_Spikevax
4. protein_adundance_normalized
5. uptake
6. editing_efficiency_normalized
7. LRP6_knockdown_normalized
8. diameter
9. zeta_potential
10. hemolysis_percent

### Mixing Methods
- handmixed: 18,310 (92.5%)
- microfluidics: 1,487 (7.5%)

---

## 8. URL Map

```
/                              -> dashboard:index         [DONE]
/accounts/login/               -> accounts:login          [DONE]
/accounts/logout/              -> accounts:logout         [DONE]
/compounds/                    -> compounds:list          [DONE]
/compounds/<pk>/               -> compounds:detail        [DONE]
/compounds/compare/            -> compounds:compare       [DONE]
/compounds/helpers/            -> compounds:helpers        [SKELETON -> 차후 개발]
/formulations/                 -> formulations:list       [DONE]
/formulations/designer/        -> formulations:designer   [DONE]
/formulations/api/search-lipids/ -> formulations:search_lipids [DONE]
/formulations/api/similar/     -> formulations:similar    [DONE]
/experiments/                  -> experiments:list        [DONE]
/ai/predict/                   -> ai_models:predict       [DONE]
/ai/predict/api/               -> ai_models:predict_api   [DONE]
/ai/generate/                  -> ai_models:generate      [DONE]
/ai/generate/api/              -> ai_models:generate_api  [DONE]
/ai/optimize/                  -> ai_models:optimize      [DONE]
/equipment/                    -> equipment:monitor       [DONE]
/workflow/                     -> workflow:pipeline       [DONE]
/workflow/<pk>/                -> workflow:detail         [DONE]
/api/equipment/devices/        -> DRF Equipment API       [DONE]
/admin/                        -> Django Admin            [DONE]
```

---

## 9. Development Order (Recommended)

```
Phase 1 - Core Demo Loop (P0)              ✅ 완료
  1. experiments/list.html                  ✅ 풀 구현 (필터, HTMX, 페이지네이션)
  2. equipment/monitor.html                 ✅ 풀 구현 (장비 카드, 커맨드 전송, 타임라인)
  3. workflow/pipeline.html                 ✅ 풀 구현 (5-step 파이프라인, 진행률)
  4. workflow/run_detail.html               ✅ 풀 구현 (스텝 타임라인, JSON 뷰어)
  5. ai_models/predict.html                 ✅ 풀 구현 (SMILES 입력, SmilesDrawer, 예측)

Phase 2 - AI Features (P1)                 ✅ 완료
  6. ai_models/generate.html                ✅ 풀 구현 (타겟 설정, 후보 리스트, Pareto)
  7. ai_models/optimize.html                ✅ 풀 구현 (삼각 다이어그램, Pareto front)
  8. compounds/compare.html                 ✅ 풀 구현 (레이더 오버레이, 속성 비교)

Phase 3 - Polish (P2)                      ✅ 완료
  9. Dashboard 고도화                        ✅ Equipment/Workflow/AI 위젯 추가
  10. 로그인/인증                             ✅ 로그인 페이지 + @login_required
```

---

## 10. Run Instructions

```bash
cd omnilnp
pip install django djangorestframework
python manage.py runserver
# -> http://127.0.0.1:8000/
```

DB는 이미 `db.sqlite3`에 모든 데이터가 시드되어 있음. migrate 불필요.

---

## 11. Key Implementation Notes

### Template Pattern
모든 페이지는 `{% extends "base/base.html" %}` 사용. 블록:
- `{% block title %}` - 페이지 타이틀
- `{% block breadcrumb %}` - 상단 경로
- `{% block extra_head %}` - CSS/style
- `{% block content %}` - 본문
- `{% block extra_js %}` - JavaScript

### HTMX Pattern
Filter/Search는 HTMX partial reload 지원:
```python
if request.headers.get("HX-Request"):
    return render(request, "app/_partial.html", ctx)
return render(request, "app/full.html", ctx)
```

### Chart.js Pattern
CDN 로드됨 (`base.html`). Dark theme 설정:
```javascript
Chart.defaults.color = '#9ca8c0';
Chart.defaults.borderColor = 'rgba(255,255,255,0.04)';
```

### SmilesDrawer Pattern
SMILES -> 2D 구조: `detail.html` 참고
```javascript
const drawer = new SmilesDrawer.SmiDrawer({width:420, height:300, ...});
SmilesDrawer.parse(smiles, tree => { drawer.draw(tree, 'canvas-id', 'dark'); });
```

### API Pattern (DRF)
Equipment API: `equipment/api_views.py` + `serializers.py` 참고.
Custom actions: `@action(detail=True, methods=['post'])`

---

## 12. 계획서 대응표 (인실리콕스 1차년도)

| 계획서 항목 | 플랫폼 기능 | 상태 |
|-----------|-----------|------|
| 이온화지질 구조-LNP 조성-실험 설계 모델 정의 | Formulation Designer + AI Predict | DONE |
| 학습 데이터 셋 구축 | LNPDB 19,797건 로드 + Explorer | DONE |
| 생성형 AI 기반 이온화지질 구조 설계 프로토타입 | AI Generate 페이지 | DONE |
| LNP 제형 후보 설계 AI 모델 프로토타입 | AI Predict + Formulation Designer | DONE |
| 생성형 AI 기반 실험 조건 제안 알고리즘 초기 모델 | AI Optimize 페이지 | DONE |
| AI-자동화 장비 간 통신 인터페이스 설계 | Equipment REST API + Monitor | DONE |
| 자동화 장비-로봇-AI 자율실험실 시스템 구현 | Workflow Pipeline + Run Detail | DONE |
| 웹 기반 플랫폼 프로토타입 개발 | 전체 플랫폼 (17 pages + 4 APIs) | DONE (100%) |

---

## 13. 차후 개발 항목 (Future Development)

### 우선순위 높음
| 항목 | 설명 | 비고 |
|------|------|------|
| 실제 AI 모델 연동 | Demo placeholder → 학습된 RF/VAE/BO 모델 교체 | predict_api, generate_api에 실제 모델 inference 연결 |
| 실제 장비 통신 | DRF API mock → 실제 장비 REST/MQTT/OPC-UA 연동 | Equipment API 엔드포인트는 준비 완료 |
| Workflow 자동 실행 | 수동 표시 → Celery/Redis 기반 비동기 파이프라인 | 현재는 DB 상태만 표시 |

### 우선순위 중간
| 항목 | 설명 | 비고 |
|------|------|------|
| Helper Lipid 페이지 | `compounds/helpers.html` 풀 구현 | HelperLipid(7), Cholesterol(16), PEGLipid(15) 목록 + 사용빈도 차트 |
| 사용자 관리 | 회원가입, 비밀번호 변경, 프로필 편집 | accounts.User 모델 활용 (role, organization 필드) |
| Formulation 상세 페이지 | `/formulations/<pk>/` 개별 제형 상세 뷰 | 현재는 리스트만 존재 |
| Experiment 상세 페이지 | `/experiments/<pk>/` 개별 실험 상세 뷰 | 현재는 리스트만 존재 |
| Prediction 히스토리 | AI 예측 결과 저장 + 히스토리 테이블 | Prediction 모델은 존재, UI 연결 필요 |

### 우선순위 낮음
| 항목 | 설명 | 비고 |
|------|------|------|
| 데이터 Export | CSV/Excel 다운로드 기능 | Lipid, Formulation, Experiment 데이터 |
| 알림 시스템 | 장비 에러, Workflow 완료 등 실시간 알림 | WebSocket 또는 polling |
| 다국어 지원 | 한국어/영어 전환 | Django i18n 활용 |
| 배포 설정 | PostgreSQL 전환, Docker, nginx, gunicorn | 현재는 SQLite + runserver |
| API 인증 강화 | DRF Token/JWT 인증 | 현재는 AllowAny |
