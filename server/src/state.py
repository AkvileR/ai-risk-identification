from typing import TypedDict, Dict, Optional, Annotated, Set, Literal
from .constants import ActivePhase, ExclusionType, RiskTier, Role
import operator

class SystemDescription(TypedDict):
    raw_input: str
    role: Role
    is_gpai: bool
    in_eu_scope: bool
    exclusions: list[ExclusionType]

class CriterionFinding(TypedDict):
    criterion_id: str
    article_ref: str
    question: str
    applies: Literal["yes", "no", "uncertain"]
    confidence_score: float
    reasoning: str
    clarification_question: Optional[str]
    clarification_round_count: int
    extracted_value: Optional[dict]

class Verdict(TypedDict):
    role: Role
    detected_role: Role
    risk_tier: RiskTier
    tier_reasoning: str
    is_gpai: bool
    is_gpai_systemic: bool
    exclusions: list[ExclusionType]
    applicable_findings: list[CriterionFinding]
    non_applicable_findings: list[CriterionFinding]
    uncertain_findings: list[CriterionFinding]
    article_citations: list[str]

def _last_phase(_old: ActivePhase, new: ActivePhase) -> ActivePhase:
    return new

class State(TypedDict):
    user_input: str
    system_description: Optional[SystemDescription]
    criterion_findings: Annotated[Dict[str, CriterionFinding], operator.ior]
    active_phase: Annotated[ActivePhase, _last_phase]
    pending_assessments: Set[str]
    verdict: Optional[Verdict]
