from typing import Final, TypedDict
from enum import StrEnum

ASSESSMENT_CONFIDENCE_THRESHOLD: Final = 0.75

RAG_ENABLED: Final = False

GEMINI_MODEL: Final = "gemini-2.5-flash"
ASSESSMENT_TEMPERATURE: Final = 0.0
MAX_CLARIFICATION_ROUNDS: Final = 2
LOGPROB_RETRY_LIMIT: Final = 3
LOGPROB_TEMPERATURE: Final = 2.5
LOGPROB_TOP_K: Final = 5
MAX_VALUE_TOKEN_WINDOW: Final = 5
ANSWER_TOKENS: Final[frozenset[str]] = frozenset({"Y", "N", "U"})
APPLIES_MARKER: Final = '"applies":'
LETTER_TO_VERDICT: Final[dict[str, str]] = {"Y": "yes", "N": "no", "U": "uncertain"}
ROLE_TOKENS: Final[frozenset[str]] = frozenset({"P", "D", "S", "I", "M", "R"})
ROLE_MARKER: Final = '"role":'
BOOL_TOKENS: Final[frozenset[str]] = frozenset({"Y", "N"})
ASSESSMENT_PROMPT_LEGEND: Final = "Answer with a single letter: Y for yes, N for no, U for uncertain."
ROLE_PROMPT_LEGEND: Final = "Set role to a single letter chosen mnemonically from the role name: P=Provider, D=Deployer, S=diStributor, I=Importer, M=Product Manufacturer, R=Authorised Representative."
EXCLUSIONS_PROMPT_LEGEND: Final = "For each exclusion field, set Y if the exclusion applies to your system, N otherwise."
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

ART2_EXCLUSION_TYPES: Final[tuple[ExclusionType, ...]] = (
    ExclusionType.MILITARY,
    ExclusionType.THIRD_COUNTRY_LE,
    ExclusionType.RESEARCH,
    ExclusionType.OPEN_SOURCE,
    ExclusionType.PERSONAL,
)

EXCLUSION_MARKERS: Final[dict[ExclusionType, str]] = {e: f'"{e.value}":' for e in ART2_EXCLUSION_TYPES}

#TODO: Make them taken from KB later
EXCLUSION_MESSAGES: Final[dict[ExclusionType, str]] = {
    ExclusionType.MILITARY: "Excluded under Art. 2: military / defence / national-security use. Act obligations do not apply.",
    ExclusionType.THIRD_COUNTRY_LE: "Excluded under Art. 2: third-country law-enforcement / judicial cooperation use. Act obligations do not apply.",
    ExclusionType.RESEARCH: "Partial exclusion under Art. 2: scientific R&D. Act obligations apply once the system is placed on the market or put into service.",
    ExclusionType.OPEN_SOURCE: "Partial exclusion under Art. 2: free/open-source licence. Act obligations apply once the system is placed on the market or put into service as part of a high-risk, prohibited, GPAI, or transparency-obliged system.",
    ExclusionType.PERSONAL: "Partial exclusion under Art. 2: purely personal, non-professional deployment. Deployer obligations do not apply.",
    ExclusionType.HIGH_RISK_EXCEPTION: "High-risk Art. 2 exception: the system would otherwise be excluded but is high-risk under Annex I §A. Only Article 112 applies — track Commission reviews and updates.",
}

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
    "art2_exclusions",
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

VOICE: Write all reasoning and clarification questions in second person,
addressing the user directly. Use "you", "your system", "your role" --
never "the user", "their system", or "the described system".

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

OUTPUT JSON matching the CriterionAssessmentResponse schema. If applies="U",
set clarification_question to a single targeted follow-up addressed to the user
in second person."""

IDENTIFY_SYSTEM_PROMPT_TEMPLATE: Final = """SYSTEM: You are an EU AI Act compliance analyst. The DESCRIPTION below
was written by the user about their own AI system. Answer the CRITERION
below by extracting the literal value the schema expects. Your reasoning
must quote inline only from the DESCRIPTION{rag_clause} -- do not cite
anything outside this context.

VOICE: Write reasoning and clarification_question in second person,
addressing the user directly. Use "you", "your system", "your role" --
never "the user", "their system", or "the described system".

CRITERION:
  id:           {criterion_id}
  article:      {article_ref}
  question:     {question}
{rag_block}
DESCRIPTION: {description}
{context_block}prior clarifications: {prior_clarifications}

OUTPUT JSON matching the {schema_name} schema. {schema_legend} If the answer
is ambiguous from the DESCRIPTION, set clarification_question to a single
targeted follow-up addressed to the user in second person; otherwise leave
it null."""

