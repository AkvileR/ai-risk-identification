from typing import Final, TypedDict
from enum import StrEnum

ASSESSMENT_CONFIDENCE_THRESHOLD: Final = 0.85

RAG_ENABLED: Final = True

GEMINI_MODEL: Final = "gemini-2.5-flash"
ASSESSMENT_TEMPERATURE: Final = 0.0
MAX_CLARIFICATION_ROUNDS: Final = 2
LOGPROB_RETRY_LIMIT: Final = 3
LOGPROB_TEMPERATURE: Final = 4.5
LOGPROB_TOP_K: Final = 5
MAX_VALUE_TOKEN_WINDOW: Final = 5
ANSWER_TOKENS: Final[frozenset[str]] = frozenset({"Y", "N", "U"})
APPLIES_MARKER: Final = '"applies":'
LETTER_TO_VERDICT: Final[dict[str, str]] = {"Y": "yes", "N": "no", "U": "uncertain"}
ROLE_TOKENS: Final[frozenset[str]] = frozenset({"P", "D", "S", "I", "M", "R"})
ROLE_MARKER: Final = '"role":'
ASSESSMENT_PROMPT_LEGEND: Final = "Answer with a single letter: Y for yes, N for no, U for uncertain."
ROLE_PROMPT_LEGEND: Final = "Set role to a single letter chosen mnemonically from the role name: P=Provider, D=Deployer, S=diStributor, I=Importer, M=Product Manufacturer, R=Authorised Representative. Determine the role purely from the user's relationship to the AI system. Do not discuss scope, applicability, exclusions, or whether the Regulation's obligations apply — those are evaluated by separate criteria and must not appear in the reasoning here."
RESOURCE_EXHAUSTED_MARKER: Final = "[RESOURCE_EXHAUSTED]"
CRITERION_MAX_CONCURRENCY: Final = 5
GEMINI_MAX_RETRIES_429: Final = 5
GEMINI_RETRY_INITIAL_DELAY: Final = 2.0
GEMINI_RETRY_BACKOFF_FACTOR: Final = 1.5

class Role(StrEnum):
    PROVIDER = "provider"
    DEPLOYER = "deployer"
    DISTRIBUTOR = "distributor"
    IMPORTER = "importer"
    PRODUCT_MANUFACTURER = "product_manufacturer"
    AUTHORISED_REPRESENTATIVE = "authorised_representative"

def format_role(role: Role | str) -> str:
    return str(role).replace("_", " ").title()

ALL_ROLES: Final[set[Role]] = set(Role)

LETTER_TO_ROLE: Final[dict[str, Role]] = {
    "P": Role.PROVIDER,
    "D": Role.DEPLOYER,
    "S": Role.DISTRIBUTOR,
    "I": Role.IMPORTER,
    "M": Role.PRODUCT_MANUFACTURER,
    "R": Role.AUTHORISED_REPRESENTATIVE,
}

class RiskTier(StrEnum):
    OUT_OF_SCOPE = "Out of Scope"
    CRITICAL = "Critical"
    HIGH = "High"
    LIMITED = "Limited"
    LOW = "Low"

class ActivePhase(StrEnum):
    DEFINING_SYSTEM = "defining_system"
    ASKING_CLARIFICATION = "asking_clarification"
    EVALUATING_CRITERIA = "evaluating_criteria"
    SYNTHESIS = "synthesis"

class ExclusionType(StrEnum):
    MILITARY = "military"
    THIRD_COUNTRY_LE = "third_country_le"
    RESEARCH = "research"
    OPEN_SOURCE = "open_source"
    PERSONAL = "personal"
    HIGH_RISK_EXCEPTION = "high_risk_exception"

class AmbiguityType(StrEnum):
    TERMINOLOGY = "terminology"
    UNDERSPECIFIED = "underspecified"
    SCOPE = "scope"

EXCLUSION_CRITERION_IDS: Final[dict[str, ExclusionType]] = {
    "art2_excl_military": ExclusionType.MILITARY,
    "art2_excl_third_country_le": ExclusionType.THIRD_COUNTRY_LE,
    "art2_excl_research": ExclusionType.RESEARCH,
    "art2_excl_open_source": ExclusionType.OPEN_SOURCE,
    "art2_excl_personal": ExclusionType.PERSONAL,
}

OPEN_SOURCE_EXCLUSION_ID: Final = "art2_excl_open_source"

NON_TIER_ARTICLE_PREFIXES: Final = ("Art. 51", "Art. 25", "Art. 6(1)(b)", "Art. 6(3)", "Art. 3", "Art. 2")
ROLE_CHANGING_ARTICLE_PREFIXES: Final = ("Annex I", "Annex III", "Art. 6(1)(b)", "Art. 6(3)")

ART2_SCOPE_CRITERION_IDS: Final[list[str]] = [
    "art2_provider_places_ai_eu",
    "art2_provider_places_gpai_eu",
    "art2_deployer_established_eu",
    "art2_importer_third_country_trademark",
    "art2_output_used_in_eu",
]

GPAI_FLAG_CRITERION_ID: Final = "art2_provider_places_gpai_eu"

ART2_PROVIDER_SCOPE_IDS: Final[set[str]] = {
    "art2_provider_places_ai_eu",
    GPAI_FLAG_CRITERION_ID,
}

IDENTIFICATION_CRITERION_IDS: Final[set[str]] = {
    "art3_entity_role",
    *ART2_SCOPE_CRITERION_IDS,
    *EXCLUSION_CRITERION_IDS,
}

GATE_CRITERION_IDS: Final[set[str]] = {
    "art6_significant_risk",
    "art6_third_party_conformity_assessment_required",
}

class AssessmentCriterion(TypedDict):
    id: str
    article_ref: str
    question: str
    applies_to_roles: set[Role]

ASSESSMENT_PROMPT_TEMPLATE: Final = """SYSTEM: You are an EU AI Act compliance analyst. The SYSTEM DESCRIPTION
below was written by the user about their own AI system. Decide whether
the user's system DOES what the CRITERION describes.

Answer the applies field with a single letter:
- Y (yes): the description states or strongly implies that the system does
  what the criterion describes.
- N (no): the description states the system does not, OR the description
  does not mention this behavior at all. Absence of evidence about the
  behavior is "no", not "uncertain".
- U (uncertain): only when the description discusses something related to
  the criterion but is genuinely ambiguous about whether the behavior
  matches.

Your reasoning must quote inline only from the SYSTEM DESCRIPTION{rag_clause} --
do not cite anything outside this context.

VOICE: Write reasoning in second person, addressing the user directly.
Use "you", "your system", "your role" -- never "the user", "their system",
or "the described system". When quoting a prior clarification, quote only
the user's answer text -- do not include the "Q:" or "A:" labels that
structure the input. Refer to Act provisions only by their legal
designation (e.g., "Article 5(1)(h)", "Annex I §A, point 10"). Do not
name the retrieval container in reasoning -- never write "the RELEVANT AI
ACT TEXT", "the retrieved text", "as listed above", or similar references
to the prompt's structure.

CRITERION:
  id:           {criterion_id}
  article:      {article_ref}
  question:     {question}
{rag_block}
SYSTEM DESCRIPTION:
  raw input:    {raw_input}
  role:         {role}
  is GPAI:      {is_gpai}
  prior clarifications: {prior_clarifications}

OUTPUT JSON matching the CriterionAssessmentResponse schema."""

IDENTIFY_SYSTEM_PROMPT_TEMPLATE: Final = """SYSTEM: You are an EU AI Act compliance analyst. The DESCRIPTION below
was written by the user about their own AI system. Answer the CRITERION
below by extracting the literal value the schema expects. Your reasoning
must quote inline only from the DESCRIPTION{rag_clause} -- do not cite
anything outside this context.

VOICE: Write reasoning in second person, addressing the user directly.
Use "you", "your system", "your role" -- never "the user", "their system",
or "the described system". When quoting a prior clarification, quote only
the user's answer text -- do not include the "Q:" or "A:" labels that
structure the input. Refer to Act provisions only by their legal
designation (e.g., "Article 5(1)(h)", "Annex I §A, point 10"). Do not
name the retrieval container in reasoning -- never write "the RELEVANT AI
ACT TEXT", "the retrieved text", "as listed above", or similar references
to the prompt's structure.

CRITERION:
  id:           {criterion_id}
  article:      {article_ref}
  question:     {question}
{rag_block}
DESCRIPTION: {description}
{context_block}prior clarifications: {prior_clarifications}

OUTPUT JSON matching the {schema_name} schema. {schema_legend}"""

AT_DEFINITIONS: Final = """- terminology: The description uses a term whose legal or technical interpretation determines the answer. The user must clarify which meaning they intended.
- underspecified: The behavior or attribute the criterion asks about is not addressed by the description. The user must supply the missing fact.
- scope: The description mentions a related but possibly out-of-scope activity. The user must confirm whether the criterion's behavior is part of their system."""

AT_CLARIFICATION_ACTIONS: Final[dict[AmbiguityType, str]] = {
    AmbiguityType.TERMINOLOGY: (
        "Quote the specific phrase from the DESCRIPTION whose interpretation drives the answer. "
        "Using only the RELEVANT AI ACT TEXT for this criterion, enumerate the distinct "
        "interpretations the Act distinguishes for that phrase as labelled options. "
        "Ask which one matches the user's system. Do not invent options that are not in the "
        "Act text; if the Act text does not enumerate options, ask which intended meaning applies."
    ),
    AmbiguityType.UNDERSPECIFIED: (
        "Identify the specific fact the criterion requires that the DESCRIPTION does not "
        "address. Ask for that fact directly, in plain language. If the RELEVANT AI ACT TEXT "
        "enumerates options for that fact (roles, risk tiers, exclusion categories), present "
        "them as labelled options; otherwise ask an open question."
    ),
    AmbiguityType.SCOPE: (
        "Quote the adjacent activity the user mentioned in the DESCRIPTION. Using the RELEVANT "
        "AI ACT TEXT, state the criterion's specific in-scope behaviour in one short clause, "
        "then ask the user to confirm whether their system performs that in-scope behaviour or "
        "only the adjacent activity they mentioned."
    ),
}

AMBIGUITY_CLASSIFICATION_PROMPT_TEMPLATE: Final = """SYSTEM: You are an EU AI Act compliance analyst. The DESCRIPTION below
was written by the user about their own AI system. An automated assessment
flagged the CRITERIA listed below as uncertain. For each criterion,
classify which AMBIGUITY TYPE best explains the gap between the
description and a confident answer.

AMBIGUITY TYPES:
{at_definitions}

For each criterion, briefly explain in 'reasoning' which AT applies and
why, citing inline only from the DESCRIPTION or the prior assessment
reasoning -- do not cite anything outside this context. Then assign
exactly one ambiguity_type from the list above. Preserve criterion_id
values exactly.

DESCRIPTION: {description}

UNCERTAIN CRITERIA:
{criteria_block}

OUTPUT JSON matching the BatchAmbiguityResponse schema, with one
classification per criterion in the same order."""

CLARIFICATION_GENERATION_PROMPT_TEMPLATE: Final = """SYSTEM: You are an EU AI Act compliance analyst. The DESCRIPTION below
was written by the user about their own AI system. An automated assessment
flagged each CRITERION below as uncertain and classified the type of
ambiguity. For each criterion, generate exactly one clarifying question
the user can answer to resolve that ambiguity.

For each criterion, follow the ACTION specified in its block. The action
tells you how to construct the question for that criterion's ambiguity
type.

VOICE: Write each question in second person, addressing the user directly.
Use "you", "your system", "your role" -- never "the user", "their system",
or "the described system". Quote inline only from the DESCRIPTION or that
criterion's RELEVANT AI ACT TEXT -- do not cite anything outside this
context. Do not invent legal options or definitions that are not in the
provided Act text. Do not include Article, Annex, paragraph, or point
citations in the user-facing question -- no "as referred to in Article X",
"under Annex Y", "pursuant to Article Z", or similar legal references. The
user is a non-lawyer; rephrase what the criterion requires in plain words,
using the retrieved Act text only as your source for accuracy. Never refer
to the retrieval container itself ("the RELEVANT AI ACT TEXT", "the
retrieved text", "as listed above"). Each question must be self-contained:
the user should be able to answer it without first reading the criterion's
article.

If a criterion already has PRIOR CLARIFICATIONS, your new question must
target a different gap than the prior exchanges; do not repeat what was
already asked.

DESCRIPTION: {description}

UNCERTAIN CRITERIA:
{criteria_block}

OUTPUT JSON matching the BatchClarificationGeneration schema, with one
clarification per criterion in the same order. Preserve criterion_id
values exactly. The 'question' field must contain only the user-facing
question text -- no preamble, no labels, no JSON-internal commentary."""

