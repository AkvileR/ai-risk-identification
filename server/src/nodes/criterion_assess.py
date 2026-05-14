from typing import Optional
from src.ai_client import query_gemini_for_assessment
from src.constants import (
    ASSESSMENT_CONFIDENCE_THRESHOLD,
    ASSESSMENT_PROMPT_TEMPLATE,
    LETTER_TO_VERDICT,
    RAG_ENABLED,
)
from src.criteria import CRITERIA_BY_ID
from src.rag import retrieve_for_criterion
from src.state import CriterionFinding, SystemDescription

def _format_chunks(chunks) -> str:
    if not chunks:
        return ""
    lines = ["", "RELEVANT AI ACT TEXT (retrieved):"]
    for c in chunks:
        heading = c["article_ref"]
        if c.get("title"):
            heading = f"{heading} -- {c['title']}"
        lines.append(f"  [{heading}]")
        lines.append(f"  {c['text']}")
    return "\n".join(lines) + "\n"

def _build_prompt(
    question_id: str,
    question_text: str,
    article_ref: str,
    sd: SystemDescription,
    chunks,
    prior_finding: Optional[CriterionFinding],
) -> str:
    rag_block = _format_chunks(chunks)
    rag_clause = " or RELEVANT AI ACT TEXT" if rag_block else ""
    prior_text = ""
    if prior_finding:
        prior_text = prior_finding.get("reasoning") or ""
    return ASSESSMENT_PROMPT_TEMPLATE.format(
        rag_clause=rag_clause,
        rag_block=rag_block,
        criterion_id=question_id,
        article_ref=article_ref,
        question=question_text,
        raw_input=sd.get("raw_input", ""),
        role=sd.get("role", ""),
        is_gpai=sd.get("is_gpai", False),
        prior_clarifications=prior_text or "(none)",
    )

def _evaluate_question(
    question_id: str,
    question_text: str,
    article_ref: str,
    sd: SystemDescription,
    chunks,
    prior_finding: Optional[CriterionFinding],
) -> CriterionFinding:
    prompt = _build_prompt(question_id, question_text, article_ref, sd, chunks, prior_finding)
    parsed, softmax = query_gemini_for_assessment(prompt)
    if softmax is None:
        applies = "uncertain"
        confidence_score = 0.0
    else:
        applies = LETTER_TO_VERDICT[parsed.applies]
        confidence_score = softmax[parsed.applies]
        if confidence_score < ASSESSMENT_CONFIDENCE_THRESHOLD:
            applies = "uncertain"
    prior_rounds = (prior_finding or {}).get("clarification_round_count", 0)
    return {
        "criterion_id": question_id,
        "article_ref": article_ref,
        "question": question_text,
        "applies": applies,
        "confidence_score": confidence_score,
        "reasoning": parsed.reasoning,
        "clarification_question": parsed.clarification_question,
        "clarification_round_count": prior_rounds,
        "extracted_value": None,
    }

def criterion_assess(task: dict):
    criterion_id: str = task["criterion_id"]
    sd: SystemDescription = task["system_description"]
    prior: Optional[CriterionFinding] = task.get("prior_finding")

    criterion = CRITERIA_BY_ID[criterion_id]
    chunks = retrieve_for_criterion(criterion) if RAG_ENABLED else []
    finding = _evaluate_question(
        criterion["id"],
        criterion["question"],
        criterion["article_ref"],
        sd,
        chunks,
        prior,
    )
    return {
        "criterion_findings": {criterion_id: finding},
    }
