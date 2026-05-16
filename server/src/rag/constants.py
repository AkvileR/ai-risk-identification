import re
from pathlib import Path
from typing import Final

_DATA_DIR: Final = Path(__file__).resolve().parent / "data"

AI_ACT_CORPUS_PATH: Final = _DATA_DIR / "ai_act.md"
AI_ACT_INDEX_PATH: Final = _DATA_DIR / "ai_act_index.npz"

HEADING_PATTERN: Final = re.compile(r"(?m)^##\s+(.+?)\s*$")
BOLD_TITLE_PATTERN: Final = re.compile(r"\*\*(.+?)\*\*")
ART3_DEFINITION_PATTERN: Final = re.compile(r"(?m)^\((\d+)\)\s*")
DEFINITION_TERM_PATTERN: Final = re.compile(r"^\s*[‘']([^’']+)[’']")
PARAGRAPH_PATTERN: Final = re.compile(r"(?m)^(\d+)\.\s*$")
LETTER_POINT_PATTERN: Final = re.compile(r"(?m)^\(([a-z])\)\s+")
ROMAN_SUBPOINT_FOLLOWER_PATTERN: Final = re.compile(r"(?m)^\(ii\)\s+")
ANNEX_I_SECTION_PATTERN: Final = re.compile(r"(?m)^Section\s+([AB])\.\s")
CROSSREF_ARTICLE_PATTERN: Final = re.compile(r"(?:Article|Art\.)\s+(\d+)(?:\((\d+)\))?(?:\(([a-z])\))?")
CROSSREF_ANNEX_PATTERN: Final = re.compile(r"Annex\s+([IVX]+)(?:\s*[,]?\s+Section\s+([AB]))?")

ARTICLE_PARAGRAPH_SPLIT_REFS: Final[frozenset[str]] = frozenset({"Art. 5", "Art. 6", "Art. 25", "Art. 50"})
ARTICLE_LETTER_POINT_SPLIT_REFS: Final[frozenset[str]] = frozenset({"Art. 5", "Art. 6"})

RAG_TOP_K: Final = 5
RAG_DEFINITIONS_K: Final = 2
RAG_CROSSREF_K: Final = 3
RAG_MAX_RESULTS: Final = 8

EMBEDDING_MODEL: Final = "text-embedding-005"
EMBEDDING_MAX_CHARS_PER_BATCH: Final = 40_000
EMBEDDING_MAX_ITEMS_PER_BATCH: Final = 20
EMBEDDING_SLEEP_BETWEEN_BATCHES: Final = 9.0
EMBEDDING_MAX_RETRIES: Final = 8
EMBEDDING_RETRY_INITIAL_DELAY: Final = 9.0
EMBEDDING_RETRY_BACKOFF_FACTOR: Final = 1.5
EMBEDDING_RETRY_MAX_DELAY: Final = 60.0
