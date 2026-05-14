from pathlib import Path
from typing import TypedDict
from .constants import BOLD_TITLE_PATTERN, HEADING_PATTERN

# Scoped from heading to heading for now
class ActChunk(TypedDict):
    article_ref: str
    title: str
    text: str

def load_chunks(path: str | Path) -> list[ActChunk]:
    raw = Path(path).read_text(encoding="utf-8")
    matches = list(HEADING_PATTERN.finditer(raw))
    chunks: list[ActChunk] = []
    for i, m in enumerate(matches):
        ref = m.group(1).strip()
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        body = raw[body_start:body_end].strip()
        title_line = ""
        bold = BOLD_TITLE_PATTERN.match(body)
        if bold:
            title_line = bold.group(1).strip()
        chunks.append(
            {
                "article_ref": ref,
                "title": title_line,
                "text": f"[{ref}] {body}",
            }
        )
    return chunks
