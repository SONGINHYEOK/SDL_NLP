# OmniLNP - AI-Native Autonomous Lab Platform

LNP(Lipid Nanoparticle) 신약 개발을 위한 AI 기반 자율실험실 플랫폼.
LNPDB(19,797건 실험 데이터, 13,339종 이온화 지질)를 기반으로 AI 설계 → 합성 → 제형화 → 분석 → 학습의 5단계 Closed-loop 최적화 파이프라인을 제공합니다.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 5.x, Django REST Framework |
| Database | SQLite (개발), PostgreSQL (운영) |
| Frontend | Tailwind CSS (CDN), HTMX, Chart.js, SmilesDrawer |
| AI Report | Groq API (Llama 3.3 70B) |
| Language | Python 3.9+ |

## Quick Start

### 1. 저장소 클론 및 의존성 설치

```bash
git clone <repository-url>
cd omnilnp_django

# 가상환경 생성 (권장)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 데이터베이스 설정

프로젝트에 **사전 구축된 `db.sqlite3`** (16MB)이 포함되어 있습니다.
이 파일이 있다면 바로 서버를 실행할 수 있습니다.

**DB 파일이 없거나 초기화가 필요한 경우:**

```bash
# 마이그레이션
python manage.py migrate

# LNPDB 데이터 로딩 (19,797건, 약 2-3분 소요)
python manage.py runscript seed_db

# 데모 데이터 생성 (장비 5개, AI 모델 3개, 워크플로우 2개)
python manage.py runscript create_demo_data

# 관리자 계정 생성
python manage.py createsuperuser
```

### 3. 환경변수 설정

```bash
# AI 보고서 생성 기능에 필요 (선택사항)
export GROQ_API_KEY="gsk_your_api_key_here"
```

> Groq API 키가 없어도 플랫폼의 모든 기능이 동작합니다.
> 워크플로우 완료 후 AI 보고서 생성 기능만 비활성화됩니다.
> 키 발급: https://console.groq.com/keys

### 4. 서버 실행

```bash
GROQ_API_KEY="gsk_..." python manage.py runserver
```

브라우저에서 http://127.0.0.1:8000/ 접속
## 주요 기능

### DATA - 데이터 탐색

| 페이지 | 경로 | 설명 |
|--------|------|------|
| Dashboard | `/` | 통계 카드, 파이프라인 개요, 최근 데이터 |
| Lipid Explorer | `/compounds/` | 13,339종 이온화 지질 검색/필터/정렬 |
| Lipid Detail | `/compounds/<pk>/` | 2D 구조, 레이더 차트, 17개 물성, 실험 결과 |
| Lipid Compare | `/compounds/compare/` | 최대 4개 지질 병렬 비교 |
| Formulations | `/formulations/` | 19,797건 LNP 제형 목록 |
| Formulation Designer | `/formulations/designer/` | 4성분 슬라이더, AI 예측, 유사 제형 검색 |
| Experiments | `/experiments/` | 실험 결과 필터링 (method/cargo/model) |

### AI MODELS - AI 모델링

| 페이지 | 경로 | 설명 |
|--------|------|------|
| Predict | `/ai/predict/` | SMILES 입력 → 17개 물성 예측 |
| Generate | `/ai/generate/` | 타겟 물성 범위 설정 → 신규 지질 후보 생성 |
| Optimize | `/ai/optimize/` | 삼각 다이어그램, Pareto front, 최적 조성 도출 |

### LAB - 자율실험실

| 페이지 | 경로 | 설명 |
|--------|------|------|
| Equipment | `/equipment/` | 5개 장비 상태 모니터링, 명령 전송 |
| Workflow | `/workflow/` | Closed-loop 파이프라인 관리 |
| Workflow Detail | `/workflow/<pk>/` | 5단계 실행 상세 + AI 보고서 생성 |

### AI Assistant

모든 페이지 우하단의 채팅 버튼으로 AI 어시스턴트와 대화할 수 있습니다.
현재 페이지 컨텍스트를 인식하여 관련 데이터 기반으로 응답합니다.

## Workflow Pipeline (핵심 기능)

5단계 Closed-loop 최적화 파이프라인:

```
Design → Synthesize → Formulate → Analyze → Learn
  │          │            │           │          │
  │          │            │           │          └─ AI 모델 성능 개선
  │          │            │           └─ Experiment + ExperimentResult 생성
  │          │            └─ LNPFormulation 레코드 생성
  │          └─ 합성 조건 시뮬레이션 + 장비 로그
  └─ DB 기반 후보 지질 선별 + GeneratedCandidate 생성
```

### 워크플로우 실행 방법

1. `/workflow/` → **New Workflow** 버튼 클릭
2. 이름, 설명, AI 모델 선택 후 생성
3. 각 단계마다: **Approve** (승인) → **Simulate** (실행)
4. 5단계 완료 후 **Generate AI Report** 버튼으로 보고서 생성

### 각 단계별 생성되는 DB 레코드

| Step | 생성 레코드 | 주요 Output |
|------|------------|------------|
| Design | GeneratedCandidate x N, Prediction x 1 | top_candidate (lipid_id, scores) |
| Synthesize | EquipmentStatus x 2 | yield, purity, synthesis_conditions |
| Formulate | LNPFormulation x 1, EquipmentStatus x 2 | formulation_pk, composition, N/P ratio |
| Analyze | Experiment x 1, ExperimentResult x 3, EquipmentStatus x 2 | diameter, PDI, zeta, EE%, luminescence |
| Learn | AIModel 업데이트 | R2/RMSE 개선, feature_importance, suggestions |

### AI 보고서 내용

완료된 워크플로우에서 생성되는 보고서는 LNP 최적화 논문 수준의 분석을 포함합니다:

- 이온화 지질 설계 및 선정 근거 (MW, LogP, 생분해성 링커)
- FDA 승인 제형(Onpattro, Comirnaty, Spikevax) 대비 조성 비교
- 물리화학적 특성 판정 (입자 크기, PDI, 제타 전위, 캡슐화 효율)
- 구조-활성 관계(SAR) 인사이트
- AI 모델 성능 변화 및 차기 반복 권고사항

## Project Structure

```
omnilnp_django/
├── config/                  # Django 설정
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                # 사용자 인증 (Custom User + Role)
├── dashboard/               # 메인 대시보드
├── compounds/               # 지질 라이브러리
│   └── models.py            #   IonizableLipid(13,339), HeadGroup, Linker, Tail,
│                            #   HelperLipid(7), Cholesterol(16), PEGLipid(15)
├── formulations/            # LNP 제형
│   └── models.py            #   LNPFormulation(19,797)
├── experiments/             # 실험 결과
│   └── models.py            #   Experiment(43), ExperimentResult(19,797)
├── ai_models/               # AI 모델 관리
│   └── models.py            #   AIModel, Prediction, GeneratedCandidate
├── equipment/               # 장비 모니터링
│   └── models.py            #   Equipment(5), EquipmentStatus
├── workflow/                # 파이프라인 오케스트레이션
│   ├── models.py            #   WorkflowRun, WorkflowStep
│   ├── pipeline.py          #   5단계 실행 엔진 (execute_step)
│   └── views.py
├── assistant/               # AI 어시스턴트 + 보고서 생성
├── templates/               # Django 템플릿 (dark theme)
├── static/                  # CSS, JS, 폰트
├── scripts/
│   ├── seed_db.py           # LNPDB CSV → DB 로딩
│   └── create_demo_data.py  # 데모 데이터 생성
├── data/seed/
│   └── LNPDB.csv            # 원본 데이터 (19,797건, 66컬럼)
├── db.sqlite3               # 사전 구축 DB (16MB)
├── requirements.txt
├── DEMO_SCENARIO.md         # 시연 튜토리얼 (Step-by-Step)
└── README.md
```

## DB Schema

```
IonizableLipid (13,339) ──┐
HelperLipid (7) ──────────┤
Cholesterol (16) ─────────┼── LNPFormulation (19,797) ── ExperimentResult (19,797)
PEGLipid (15) ────────────┘         │                           │
                                     │                     Experiment (43)
HeadGroup (771) ──┐                  │
Linker (38) ──────┼── IonizableLipid │
Tail (374) ───────┘                  │
                                     │
AIModel (3) ── Prediction            │
            └── GeneratedCandidate   │
                                     │
Equipment (5) ── EquipmentStatus     │
                                     │
WorkflowRun ── WorkflowStep (5 per run)
```

## API Endpoints

| Endpoint | Method | 설명 |
|----------|--------|------|
| `/formulations/api/search-lipids/?q=` | GET | 지질 검색 (autocomplete) |
| `/formulations/api/similar/` | GET | 유사 제형 검색 |
| `/ai/predict/api/` | POST | AI 물성 예측 |
| `/ai/generate/api/` | POST | AI 구조 생성 |
| `/api/equipment/devices/` | GET/POST | 장비 CRUD |
| `/api/equipment/devices/<pk>/command/` | POST | 장비 명령 전송 |
| `/api/equipment/devices/<pk>/status/` | GET | 장비 상태 이력 |
| `/assistant/api/chat/` | POST | AI 어시스턴트 채팅 |
| `/assistant/api/report/<pk>/` | POST | 워크플로우 AI 보고서 생성 |

## 시연 가이드

상세한 시연 시나리오는 [DEMO_SCENARIO.md](DEMO_SCENARIO.md) 를 참고하세요.

**Quick Demo (5분):**

1. 로그인 → Dashboard 통계 확인
2. Lipid Explorer → 지질 검색/상세/비교
3. Formulation Designer → 4성분 조성 설계 + AI 예측
4. AI Generate → 신규 구조 생성
5. Workflow → 새 워크플로우 생성 → 5단계 순차 실행 → AI 보고서

## Data Source

> **LNPDB**: Song, Baek & Seo (2026). *A comprehensive database for lipid nanoparticle-mediated nucleic acid delivery.* Scientific Data.
>
> 43개 논문에서 수집한 19,797건의 LNP 실험 결과와 13,339종의 고유 이온화 지질 구조를 포함합니다.

## License

InSiliCox Inc. Internal Use
