from langgraph.types import Command, Send

from src.constants import (
    ART2_PROVIDER_SCOPE_IDS,
    ART2_SCOPE_CRITERION_IDS,
    CRITERION_MAX_CONCURRENCY,
    GATE_CRITERION_IDS,
    GPAI_FLAG_CRITERION_ID,
    IDENTIFICATION_CRITERION_IDS,
    ActivePhase,
    AssessmentCriterion,
    Role,
)
from src.criteria import CRITERIA, CRITERIA_BY_ID
from src.state import CriterionFinding, State, SystemDescription
from src.synthesis_utils import derive_role, is_role_changing_article

def _is_relevant_to_system(criterion: AssessmentCriterion, sd: SystemDescription) -> bool:
    art = criterion["article_ref"]
    if art.startswith("Art. 51") and not sd["is_gpai"]:
        return False
    return True

def _high_risk_pending_for_role(role: Role, sd: SystemDescription) -> set[str]:
    return {
        c["id"]
        for c in CRITERIA
        if c["id"] not in IDENTIFICATION_CRITERION_IDS
        and c["id"] not in GATE_CRITERION_IDS
        and is_role_changing_article(c["article_ref"])
        and role in c["applies_to_roles"]
        and _is_relevant_to_system(c, sd)
    }

def _remaining_pending(
    derived_role: Role,
    sd: SystemDescription,
    findings: dict[str, CriterionFinding],
) -> set[str]:
    return {
        c["id"]
        for c in CRITERIA
        if c["id"] not in IDENTIFICATION_CRITERION_IDS
        and c["id"] not in GATE_CRITERION_IDS
        and derived_role in c["applies_to_roles"]
        and c["id"] not in findings
        and _is_relevant_to_system(c, sd)
    }

def _gate_pending_for_role(
    role: Role,
    findings: dict[str, CriterionFinding],
) -> set[str]:
    pending: set[str] = set()
    if "art6_third_party_conformity_assessment_required" not in findings and any(
        f.get("applies") == "yes" and f["article_ref"].startswith("Annex I §A")
        for f in findings.values()
    ):
        criterion = CRITERIA_BY_ID["art6_third_party_conformity_assessment_required"]
        if role in criterion["applies_to_roles"]:
            pending.add("art6_third_party_conformity_assessment_required")
    if "art6_significant_risk" not in findings and any(
        f.get("applies") == "yes" and f["article_ref"].startswith("Annex III")
        for f in findings.values()
    ):
        criterion = CRITERIA_BY_ID["art6_significant_risk"]
        if role in criterion["applies_to_roles"]:
            pending.add("art6_significant_risk")
    return pending

def _plan_product_manufacturer(
    sd: SystemDescription,
    findings: dict[str, CriterionFinding],
) -> dict:
    e3 = findings.get("art25_3_pm_integrates_ai")
    if e3 is None:
        return {"pending_assessments": {"art25_3_pm_integrates_ai"}}
    if e3["applies"] != "yes":
        return {"pending_assessments": set()}

    section_a_ids = {
        c["id"]
        for c in CRITERIA
        if c["article_ref"].startswith("Annex I §A")
        and Role.PRODUCT_MANUFACTURER in c["applies_to_roles"]
        and _is_relevant_to_system(c, sd)
    }
    unevaluated = section_a_ids - set(findings.keys())
    if unevaluated:
        return {"pending_assessments": unevaluated}

    gate_pending = _gate_pending_for_role(Role.PRODUCT_MANUFACTURER, findings)
    if gate_pending:
        return {"pending_assessments": gate_pending}

    derived = derive_role(Role.PRODUCT_MANUFACTURER, findings)
    if derived != Role.PROVIDER:
        return {"pending_assessments": set()}
    remaining = _remaining_pending(Role.PROVIDER, sd, findings)
    if remaining:
        return {"pending_assessments": remaining}
    return {"pending_assessments": _gate_pending_for_role(Role.PROVIDER, findings)}

def _plan_for_any(
    role: Role,
    sd: SystemDescription,
    findings: dict[str, CriterionFinding],
) -> dict:
    high_risk = _high_risk_pending_for_role(role, sd)
    unevaluated = high_risk - set(findings.keys())
    if unevaluated:
        return {"pending_assessments": unevaluated}
    gate_pending = _gate_pending_for_role(role, findings)
    if gate_pending:
        return {"pending_assessments": gate_pending}
    derived = derive_role(role, findings)
    remaining = _remaining_pending(derived, sd, findings)
    if remaining:
        return {"pending_assessments": remaining}
    return {"pending_assessments": _gate_pending_for_role(derived, findings)}

def _plan_provider(
    sd: SystemDescription,
    findings: dict[str, CriterionFinding],
) -> dict:
    remaining = _remaining_pending(Role.PROVIDER, sd, findings)
    if remaining:
        return {"pending_assessments": remaining}
    return {"pending_assessments": _gate_pending_for_role(Role.PROVIDER, findings)}

def _build_sends(pending: set[str], sd: SystemDescription) -> list[Send]:
    return [
        Send("criterion_assess", {
            "criterion_id": cid,
            "system_description": sd,
            "prior_finding": None,
        })
        for cid in sorted(pending)
    ]

def _provider_backfill_pending(findings: dict[str, CriterionFinding]) -> set[str]:
    return ART2_PROVIDER_SCOPE_IDS - set(findings.keys())

def _refresh_scope_flags(
    sd: SystemDescription,
    findings: dict[str, CriterionFinding],
) -> SystemDescription:
    gpai = findings.get(GPAI_FLAG_CRITERION_ID)
    is_gpai = gpai is not None and gpai.get("applies") == "yes"
    provider_s1 = [
        c["id"] for c in CRITERIA
        if c["id"] in ART2_SCOPE_CRITERION_IDS and Role.PROVIDER in c["applies_to_roles"]
    ]
    placed_in_eu = any(
        (findings.get(cid) or {}).get("applies") == "yes" for cid in provider_s1
    )
    return {**sd, "is_gpai": is_gpai, "in_eu_scope": sd["in_eu_scope"] or placed_in_eu}

def assessment_planner(state: State):
    sd = state["system_description"]
    role = sd["role"]

    if not sd["in_eu_scope"] or role == Role.AUTHORISED_REPRESENTATIVE:
        return Command(
            update={"pending_assessments": set(), "active_phase": ActivePhase.EVALUATING_CRITERIA},
            goto="synthesis",
        )

    findings = state.get("criterion_findings") or {}
    if role == Role.PRODUCT_MANUFACTURER:
        plan = _plan_product_manufacturer(sd, findings)
    elif role == Role.PROVIDER:
        plan = _plan_provider(sd, findings)
    else:
        plan = _plan_for_any(role, sd, findings)

    sd_updates: dict = {}
    if role != Role.PROVIDER and derive_role(role, findings) == Role.PROVIDER:
        backfill_pending = _provider_backfill_pending(findings)
        if backfill_pending:
            updates = {
                "pending_assessments": backfill_pending,
                "active_phase": ActivePhase.EVALUATING_CRITERIA,
            }
            batch = sorted(backfill_pending)[:CRITERION_MAX_CONCURRENCY]
            return Command(update=updates, goto=_build_sends(set(batch), sd))
        refreshed_sd = _refresh_scope_flags(sd, findings)
        if refreshed_sd != sd:
            sd_updates["system_description"] = refreshed_sd
            sd = refreshed_sd
            if not sd["in_eu_scope"]:
                return Command(
                    update={
                        **sd_updates,
                        "pending_assessments": set(),
                        "active_phase": ActivePhase.EVALUATING_CRITERIA,
                    },
                    goto="synthesis",
                )
            plan = _plan_provider(sd, findings)

    remaining = set(plan["pending_assessments"]) - set(findings.keys())
    updates = {**sd_updates, "pending_assessments": remaining, "active_phase": ActivePhase.EVALUATING_CRITERIA}

    batch = sorted(remaining)[:CRITERION_MAX_CONCURRENCY]
    if batch:
        return Command(update=updates, goto=_build_sends(set(batch), sd))
    return Command(update=updates, goto="synthesis")
