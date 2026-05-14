from langgraph.types import Command, Send, interrupt

from src.ai_client import (
    query_gemini_for_ambiguity_batch,
    query_gemini_for_clarification_generation,
)
from src.constants import (
    AMBIGUITY_CLASSIFICATION_PROMPT_TEMPLATE,
    ART2_PROVIDER_SCOPE_IDS,
    AT_CLARIFICATION_ACTIONS,
    AT_DEFINITIONS,
    ActivePhase,
    AmbiguityType,
    CLARIFICATION_GENERATION_PROMPT_TEMPLATE,
    IDENTIFICATION_CRITERION_IDS,
    MAX_CLARIFICATION_ROUNDS,
    RAG_ENABLED,
)
from src.criteria import CRITERIA_BY_ID
from src.nodes.identify_system import _sibling_context_for
from src.rag import format_chunks_block, retrieve_for_criterion
from src.state import CriterionFinding, State

def clarification(state: State):
    findings = state.get("criterion_findings") or {}
    sd_set = state.get("system_description") is not None

    if not sd_set:
        pending = [
            cid for cid, f in findings.items()
            if cid in IDENTIFICATION_CRITERION_IDS
            and f.get("applies") == "uncertain"
            and f.get("clarification_round_count", 0) < MAX_CLARIFICATION_ROUNDS
        ]
        if pending:
            return _handle_batch(state, pending)
        return Command(update={"active_phase": ActivePhase.ASKING_CLARIFICATION}, goto="identify_planner")

    pending = [
        cid for cid, f in findings.items()
        if (cid not in IDENTIFICATION_CRITERION_IDS or cid in ART2_PROVIDER_SCOPE_IDS)
        and f.get("applies") == "uncertain"
        and f.get("clarification_round_count", 0) < MAX_CLARIFICATION_ROUNDS
    ]
    if pending:
        return _handle_batch(state, pending)
    return Command(update={"active_phase": ActivePhase.ASKING_CLARIFICATION}, goto="assessment_planner")

def _build_send(
    cid: str,
    prior: CriterionFinding,
    state: State,
    findings: dict[str, CriterionFinding],
) -> Send:
    if state.get("system_description") is None:
        return Send("criterion_assess", {
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

def _description_for(state: State) -> str:
    sd = state.get("system_description")
    if sd is not None:
        return sd.get("raw_input", "") or ""
    return state.get("user_input", "") or ""

def _criteria_block(pending: list[str], findings: dict[str, CriterionFinding]) -> str:
    lines: list[str] = []
    for cid in pending:
        f = findings.get(cid) or {}
        lines.append(f"- criterion_id: {cid}")
        lines.append(f"  article_ref: {f.get('article_ref', '')}")
        lines.append(f"  question: {f.get('question', '')}")
        lines.append(
            f"  prior assessment: applies={f.get('applies', '')}; reasoning={f.get('reasoning', '')}"
        )
    return "\n".join(lines)

def _clarification_criteria_block(
    pending: list[str],
    findings: dict[str, CriterionFinding],
    at_by_cid: dict[str, AmbiguityType],
) -> str:
    lines: list[str] = []
    for cid in pending:
        f = findings.get(cid) or {}
        at = at_by_cid[cid]
        criterion = CRITERIA_BY_ID.get(cid)
        chunks = retrieve_for_criterion(criterion) if (RAG_ENABLED and criterion is not None) else []
        rag_block = format_chunks_block(chunks)
        history = f.get("clarification_history") or []
        prior_text = "\n".join(
            f"    - Q: {e['question']}\n      A: {e['answer']}"
            for e in history
        ) or "    (none)"
        lines.append(f"- criterion_id: {cid}")
        lines.append(f"  article_ref: {f.get('article_ref', '')}")
        lines.append(f"  info_target: {f.get('question', '')}")
        lines.append(f"  ambiguity_type: {at.value}")
        lines.append(f"  action: {AT_CLARIFICATION_ACTIONS[at]}")
        lines.append(f"  prior_uncertain_reasoning: {f.get('reasoning', '')}")
        lines.append("  prior_clarifications:")
        lines.append(prior_text)
        if rag_block:
            lines.append(rag_block.rstrip())
    return "\n".join(lines)

def _classify_ambiguity(
    state: State, pending: list[str], findings: dict[str, CriterionFinding]
) -> dict[str, AmbiguityType]:
    prompt = AMBIGUITY_CLASSIFICATION_PROMPT_TEMPLATE.format(
        at_definitions=AT_DEFINITIONS,
        description=_description_for(state),
        criteria_block=_criteria_block(pending, findings),
    )
    response = query_gemini_for_ambiguity_batch(prompt)
    by_cid = {c.criterion_id: c.ambiguity_type for c in response.classifications}
    return {cid: by_cid.get(cid, AmbiguityType.UNDERSPECIFIED) for cid in pending}

def _generate_clarifications(
    state: State,
    pending: list[str],
    findings: dict[str, CriterionFinding],
    at_by_cid: dict[str, AmbiguityType],
) -> dict[str, str]:
    prompt = CLARIFICATION_GENERATION_PROMPT_TEMPLATE.format(
        description=_description_for(state),
        criteria_block=_clarification_criteria_block(pending, findings, at_by_cid),
    )
    response = query_gemini_for_clarification_generation(prompt)
    by_cid = {c.criterion_id: c.question for c in response.clarifications}
    return {
        cid: (by_cid.get(cid) or (findings.get(cid) or {}).get("question", ""))
        for cid in pending
    }

def _handle_batch(state: State, pending: list[str]):
    findings = dict(state.get("criterion_findings") or {})

    at_by_cid = _classify_ambiguity(state, pending, findings)
    q_by_cid = _generate_clarifications(state, pending, findings, at_by_cid)

    questions = [
        {
            "criterion_id": cid,
            "article_ref": (findings.get(cid) or {}).get("article_ref"),
            "ambiguity_type": at_by_cid[cid],
            "question": q_by_cid[cid],
        }
        for cid in pending
    ]

    answers = interrupt({"kind": "criterion_clarifications", "questions": questions}) or {}

    rendered_q_by_cid = {q["criterion_id"]: q["question"] for q in questions}
    updated: dict[str, CriterionFinding] = {}
    re_sends: list[Send] = []
    for cid in pending:
        answer = (answers.get(cid) or "").strip()
        prior = dict(findings[cid])
        prior["clarification_round_count"] = prior.get("clarification_round_count", 0) + 1
        if answer:
            exchange = {"question": rendered_q_by_cid[cid], "answer": answer}
            prior["clarification_history"] = list(prior.get("clarification_history") or []) + [exchange]
            re_sends.append(_build_send(cid, prior, state, {**findings, cid: prior}))
        else:
            updated[cid] = prior

    update: dict = {"active_phase": ActivePhase.ASKING_CLARIFICATION}
    if updated:
        update["criterion_findings"] = updated

    if re_sends:
        return Command(update=update, goto=re_sends)
    fallback = "assessment_planner" if state.get("system_description") is not None else "identify_planner"
    return Command(update=update, goto=fallback)
