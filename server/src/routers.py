from src.constants import ART2_PROVIDER_SCOPE_IDS, IDENTIFICATION_CRITERION_IDS, MAX_CLARIFICATION_ROUNDS
from src.state import State

def _is_pending(f: dict) -> bool:
    return (
        f.get("applies") == "uncertain"
        and f.get("clarification_round_count", 0) < MAX_CLARIFICATION_ROUNDS
    )

def _has_pending_identification_clarification(findings: dict) -> bool:
    return any(
        cid in IDENTIFICATION_CRITERION_IDS and _is_pending(f)
        for cid, f in findings.items()
    )

def _has_pending_assessment_clarification(findings: dict) -> bool:
    return any(
        (cid not in IDENTIFICATION_CRITERION_IDS or cid in ART2_PROVIDER_SCOPE_IDS)
        and _is_pending(f)
        for cid, f in findings.items()
    )

def criterion_assess_router(state: State) -> str:
    findings = state.get("criterion_findings") or {}
    if state.get("system_description") is not None:
        if _has_pending_assessment_clarification(findings):
            return "clarification"
        return "assessment_planner"
    if _has_pending_identification_clarification(findings):
        return "clarification"
    return "identify_planner"
