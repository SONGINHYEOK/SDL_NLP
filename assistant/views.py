import json
import requests as http_requests
from django.conf import settings
from django.db.models import Avg, Min, Max, Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

PAGE_CONTEXT = {
    "dashboard": "대시보드(Dashboard) 페이지 - 전체 파이프라인 현황, 핵심 지표(KPI), 실험 진행 상황을 보여줍니다. 사용자가 지표 해석이나 전체 현황 파악에 도움이 필요할 수 있습니다.",
    "compounds": "지질 탐색기(Lipid Explorer) 페이지 - 이온화 지질(Ionizable Lipid) 라이브러리를 탐색합니다. SMILES 구조, 물리화학적 성질(logP, pKa, MW 등), 구조-활성 관계(SAR)를 다룹니다.",
    "formulations": "제형 설계(Formulation Designer) 페이지 - LNP 제형의 조성비(이온화 지질, 헬퍼 지질, 콜레스테롤, PEG-지질)를 설계하고 최적화합니다.",
    "experiments": "실험 관리(Experiments) 페이지 - 실험 결과 데이터를 기록·조회합니다. 캡슐화 효율(EE%), 입자 크기, PDI, 제타 전위 등의 결과를 해석합니다.",
    "ai_models": "AI 모델(AI Models) 페이지 - 물성 예측(Predictor), 구조 생성(Generator), 다목적 최적화(Optimizer) 모델을 사용합니다.",
    "equipment": "장비 모니터링(Equipment Monitor) 페이지 - 실험실 장비의 실시간 상태(가동/유휴/오류/정비)와 프로토콜을 관리합니다.",
    "workflow": "워크플로우(Workflow) 페이지 - 폐쇄 루프(Closed-loop) 최적화 파이프라인의 단계별 진행 상황을 관리합니다. 설계→예측→실험→분석 순환 과정을 다룹니다.",
}

SYSTEM_PROMPT_TEMPLATE = """당신은 OmniLNP 플랫폼의 AI 어시스턴트입니다.
이 플랫폼은 AI 기반 지질 나노입자(LNP) 신약 개발 자동화 시스템입니다.

현재 사용자는 [{page_label}] 페이지에 있습니다.
{page_detail}

## 현재 플랫폼 데이터 현황
{db_data}

{screen_data_section}
위 데이터를 참고하여 사용자의 질문에 구체적 수치와 함께 답변하세요.
한국어로 답변하되, 전문 용어는 영문 병기하세요.
답변은 간결하게 유지하세요."""


def _get_db_data(page_context):
    """Fetch relevant DB data for the given page context."""
    lines = []
    try:
        if page_context == "dashboard":
            lines.extend(_data_dashboard())
        elif page_context == "compounds":
            lines.extend(_data_compounds())
        elif page_context == "formulations":
            lines.extend(_data_formulations())
        elif page_context == "experiments":
            lines.extend(_data_experiments())
        elif page_context == "ai_models":
            lines.extend(_data_ai_models())
        elif page_context == "equipment":
            lines.extend(_data_equipment())
        elif page_context == "workflow":
            lines.extend(_data_workflow())
        else:
            lines.extend(_data_dashboard())
    except Exception:
        lines.append("(데이터 조회 중 오류 발생)")
    return "\n".join(lines)


def _data_dashboard():
    from compounds.models import IonizableLipid, HelperLipid, Cholesterol, PEGLipid
    from formulations.models import LNPFormulation
    from experiments.models import Experiment, ExperimentResult
    from ai_models.models import AIModel, GeneratedCandidate
    from equipment.models import Equipment
    from workflow.models import WorkflowRun

    lines = []
    lines.append(f"- 이온화 지질(Ionizable Lipid): {IonizableLipid.objects.count():,}개")
    lines.append(f"- 헬퍼 지질: {HelperLipid.objects.count()}종, 콜레스테롤: {Cholesterol.objects.count()}종, PEG-지질: {PEGLipid.objects.count()}종")
    lines.append(f"- LNP 제형: {LNPFormulation.objects.count():,}개")
    lines.append(f"- 실험: {Experiment.objects.count():,}건, 실험 결과: {ExperimentResult.objects.count():,}건")
    lines.append(f"- AI 모델: 총 {AIModel.objects.count()}개 (활성: {AIModel.objects.filter(is_active=True).count()}개)")
    lines.append(f"- 생성 후보 물질: {GeneratedCandidate.objects.count():,}개")
    lines.append(f"- 장비: {Equipment.objects.count()}대 (연결: {Equipment.objects.filter(is_connected=True).count()}대)")
    wf_running = WorkflowRun.objects.filter(status__in=["running", "analyzing"]).count()
    lines.append(f"- 워크플로우: 총 {WorkflowRun.objects.count()}건 (진행 중: {wf_running}건)")
    return lines


def _data_compounds():
    from compounds.models import IonizableLipid, HeadGroup, Linker, Tail

    total = IonizableLipid.objects.count()
    lines = [f"- 전체 이온화 지질: {total:,}개"]
    lines.append(f"- Head Group: {HeadGroup.objects.count()}종, Linker: {Linker.objects.count()}종, Tail: {Tail.objects.count()}종")

    agg = IonizableLipid.objects.aggregate(
        mw_avg=Avg("molecular_weight"), mw_min=Min("molecular_weight"), mw_max=Max("molecular_weight"),
        logp_avg=Avg("logp"), logp_min=Min("logp"), logp_max=Max("logp"),
        tpsa_avg=Avg("tpsa"),
    )
    if agg["mw_avg"]:
        lines.append(f"- MW 범위: {agg['mw_min']:.1f} ~ {agg['mw_max']:.1f} (평균 {agg['mw_avg']:.1f})")
        lines.append(f"- logP 범위: {agg['logp_min']:.2f} ~ {agg['logp_max']:.2f} (평균 {agg['logp_avg']:.2f})")
        lines.append(f"- 평균 TPSA: {agg['tpsa_avg']:.1f}")

    src = IonizableLipid.objects.values("source").annotate(cnt=Count("id")).order_by("-cnt")
    if src:
        lines.append("- 출처별: " + ", ".join(f"{s['source']}({s['cnt']:,})" for s in src))

    top = IonizableLipid.objects.annotate(
        result_count=Count("formulations__results")
    ).order_by("-result_count")[:5]
    if top:
        lines.append("- 실험 데이터 많은 상위 지질:")
        for lip in top:
            if lip.result_count > 0:
                lines.append(f"  · {lip.name}: {lip.result_count}건 (MW={lip.molecular_weight}, logP={lip.logp})")

    return lines


def _data_formulations():
    from formulations.models import LNPFormulation
    from compounds.models import HelperLipid, Cholesterol, PEGLipid

    total = LNPFormulation.objects.count()
    lines = [f"- 전체 LNP 제형: {total:,}개"]

    src = LNPFormulation.objects.values("source").annotate(cnt=Count("id")).order_by("-cnt")
    if src:
        lines.append("- 출처별: " + ", ".join(f"{s['source']}({s['cnt']:,})" for s in src))

    method = LNPFormulation.objects.values("mixing_method").annotate(cnt=Count("id")).order_by("-cnt")
    if method:
        lines.append("- 혼합 방법: " + ", ".join(f"{m['mixing_method']}({m['cnt']:,})" for m in method if m['mixing_method']))

    hl_dist = LNPFormulation.objects.values("helper_lipid__name").annotate(cnt=Count("id")).order_by("-cnt")[:5]
    if hl_dist:
        lines.append("- 주요 헬퍼 지질: " + ", ".join(f"{h['helper_lipid__name']}({h['cnt']:,})" for h in hl_dist if h['helper_lipid__name']))

    agg = LNPFormulation.objects.aggregate(
        il_avg=Avg("il_molratio"), hl_avg=Avg("hl_molratio"),
        chl_avg=Avg("chl_molratio"), peg_avg=Avg("peg_molratio"),
    )
    if agg["il_avg"]:
        lines.append(f"- 평균 몰비: IL={agg['il_avg']:.1f}, HL={agg['hl_avg']:.1f}, CHL={agg['chl_avg']:.1f}, PEG={agg['peg_avg']:.2f}")

    return lines


def _data_experiments():
    from experiments.models import Experiment, ExperimentResult

    exp_total = Experiment.objects.count()
    res_total = ExperimentResult.objects.count()
    lines = [f"- 실험: {exp_total:,}건, 결과: {res_total:,}건"]

    cargo = Experiment.objects.values("cargo").annotate(cnt=Count("id")).order_by("-cnt")
    if cargo:
        lines.append("- 카고 타입: " + ", ".join(f"{c['cargo']}({c['cnt']:,})" for c in cargo))

    model_type = Experiment.objects.values("model_type").annotate(cnt=Count("id")).order_by("-cnt")
    if model_type:
        lines.append("- 모델 타입: " + ", ".join(f"{m['model_type']}({m['cnt']:,})" for m in model_type))

    methods = ExperimentResult.objects.values("method").annotate(cnt=Count("id")).order_by("-cnt")
    if methods:
        lines.append("- 측정 방법 분포: " + ", ".join(f"{m['method']}({m['cnt']:,})" for m in methods))

    recent = ExperimentResult.objects.select_related(
        "experiment", "formulation__ionizable_lipid"
    ).order_by("-created_at")[:10]
    if recent:
        lines.append("- 최근 실험 결과:")
        for r in recent:
            lip_name = r.formulation.ionizable_lipid.name if r.formulation and r.formulation.ionizable_lipid else "N/A"
            lines.append(f"  · [{r.method}] {lip_name}: {r.value} (모델: {r.experiment.model_name})")

    return lines


def _data_ai_models():
    from ai_models.models import AIModel, Prediction, GeneratedCandidate

    models = AIModel.objects.all()
    lines = [f"- AI 모델 총: {models.count()}개 (활성: {models.filter(is_active=True).count()}개)"]

    for m in models[:8]:
        pred_cnt = Prediction.objects.filter(ai_model=m).count()
        metrics_str = ""
        if m.metrics:
            metrics_str = ", ".join(f"{k}={v}" for k, v in m.metrics.items())
        lines.append(f"  · {m.name} v{m.version} ({m.model_type}) - {'활성' if m.is_active else '비활성'}, 예측 {pred_cnt}건" + (f", 성능: {metrics_str}" if metrics_str else ""))

    cand_total = GeneratedCandidate.objects.count()
    if cand_total:
        status_dist = GeneratedCandidate.objects.values("status").annotate(cnt=Count("id")).order_by("-cnt")
        lines.append(f"- 생성 후보 물질: {cand_total:,}개")
        lines.append("  상태별: " + ", ".join(f"{s['status']}({s['cnt']:,})" for s in status_dist))

    return lines


def _data_equipment():
    from equipment.models import Equipment, EquipmentStatus

    equips = Equipment.objects.all()
    lines = [f"- 장비 총: {equips.count()}대 (연결: {equips.filter(is_connected=True).count()}대)"]

    for eq in equips[:10]:
        latest = EquipmentStatus.objects.filter(equipment=eq).order_by("-timestamp").first()
        status_str = latest.status if latest else "unknown"
        msg = f" - {latest.message}" if latest and latest.message else ""
        lines.append(f"  · {eq.name} ({eq.equipment_type}, {eq.protocol}) - 상태: {status_str}{msg}")

    return lines


def _data_workflow():
    from workflow.models import WorkflowRun, WorkflowStep

    runs = WorkflowRun.objects.all()
    lines = [f"- 워크플로우 총: {runs.count()}건"]

    status_dist = runs.values("status").annotate(cnt=Count("id")).order_by("-cnt")
    if status_dist:
        lines.append("- 상태별: " + ", ".join(f"{s['status']}({s['cnt']})" for s in status_dist))

    active = runs.filter(status__in=["designing", "queued", "running", "analyzing", "paused"]).order_by("-created_at")[:5]
    if active:
        lines.append("- 진행 중 워크플로우:")
        for run in active:
            steps = WorkflowStep.objects.filter(workflow=run).order_by("step_order")
            step_summary = ", ".join(f"{s.step_type}:{s.status}" for s in steps)
            lines.append(f"  · {run.name} (반복 #{run.iteration}, 상태: {run.status}, 진행: {run.progress_pct}%)")
            if step_summary:
                lines.append(f"    단계: {step_summary}")

    recent_done = runs.filter(status="completed").order_by("-completed_at")[:3]
    if recent_done:
        lines.append("- 최근 완료:")
        for run in recent_done:
            lines.append(f"  · {run.name} (반복 #{run.iteration}, 완료: {run.completed_at})")

    return lines


REPORT_SYSTEM_PROMPT = """당신은 OmniLNP 플랫폼의 수석 연구 보고서 작성 AI입니다.
아래 워크플로우 실행 데이터를 기반으로, LNP 최적화 논문 수준의 전문 보고서를 작성하세요.

## 보고서 구조 (반드시 아래 형식을 따르세요)

### 1. 실행 개요 (Executive Summary)
- 워크플로우명, 반복(iteration) 차수, 총 소요 시간, 사용 AI 모델
- 이번 사이클의 핵심 목표 및 달성 여부 한 줄 요약

### 2. 이온화 지질 설계 및 선정 (Ionizable Lipid Design)
- 선정된 후보 지질의 구조적 특성: 분자량(MW), LogP, TPSA, HBD/HBA
- 링커 타입(ester, disulfide 등)과 생분해성(biodegradability) 평가
- 탐색 공간(search space) 대비 선별 전략 (필터 조건, 샘플링 수)
- 다목적 최적화 점수: efficacy, stability, safety 및 Pareto rank

### 3. 합성 가능성 평가 (Synthetic Feasibility)
- 합성 조건 (온도, 반응시간, 용매, 촉매)
- 수율(yield) 및 순도(purity) — 일반적 기준: 수율>70%, 순도>95%
- QC 결과 (MS, NMR, HPLC 확인 여부)

### 4. LNP 제형 조성 분석 (Formulation Composition)
- 4성분 몰비: IL:HL:Chol:PEG (실제 수치 명시)
- FDA 승인 제형과 비교:
  · Onpattro (MC3): 50:10:38.5:1.5
  · Comirnaty (ALC-0315): 46.3:9.4:42.7:1.6
  · Spikevax (SM-102): 50:10:38.5:1.5
- N/P ratio 및 적정 범위(4-10) 대비 평가
- Helper lipid 선택 근거 (DSPC vs DOPE 등)
- 마이크로플루이딕 혼합 파라미터 (TFR, FRR)

### 5. 물리화학적 특성 평가 (Physicochemical Characterization)
각 측정값과 함께 판정 기준을 명시하세요:
| 항목 | 측정값 | 적정 범위 | 판정 |
|------|--------|----------|------|
| 입자 크기(Diameter) | nm | 60-150 nm | |
| 다분산 지수(PDI) | | <0.2 우수, <0.3 허용 | |
| 제타 전위(Zeta Potential) | mV | -30~-10 mV | |
| 캡슐화 효율(Encapsulation Efficiency) | % | >85% | |
- QC 통과 여부 및 종합 판정
- LNPDB 평균값 대비 비교 (벤치마크 데이터 제공 시)

### 6. 기능성 평가 (Functional Assay)
- 세포주, cargo 종류, 투여 용량
- 형광/발광 정규화 값(luminescence normalized) 및 DB 평균 대비 성능
- Transfection efficiency 해석

### 7. 구조-활성 관계 인사이트 (Structure-Activity Relationship)
- AI Feature importance 기반 핵심 descriptor 분석
  (예: LogP와 transfection 상관관계, MW와 입자 크기 관계)
- 이번 결과에서 도출된 SAR 가설

### 8. AI 모델 성능 및 학습 (Model Performance)
- R², RMSE 변화 (학습 전→후)
- 학습 데이터 수 증가
- 모델 개선율 및 수렴 추세

### 9. 차기 반복 권고사항 (Next Iteration Recommendations)
- 조성비 최적화 방향 (PDI>0.2이면 PEG 증량 등 구체적 수치)
- 지질 구조 변경 제안 (head group, tail 길이/분기)
- 실험 조건 변경 (N/P ratio, 혼합 속도 등)

### 10. 결론 (Conclusion)
- 전체 파이프라인 성공/실패 판정
- 약물 전달 시스템(DDS)으로서의 개발 가능성 평가
- 다음 단계 로드맵

## 작성 규칙
- 반드시 한국어(Korean)로만 작성하세요. 일본어, 중국어 등 다른 언어를 절대 사용하지 마세요.
- 전문 용어는 영문 병기하세요 (예: 입자 크기(Particle Size)).
- 모든 수치를 빠짐없이 포함하고, 적정 범위와 함께 판정(우수/양호/주의/부적합)을 명시하세요.
- 표(table)를 적극 활용하세요.
- 근거 없는 추측은 피하고, 제공된 데이터에 기반하여 작성하세요."""


def _collect_run_data(run):
    """Collect workflow run data for report generation."""
    lines = []
    lines.append("## 워크플로우 정보")
    lines.append(f"- 이름: {run.name}")
    lines.append(f"- 상태: {run.status}")
    lines.append(f"- 반복 차수: {run.iteration}")
    if run.ai_model:
        metrics_str = ""
        if run.ai_model.metrics:
            metrics_str = ", ".join(f"{k}={v}" for k, v in run.ai_model.metrics.items())
        lines.append(f"- AI 모델: {run.ai_model.name} v{run.ai_model.version} ({metrics_str})")
        lines.append(f"- 학습 데이터 수: {run.ai_model.training_data_count}")
    else:
        lines.append("- AI 모델: 미지정")
    lines.append(f"- 생성일: {run.created_at}")
    lines.append(f"- 완료일: {run.completed_at}")
    if run.created_at and run.completed_at:
        duration = run.completed_at - run.created_at
        hours, remainder = divmod(int(duration.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        lines.append(f"- 총 소요 시간: {hours}시간 {minutes}분 {seconds}초")

    lines.append("")
    lines.append("## 단계별 실행 결과")
    for step in run.steps.all().order_by("step_order"):
        lines.append(f"### Step {step.step_order}: {step.get_step_type_display()}")
        lines.append(f"- 상태: {step.status}")
        if step.started_at and step.completed_at:
            step_dur = step.completed_at - step.started_at
            lines.append(f"- 소요 시간: {step_dur}")
        if step.equipment:
            lines.append(f"- 장비: {step.equipment.name} ({step.equipment.equipment_type})")
        if step.output_data:
            lines.append(f"- 결과: {json.dumps(step.output_data, ensure_ascii=False)}")
        lines.append("")

    # FDA 승인 LNP 제형 벤치마크
    lines.append("## 참고: FDA 승인 LNP 제형 벤치마크")
    lines.append("| 제품명 | 이온화 지질 | IL:HL:Chol:PEG | 입자크기(nm) | PDI | 적응증 |")
    lines.append("|--------|-----------|---------------|-------------|-----|--------|")
    lines.append("| Onpattro | MC3 (DLin-MC3-DMA) | 50:10:38.5:1.5 | 60-100 | <0.1 | hATTR (siRNA) |")
    lines.append("| Comirnaty | ALC-0315 | 46.3:9.4:42.7:1.6 | ~80 | <0.2 | COVID-19 (mRNA) |")
    lines.append("| Spikevax | SM-102 | 50:10:38.5:1.5 | ~100 | <0.2 | COVID-19 (mRNA) |")
    lines.append("")

    # 물리화학적 특성 판정 기준
    lines.append("## 참고: LNP 물리화학적 특성 판정 기준")
    lines.append("| 항목 | 우수 | 양호 | 주의 | 부적합 |")
    lines.append("|------|------|------|------|--------|")
    lines.append("| 입자 크기(nm) | 60-100 | 100-150 | 150-200 | >200 |")
    lines.append("| PDI | <0.1 | 0.1-0.2 | 0.2-0.3 | >0.3 |")
    lines.append("| 제타 전위(mV) | -30~-20 | -20~-10 | -10~0 | >0 or <-40 |")
    lines.append("| 캡슐화 효율(%) | >95 | 85-95 | 75-85 | <75 |")
    lines.append("| N/P ratio | 4-8 | 8-10 | 10-15 | >15 |")
    lines.append("| 합성 수율(%) | >85 | 70-85 | 55-70 | <55 |")
    lines.append("| 합성 순도(%) | >98 | 95-98 | 90-95 | <90 |")

    return "\n".join(lines)


@login_required
@require_POST
def generate_report(request, pk):
    from workflow.models import WorkflowRun

    try:
        run = WorkflowRun.objects.select_related("ai_model").prefetch_related(
            "steps", "steps__equipment"
        ).get(pk=pk)
    except WorkflowRun.DoesNotExist:
        return JsonResponse({"error": "Workflow run not found"}, status=404)

    body = {}
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        pass
    regenerate = body.get("regenerate", False)

    if run.report_text and not regenerate:
        return JsonResponse({"report": run.report_text, "cached": True})

    api_key = settings.GROQ_API_KEY
    if not api_key:
        return JsonResponse({"error": "GROQ_API_KEY not configured"}, status=500)

    run_data = _collect_run_data(run)
    messages = [
        {"role": "system", "content": REPORT_SYSTEM_PROMPT},
        {"role": "user", "content": run_data},
    ]

    try:
        resp = http_requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.GROQ_MODEL,
                "messages": messages,
                "max_tokens": 4096,
                "temperature": 0.3,
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        report = data["choices"][0]["message"]["content"]
    except http_requests.exceptions.Timeout:
        return JsonResponse({"error": "API timeout"}, status=504)
    except http_requests.exceptions.RequestException as e:
        return JsonResponse({"error": f"API error: {str(e)}"}, status=502)
    except (KeyError, IndexError):
        return JsonResponse({"error": "Unexpected API response"}, status=502)

    run.report_text = report
    run.save(update_fields=["report_text"])

    return JsonResponse({"report": report, "cached": False})


@login_required
@require_POST
def chat_api(request):
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    message = body.get("message", "").strip()
    if not message:
        return JsonResponse({"error": "Empty message"}, status=400)

    page_context = body.get("page_context", "dashboard")
    history = body.get("history", [])
    screen_data = body.get("screen_data", "")

    page_detail = PAGE_CONTEXT.get(page_context, "일반 페이지입니다.")
    page_label = page_context.replace("_", " ").title()

    db_data = _get_db_data(page_context)

    screen_data_section = ""
    if screen_data:
        screen_data_section = f"## 현재 화면에 표시된 데이터\n{screen_data[:3000]}\n\n"

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        page_label=page_label,
        page_detail=page_detail,
        db_data=db_data,
        screen_data_section=screen_data_section,
    )

    messages = [{"role": "system", "content": system_prompt}]
    for h in history[-20:]:
        role = h.get("role")
        content = h.get("content", "")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": message})

    api_key = settings.GROQ_API_KEY
    if not api_key:
        return JsonResponse({"error": "GROQ_API_KEY not configured"}, status=500)

    try:
        resp = http_requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.GROQ_MODEL,
                "messages": messages,
                "max_tokens": 1024,
                "temperature": 0.7,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        reply = data["choices"][0]["message"]["content"]
        return JsonResponse({"reply": reply})
    except http_requests.exceptions.Timeout:
        return JsonResponse({"error": "API timeout"}, status=504)
    except http_requests.exceptions.RequestException as e:
        return JsonResponse({"error": f"API error: {str(e)}"}, status=502)
    except (KeyError, IndexError):
        return JsonResponse({"error": "Unexpected API response"}, status=502)
