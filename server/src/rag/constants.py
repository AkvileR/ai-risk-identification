import re
from pathlib import Path
from typing import Final

_DATA_DIR: Final = Path(__file__).resolve().parent / "data"

AI_ACT_CORPUS_PATH: Final = _DATA_DIR / "ai_act.md"
AI_ACT_INDEX_PATH: Final = _DATA_DIR / "ai_act_index.npz"

HEADING_PATTERN: Final = re.compile(r"(?m)^##\s+(.+?)\s*$")
BOLD_TITLE_PATTERN: Final = re.compile(r"\*\*(.+?)\*\*")

EMBEDDING_MODEL: Final = "text-embedding-005"
EMBEDDING_MAX_CHARS_PER_BATCH: Final = 40_000
EMBEDDING_MAX_ITEMS_PER_BATCH: Final = 20
EMBEDDING_SLEEP_BETWEEN_BATCHES: Final = 9.0
EMBEDDING_MAX_RETRIES: Final = 8
EMBEDDING_RETRY_INITIAL_DELAY: Final = 9.0
EMBEDDING_RETRY_BACKOFF_FACTOR: Final = 1.5
EMBEDDING_RETRY_MAX_DELAY: Final = 60.0
