from typing import Optional

from langgraph.types import Command, Send

from src.ai_client import (
    query_gemini_for_assessment,
    query_gemini_for_exclusions,
    query_gemini_for_role,
)
from src.constants import (
    ART2_EXCLUSION_TYPES,
    ART2_SCOPE_CRITERION_IDS,
    ASSESSMENT_CONFIDENCE_THRESHOLD,
    ASSESSMENT_PROMPT_LEGEND,
    ActivePhase,
    AssessmentCriterion,
    EXCLUSIONS_PROMPT_LEGEND,
    ExclusionType,
    GPAI_FLAG_CRITERION_ID,
    IDENTIFY_SYSTEM_PROMPT_TEMPLATE,
    LETTER_TO_ROLE,
    LETTER_TO_VERDICT,
    RAG_ENABLED,
    ROLE_PROMPT_LEGEND,
    Role,
)
from src.criteria import CRITERIA_BY_ID
from src.rag import format_chunks_block, retrieve_for_criterion
from src.state import CriterionFinding, State, SystemDescription

def _context_block(cid: str, sibling_findings: dict[str, CriterionFinding]) -> str:
    parts = []
    role_value = ((sibling_findings.get("art3_entity_role") or {}).get("extracted_value") or {}).get("role")
    if cid != "art3_entity_role" and role_value:
        parts.append(f"role (from E1): {role_value}")
    if cid == "art2_exclusions":
        gpai_finding = sibling_findings.get(GPAI_FLAG_CRITERION_ID) or {}
        if gpai_finding.get("applies") == "yes":
            parts.append("is GPAI (from S): True")
    return "\n".join(parts) + "\n" if parts else ""

def _sibling_context_for(cid: str, findings: dict[str, CriterionFinding]) -> dict[str, CriterionFinding]:
    siblings: dict[str, CriterionFinding] = {}
    e1 = findings.get("art3_entity_role")
    if e1 is not None and cid != "art3_entity_role":
        siblings["art3_entity_role"] = e1
    if cid == "art2_exclusions":
        gpai = findings.get(GPAI_FLAG_CRITERION_ID)
        if gpai is not None:
            siblings[GPAI_FLAG_CRITERION_ID] = gpai
    return siblings

def _build_prompt(
    cid: str,
    criterion: AssessmentCriterion,
    description: str,
    prior_text: str,
    sibling_findings: dict[str, CriterionFinding],
    schema_name: str,
    schema_legend: str,
) -> str:
    chunks = retrieve_for_criterion(criterion) if RAG_ENABLED else []
    rag_block = format_chunks_block(chunks)
    rag_clause = " or RELEVANT AI ACT TEXT" if rag_block else ""
    return IDENTIFY_SYSTEM_PROMPT_TEMPLATE.format(
        rag_clause=rag_clause,
        rag_block=rag_block,
        criterion_id=cid,
        article_ref=criterion["article_ref"],
        question=criterion["question"],
        description=description,
        context_block=_context_block(cid, sibling_findings),
        prior_clarifications=prior_text or "(none)",
        schema_name=schema_name,
        schema_legend=schema_legend,
    )

def _evaluate_role(prompt: str) -> tuple[str, float, str, dict]:
    parsed, softmax = query_gemini_for_role(prompt)
    role = LETTER_TO_ROLE[parsed.role]
    confidence = softmax[parsed.role] if softmax is not None else 0.0
    applies = "yes" if confidence >= ASSESSMENT_CONFIDENCE_THRESHOLD else "uncertain"
    return applies, confidence, parsed.reasoning, {"role": role}

def _evaluate_exclusions(prompt: str) -> tuple[str, float, str, dict]:
    parsed, softmax_per = query_gemini_for_exclusions(prompt)
    exclusions: list[ExclusionType] = [
        e for e in ART2_EXCLUSION_TYPES if getattr(parsed, e.value) == "Y"
    ]
    if softmax_per is None:
        return "uncertain", 0.0, parsed.reasoning, {"exclusions": exclusions}
    confidence = min(
        softmax_per[e][getattr(parsed, e.value)] for e in ART2_EXCLUSION_TYPES
    )
    applies = "yes" if confidence >= ASSESSMENT_CONFIDENCE_THRESHOLD else "uncertain"
    return applies, confidence, parsed.reasoning, {"exclusions": exclusions}

def _evaluate_s1(prompt: str) -> tuple[str, float, str, dict]:
    parsed, softmax = query_gemini_for_assessment(prompt)
    if softmax is None:
        applies = "uncertain"
        confidence = 0.0
    else:
        applies = LETTER_TO_VERDICT[parsed.applies]
        confidence = softmax[parsed.applies]
        if confidence < ASSESSMENT_CONFIDENCE_THRESHOLD:
            applies = "uncertain"
    return applies, confidence, parsed.reasoning, {"applies": applies}

def _evaluate(
    cid: str,
    user_input: str,
    sibling_findings: dict[str, CriterionFinding],
    prior_finding: Optional[CriterionFinding],
) -> CriterionFinding:
    criterion = CRITERIA_BY_ID[cid]
    history = (prior_finding or {}).get("clarification_history") or []
    prior_text = "\n".join(
        f"- Q: {e['question']}\n  A: {e['answer']}"
        for e in history
    )

    if cid == "art3_entity_role":
        schema_name, legend, evaluator = "EntityTypeResponse", ROLE_PROMPT_LEGEND, _evaluate_role
    elif cid == "art2_exclusions":
        schema_name, legend, evaluator = "ExclusionsResponse", EXCLUSIONS_PROMPT_LEGEND, _evaluate_exclusions
    else:
        schema_name, legend, evaluator = "CriterionAssessmentResponse", ASSESSMENT_PROMPT_LEGEND, _evaluate_s1

    prompt = _build_prompt(cid, criterion, user_input, prior_text, sibling_findings, schema_name, legend)
    applies, confidence, reasoning, extracted_value = evaluator(prompt)
    prior_rounds = (prior_finding or {}).get("clarification_round_count", 0)
    return {
        "criterion_id": cid,
        "article_ref": criterion["article_ref"],
        "question": criterion["question"],
        "applies": applies,
        "confidence_score": confidence,
        "reasoning": reasoning,
        "clarification_history": history,
        "clarification_round_count": prior_rounds,
        "extracted_value": extracted_value,
    }

def _s1_ids_for_role(role: Role) -> list[str]:
    return [
        cid for cid in ART2_SCOPE_CRITERION_IDS
        if role in CRITERIA_BY_ID[cid]["applies_to_roles"]
    ]

def _detected_role(findings: dict[str, CriterionFinding]) -> Optional[Role]:
    e1 = findings.get("art3_entity_role")
    if e1 is None:
        return None
    role = ((e1.get("extracted_value") or {}).get("role"))
    return role if isinstance(role, Role) else (Role(role) if role else None)

def _next_wave_pending(
    findings: dict[str, CriterionFinding],
) -> tuple[Optional[Role], list[str]]:
    if "art3_entity_role" not in findings:
        return None, ["art3_entity_role"]
    role = _detected_role(findings)
    if role == Role.AUTHORISED_REPRESENTATIVE:
        return role, []
    if role is not None:
        s1_pending = [cid for cid in _s1_ids_for_role(role) if cid not in findings]
        if s1_pending:
            return role, s1_pending
    if "art2_exclusions" not in findings:
        return role, ["art2_exclusions"]
    return role, []

def _compose_system_description(
    user_input: str,
    findings: dict[str, CriterionFinding],
) -> SystemDescription:
    e1 = (findings.get("art3_entity_role") or {}).get("extracted_value") or {}
    role: Role = e1.get("role") or Role.DEPLOYER
    r2 = (findings.get("art2_exclusions") or {}).get("extracted_value") or {}

    gpai_finding = findings.get(GPAI_FLAG_CRITERION_ID)
    is_gpai = gpai_finding is not None and gpai_finding.get("applies") == "yes"

    s1_for_role = _s1_ids_for_role(role)
    if s1_for_role:
        in_eu_scope = any(
            (findings.get(cid) or {}).get("applies") == "yes"
            for cid in s1_for_role
        )
    else:
        in_eu_scope = True

    return {
        "raw_input": user_input,
        "role": role,
        "is_gpai": is_gpai,
        "in_eu_scope": in_eu_scope,
        "exclusions": list(r2.get("exclusions") or []),
    }

def _build_wave_sends(
    pending: list[str],
    user_input: str,
    findings: dict[str, CriterionFinding],
) -> list[Send]:
    return [
        Send("criterion_assess", {
            "criterion_id": cid,
            "user_input": user_input,
            "sibling_findings": _sibling_context_for(cid, findings),
            "prior_finding": findings.get(cid),
        })
        for cid in pending
    ]

def identify_planner(state: State):
    findings = state.get("criterion_findings") or {}
    user_input = state.get("user_input", "")
    _, pending = _next_wave_pending(findings)
    if pending:
        return Command(
            update={"active_phase": ActivePhase.DEFINING_SYSTEM},
            goto=_build_wave_sends(pending, user_input, findings),
        )
    sd = _compose_system_description(user_input, findings)
    return Command(
        update={"system_description": sd, "active_phase": ActivePhase.DEFINING_SYSTEM},
        goto="assessment_planner",
    )

