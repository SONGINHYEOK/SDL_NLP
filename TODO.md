# OmniLNP - 구현 현황 및 남은 과제

## Project Context

AI-Native 자율실험실 플랫폼 (인실리콕스 1차년도 과제)
Django 5.x + Tailwind CDN + HTMX + Chart.js
DB: SQLite (19,797 LNPDB records seeded)


## Current Status

### DONE - 전체 페이지 구현 완료

| Page | 경로 | 주요 기능 |
|------|------|----------|
| Dashboard | `/` | 5개 통계 카드, 파이프라인 시각화, 장비 상태, 최근 데이터 |
| Lipid Explorer | `/compounds/` | 13,339종 검색/필터/정렬, 페이지네이션 |
| Lipid Detail | `/compounds/<pk>/` | 2D 구조(SmilesDrawer), 11축 레이더 차트, 17개 물성, 실험 결과 |
| Lipid Compare | `/compounds/compare/` | 최대 4개 지질 병렬 비교, 오버레이 레이더 차트 |
| Helper Lipids | `/compounds/helpers/` | HL(7)/Chol(16)/PEG(15) 카탈로그 |
| Formulation List | `/formulations/` | 19,797건 검색/필터, 페이지네이션 |
| Formulation Designer | `/formulations/designer/` | 4성분 슬라이더, 도넛 차트, AI 예측, 유사 제형 |
| Experiments | `/experiments/` | method/cargo/model 필터, 데이터 테이블 |
| AI Predict | `/ai/predict/` | SMILES 입력 → 물성 예측, 구조 프리뷰 |
| AI Generate | `/ai/generate/` | 타겟 물성 범위 → 후보 생성, Pareto rank |
| AI Optimize | `/ai/optimize/` | 삼각 다이어그램, Pareto front, **최적 조성 결과 카드** |
| Equipment Monitor | `/equipment/` | 장비 상태 카드, 명령 전송, 타임라인 |
| Workflow Pipeline | `/workflow/` | 워크플로우 목록, 5단계 시각화, 생성 |
| Workflow Detail | `/workflow/<pk>/` | 타임라인, input/output JSON, AI 보고서 |
| Equipment Maintenance | `/equipment/maintenance/` | 장비 캘리브레이션/정비 일정, 기한 초과 알림 |
| Inventory Dashboard | `/inventory/` | 시약 12종 재고 추적, FIFO 소모, 부족 알림 |

### DONE - Workflow Pipeline 실행 엔진 (`workflow/pipeline.py`)

| Step | 동작 | DB 레코드 생성 |
|------|------|---------------|
| Design | IonizableLipid 필터링 → 후보 샘플링 → Pareto rank | GeneratedCandidate x N, Prediction x 1 |
| Synthesize | 지질 물성 기반 합성 조건 시뮬레이션 + 시약 소모 | EquipmentStatus x 2, ReagentConsumption x 2 |
| Formulate | 4성분 조성 생성 → LNPFormulation 레코드 생성 + 시약 소모 | LNPFormulation x 1, EquipmentStatus x 2, ReagentConsumption x 4 |
| Analyze | Experiment + ExperimentResult 생성, DB 벤치마크 비교 + 시약 소모 | Experiment x 1, ExperimentResult x 3, EquipmentStatus x 2, ReagentConsumption x 2 |
| Learn | AIModel 메트릭 개선, feature importance, suggestions | AIModel 업데이트 |

- Step 간 input→output 체이닝 구현
- 실패 시 step을 FAILED 상태로 마킹
- 각 step output에 `reagents_consumed` 키 포함 (FIFO 소모)

### DONE - AI 보고서 (Groq API)

LNP 최적화 논문 수준의 10개 섹션:
1. 실행 개요
2. 이온화 지질 설계 및 선정 (MW, LogP, 링커 생분해성)
3. 합성 가능성 평가 (수율, 순도, QC)
4. LNP 제형 조성 분석 (FDA 승인 제형 대비 비교)
5. 물리화학적 특성 평가 (판정 기준표 포함)
6. 기능성 평가 (transfection efficiency)
7. 구조-활성 관계(SAR) 인사이트
8. AI 모델 성능 및 학습
9. 차기 반복 권고사항
10. 결론

### DONE - API Endpoints

| Endpoint | Method | 상태 |
|----------|--------|------|
| `/formulations/api/search-lipids/?q=` | GET | Working |
| `/formulations/api/similar/` | GET | Working |
| `/ai/predict/api/` | POST | Working |
| `/ai/generate/api/` | POST | Working |
| `/api/equipment/devices/` | GET/POST | DRF ViewSet |
| `/api/equipment/devices/<pk>/command/` | POST | Working |
| `/api/equipment/devices/<pk>/status/` | GET | Working |
| `/api/equipment/devices/<pk>/report_status/` | POST | Working |
| `/assistant/api/chat/` | POST | Groq API |
| `/assistant/api/report/<pk>/` | POST | Groq API |

### DB State

```
IonizableLipid: 13,339 (17 molecular descriptors each)
HeadGroup: 771 | Linker: 38 | Tail: 374
HelperLipid: 7 | Cholesterol: 16 | PEGLipid: 15
LNPFormulation: 19,797+
Experiment: 43+ | ExperimentResult: 19,797+
AIModel: 3 | Equipment: 5 | WorkflowRun: 2+
MaintenanceRecord: 7+ (calibration, preventive, corrective, cleaning, software_update)
Reagent: 12 | ReagentStock: 24+ | ReagentConsumption: 0+ (파이프라인 실행 시 생성)
SQLite DB: ~16MB (included in repo)
```


## Phase 2: 실제 AI Model 통합

### 2-1. Property Predictor (scikit-learn)

현재 `/ai/predict/api/`가 DB 매칭 또는 평균값 반환으로 동작. 실제 모델로 교체.

```python
# scripts/train_efficacy_model.py
# 1. LNPDB에서 luminescence_normalized 값 추출
# 2. 17개 molecular descriptor를 feature로 사용
# 3. RandomForest/XGBoost 학습
# 4. joblib로 저장 -> AIModel.model_path에 경로 기록
# 5. predict_api에서 joblib.load -> model.predict
```

Features: 17 descriptors (MW, LogP, TPSA, HBD, HBA, RotBonds, Rings, AromaticRings, vdW_Volume, MolarRef, Fsp3, sp3C, N_Count, HeavyAtoms, has_ester, has_carbonate, has_disulfide)
Target: luminescence_normalized (14,630 records)
Train/Test split by publication (data leakage 방지)

### 2-2. Structure Generator (VAE or similar)

- SMILES tokenization -> VAE latent space
- Conditional generation by target properties
- Validity/novelty/uniqueness metrics
- RDKit로 생성 구조 검증

### 2-3. Formulation Optimizer (Bayesian Optimization)

- 4-component 조성 공간에서 최적 N/P ratio, mixing method 탐색
- Multi-objective: efficacy + stability + safety
- Pareto front 도출


## Phase 3: SDL (Self-Driving Lab) 연동

### 3-1. Equipment Simulator

시연용으로 실제 장비 없이 SDL 흐름 데모.

```python
# equipment/simulator.py
# - EquipmentSimulator class
# - Hamilton STAR: protocol 실행 시뮬레이션
# - NanoAssemblr: formulation 생성 시뮬레이션
# - DLS: diameter/PDI/zeta 측정값 생성
# - Plate Reader: luminescence 값 생성
# - 각 장비 상태를 EquipmentStatus에 기록
```

### 3-2. Real-time Status (WebSocket)

- Django Channels로 장비 상태 실시간 push
- Equipment Monitor 페이지에 WebSocket 연결
- 워크플로우 진행 상태 실시간 업데이트


## Phase 4: Production 준비

### 4-1. PostgreSQL Migration

```bash
pip install psycopg2-binary dj-database-url
# .env: DATABASE_URL=postgres://user:pass@localhost:5432/omnilnp
```

### 4-2. Deployment

- Docker Compose (Django + PostgreSQL + Redis + Celery)
- Nginx reverse proxy
- Tailwind CSS build (CDN -> production build)
- collectstatic + gunicorn/uvicorn

### 4-3. Testing

```python
# 각 앱에 tests.py 작성
# - Model: 생성/검증/관계
# - View: 렌더링/필터/검색
# - API: CRUD/command/status
# - Pipeline: 5단계 실행 검증
```
