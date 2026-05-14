import math
import os
import time
from functools import wraps
from typing import Literal, Optional
from google import genai
from google.genai import errors as genai_errors
from google.genai.types import HttpOptions
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

from .constants import (
    ANSWER_TOKENS,
    APPLIES_MARKER,
    ART2_EXCLUSION_TYPES,
    ASSESSMENT_TEMPERATURE,
    BOOL_TOKENS,
    EXCLUSION_MARKERS,
    ExclusionType,
    GEMINI_MAX_RETRIES_429,
    GEMINI_MODEL,
    GEMINI_RETRY_BACKOFF_FACTOR,
    GEMINI_RETRY_INITIAL_DELAY,
    LOGPROB_RETRY_LIMIT,
    LOGPROB_TEMPERATURE,
    LOGPROB_TOP_K,
    MAX_VALUE_TOKEN_WINDOW,
    RESOURCE_EXHAUSTED_MARKER,
    ROLE_MARKER,
    ROLE_TOKENS,
)

class EntityTypeResponse(BaseModel):
    role: Literal["P", "D", "S", "I", "M", "R"]
    reasoning: str
    clarification_question: Optional[str] = None

class ExclusionsResponse(BaseModel):
    military: Literal["Y", "N"]
    third_country_le: Literal["Y", "N"]
    research: Literal["Y", "N"]
    open_source: Literal["Y", "N"]
    personal: Literal["Y", "N"]
    reasoning: str
    clarification_question: Optional[str] = None

class CriterionAssessmentResponse(BaseModel):
    applies: Literal["Y", "N", "U"]
    reasoning: str
    clarification_question: Optional[str] = None

load_dotenv()

class ResourceExhaustedError(RuntimeError):
    """Raised when the Gemini API returns a 429 / RESOURCE_EXHAUSTED quota error."""
    
def _maybe_raise_resource_exhausted(exc: Exception) -> None:
    if isinstance(exc, genai_errors.ClientError):
        status = (getattr(exc, "status", "") or "").upper()
        code = getattr(exc, "code", None)
        if code == 429 or status == "RESOURCE_EXHAUSTED":
            raise ResourceExhaustedError(
                f"{RESOURCE_EXHAUSTED_MARKER} Gemini API quota exhausted. "
                f"Please wait and retry. (status={status or 'RESOURCE_EXHAUSTED'}, code={code})"
            ) from exc

client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location="global",
    http_options=HttpOptions(api_version="v1")
)

def _retry_on_resource_exhausted(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        delay = GEMINI_RETRY_INITIAL_DELAY
        for attempt in range(GEMINI_MAX_RETRIES_429 + 1):
            try:
                return fn(*args, **kwargs)
            except ResourceExhaustedError:
                if attempt == GEMINI_MAX_RETRIES_429:
                    raise
                time.sleep(delay)
                delay *= GEMINI_RETRY_BACKOFF_FACTOR
    return wrapper

def _extract_field_softmax(
    response,
    field_marker: str,
    allowed_tokens: frozenset[str],
) -> Optional[dict[str, float]]:
    try:
        lp = response.candidates[0].logprobs_result
        chosen = lp.chosen_candidates
        tops = lp.top_candidates
    except (AttributeError, IndexError):
        return None
    if not chosen or not tops:
        return None

    buffer = ""
    marker_end = None
    for i, c in enumerate(chosen):
        buffer += c.token or ""
        if field_marker in buffer:
            marker_end = i + 1
            break
    if marker_end is None:
        return None

    answer_pos = None
    scan_end = min(marker_end + MAX_VALUE_TOKEN_WINDOW, len(chosen))
    for j in range(marker_end, scan_end):
        tok = chosen[j].token or ""
        if "," in tok or "}" in tok:
            break
        if any(ch in tok for ch in allowed_tokens):
            answer_pos = j
            break
    if answer_pos is None or answer_pos >= len(tops):
        return None

    answer_alts: dict[str, float] = {}
    for c in (tops[answer_pos].candidates or []):
        if not c.token or c.log_probability is None:
            continue
        letters = [ch for ch in allowed_tokens if ch in c.token]
        if len(letters) == 1:
            answer_alts.setdefault(letters[0], c.log_probability)
    if not answer_alts:
        return None

    max_lp = max(answer_alts.values())
    exps = {
        t: math.exp((lp - max_lp) / LOGPROB_TEMPERATURE)
        for t, lp in answer_alts.items()
    }
    total = sum(exps.values())
    return {t: e / total for t, e in exps.items()}

def _generate_with_logprobs(prompt: str, schema: type[BaseModel]):
    try:
        return client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": schema,
                "temperature": ASSESSMENT_TEMPERATURE,
                "response_logprobs": True,
                "logprobs": LOGPROB_TOP_K,
            },
        )
    except Exception as e:
        _maybe_raise_resource_exhausted(e)
        raise

@_retry_on_resource_exhausted
def query_gemini_for_assessment(
    prompt: str,
) -> tuple[CriterionAssessmentResponse, Optional[dict[str, float]]]:
    parsed: Optional[CriterionAssessmentResponse] = None
    for attempt in range(LOGPROB_RETRY_LIMIT + 1):
        response = _generate_with_logprobs(prompt, CriterionAssessmentResponse)
        try:
            parsed = CriterionAssessmentResponse.model_validate_json(response.text)
        except ValidationError:
            if attempt == LOGPROB_RETRY_LIMIT:
                raise
            continue
        softmax = _extract_field_softmax(response, APPLIES_MARKER, ANSWER_TOKENS)
        if softmax is not None:
            return parsed, softmax
    return parsed, None

@_retry_on_resource_exhausted
def query_gemini_for_role(
    prompt: str,
) -> tuple[EntityTypeResponse, Optional[dict[str, float]]]:
    parsed: Optional[EntityTypeResponse] = None
    for attempt in range(LOGPROB_RETRY_LIMIT + 1):
        response = _generate_with_logprobs(prompt, EntityTypeResponse)
        try:
            parsed = EntityTypeResponse.model_validate_json(response.text)
        except ValidationError:
            if attempt == LOGPROB_RETRY_LIMIT:
                raise
            continue
        softmax = _extract_field_softmax(response, ROLE_MARKER, ROLE_TOKENS)
        if softmax is not None:
            return parsed, softmax
    return parsed, None

@_retry_on_resource_exhausted
def query_gemini_for_exclusions(
    prompt: str,
) -> tuple[ExclusionsResponse, Optional[dict[ExclusionType, dict[str, float]]]]:
    parsed: Optional[ExclusionsResponse] = None
    for attempt in range(LOGPROB_RETRY_LIMIT + 1):
        response = _generate_with_logprobs(prompt, ExclusionsResponse)
        try:
            parsed = ExclusionsResponse.model_validate_json(response.text)
        except ValidationError:
            if attempt == LOGPROB_RETRY_LIMIT:
                raise
            continue
        softmax_per_exclusion: dict[ExclusionType, dict[str, float]] = {}
        for e in ART2_EXCLUSION_TYPES:
            s = _extract_field_softmax(response, EXCLUSION_MARKERS[e], BOOL_TOKENS)
            if s is None:
                break
            softmax_per_exclusion[e] = s
        else:
            return parsed, softmax_per_exclusion
    return parsed, None
