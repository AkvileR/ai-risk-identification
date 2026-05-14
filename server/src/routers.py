from src.constants import ART2_PROVIDER_SCOPE_IDS, IDENTIFICATION_CRITERION_IDS, MAX_CLARIFICATION_ROUNDS
from src.state import State

def _has_pending_identification_clarification(findings: dict) -> bool:
    return any(
        cid in IDENTIFICATION_CRITERION_IDS
        and f.get("clarification_question")
        and f.get("clarification_round_count", 0) < MAX_CLARIFICATION_ROUNDS
        for cid, f in findings.items()
    )

def _has_pending_assessment_clarification(findings: dict) -> bool:
    return any(
        (cid not in IDENTIFICATION_CRITERION_IDS or cid in ART2_PROVIDER_SCOPE_IDS)
        and f.get("applies") == "uncertain"
        and f.get("clarification_question")
        and f.get("clarification_round_count", 0) < MAX_CLARIFICATION_ROUNDS
        for cid, f in findings.items()
    )

def identify_router(state: State) -> str:
    findings = state.get("criterion_findings") or {}
    if _has_pending_identification_clarification(findings):
        return "clarification"
    if state.get("system_description") is not None:
        return "assessment_planner"
    return "identify_system"

def assessment_router(state: State) -> str:
    findings = state.get("criterion_findings") or {}
    if _has_pending_assessment_clarification(findings):
        return "clarification"
    return "assessment_planner"
