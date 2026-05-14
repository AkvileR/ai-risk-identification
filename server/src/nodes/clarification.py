from langgraph.types import Command, Send, interrupt

from src.constants import ART2_PROVIDER_SCOPE_IDS, ActivePhase, IDENTIFICATION_CRITERION_IDS, MAX_CLARIFICATION_ROUNDS
from src.nodes.identify_system import _sibling_context_for
from src.state import CriterionFinding, State

def clarification(state: State):
    findings = state.get("criterion_findings") or {}
    sd_set = state.get("system_description") is not None

    if not sd_set:
        pending = [
            cid for cid, f in findings.items()
            if cid in IDENTIFICATION_CRITERION_IDS
            and f.get("clarification_question")
            and f.get("clarification_round_count", 0) < MAX_CLARIFICATION_ROUNDS
        ]
        if pending:
            return _handle_batch(state, pending, target="identify_system")
        return Command(update={"active_phase": ActivePhase.ASKING_CLARIFICATION}, goto="identify_system")

    pending = [
        cid for cid, f in findings.items()
        if (cid not in IDENTIFICATION_CRITERION_IDS or cid in ART2_PROVIDER_SCOPE_IDS)
        and f.get("applies") == "uncertain"
        and f.get("clarification_question")
        and f.get("clarification_round_count", 0) < MAX_CLARIFICATION_ROUNDS
    ]
    if pending:
        return _handle_batch(state, pending, target="criterion_assess")
    return Command(update={"active_phase": ActivePhase.ASKING_CLARIFICATION}, goto="assessment_planner")

def _build_send(
    target: str,
    cid: str,
    prior: CriterionFinding,
    state: State,
    findings: dict[str, CriterionFinding],
) -> Send:
    if target == "identify_system":
        return Send("identify_system", {
            "criterion_id": cid,
            "user_input": state.get("user_input", ""),
            "sibling_findings": _sibling_context_for(cid, findings),
            "prior_finding": prior,
        })
    return Send("criterion_assess", {
        "criterion_id": cid,
        "system_description": state.get("system_description"),
        "prior_finding": prior,
    })

def _handle_batch(state: State, pending: list[str], target: str):
    findings = dict(state.get("criterion_findings") or {})

    questions = [
        {
            "criterion_id": cid,
            "article_ref": (findings.get(cid) or {}).get("article_ref"),
            "question": (findings.get(cid) or {}).get("clarification_question"),
        }
        for cid in pending
    ]

    answers = interrupt({"kind": "criterion_clarifications", "questions": questions}) or {}

    updated: dict[str, CriterionFinding] = {}
    re_sends: list[Send] = []
    for cid in pending:
        answer = (answers.get(cid) or "").strip()
        prior = dict(findings[cid])
        if not answer:
            prior["clarification_question"] = None
            updated[cid] = prior
            continue
        reasoning = prior.get("reasoning", "") or ""
        prior["reasoning"] = f"{reasoning}\n\nYour clarification: {answer}".strip()
        prior["clarification_question"] = None
        prior["clarification_round_count"] = prior.get("clarification_round_count", 0) + 1
        updated[cid] = prior
        re_sends.append(_build_send(target, cid, prior, state, {**findings, **updated}))

    if not re_sends:
        fallback = "identify_system" if target == "identify_system" else "assessment_planner"
        update = {"active_phase": ActivePhase.ASKING_CLARIFICATION}
        if updated:
            update["criterion_findings"] = updated
        return Command(update=update, goto=fallback)

    return Command(
        update={"criterion_findings": updated, "active_phase": ActivePhase.ASKING_CLARIFICATION},
        goto=re_sends,
    )
