from pathlib import Path
from typing import TypedDict
from .constants import (
    ANNEX_I_SECTION_PATTERN,
    ART3_DEFINITION_PATTERN,
    ARTICLE_LETTER_POINT_SPLIT_REFS,
    ARTICLE_PARAGRAPH_SPLIT_REFS,
    BOLD_TITLE_PATTERN,
    DEFINITION_TERM_PATTERN,
    HEADING_PATTERN,
    LETTER_POINT_PATTERN,
    PARAGRAPH_PATTERN,
    ROMAN_SUBPOINT_FOLLOWER_PATTERN,
)

class ActChunk(TypedDict):
    article_ref: str
    title: str
    text: str

def _make_chunk(ref: str, body: str, title: str = "") -> ActChunk:
    if not title:
        bold = BOLD_TITLE_PATTERN.search(body[:200])
        if bold:
            title = bold.group(1).strip()
    return {
        "article_ref": ref,
        "title": title,
        "text": f"[{ref}] {body.strip()}",
    }

def _split_art3(body: str) -> list[ActChunk]:
    chunks: list[ActChunk] = []
    matches = list(ART3_DEFINITION_PATTERN.finditer(body))
    for i, m in enumerate(matches):
        num = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sub_body = body[start:end].strip()
        ref = f"Art. 3({num})"
        term_match = DEFINITION_TERM_PATTERN.search(sub_body)
        title = f"'{term_match.group(1).strip()}'" if term_match else ""
        chunks.append({
            "article_ref": ref,
            "title": title,
            "text": f"[{ref}] {sub_body}",
        })
    return chunks

def _split_letter_points(body: str, parent_ref: str) -> list[ActChunk]:
    candidates = list(LETTER_POINT_PATTERN.finditer(body))
    matches = []
    for m in candidates:
        if m.group(1) == "i" and ROMAN_SUBPOINT_FOLLOWER_PATTERN.search(body, m.end()):
            continue
        matches.append(m)
    chunks: list[ActChunk] = []
    for i, m in enumerate(matches):
        letter = m.group(1)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sub_body = body[start:end].strip()
        ref = f"{parent_ref}({letter})"
        chunks.append({
            "article_ref": ref,
            "title": "",
            "text": f"[{ref}] {sub_body}",
        })
    return chunks

def _split_paragraphs(body: str, parent_ref: str, split_letters: bool) -> list[ActChunk]:
    chunks: list[ActChunk] = []
    matches = list(PARAGRAPH_PATTERN.finditer(body))
    for i, m in enumerate(matches):
        num = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        para_body = body[start:end].strip()
        para_ref = f"{parent_ref}({num})"
        chunks.append({
            "article_ref": para_ref,
            "title": "",
            "text": f"[{para_ref}] {para_body}",
        })
        if split_letters:
            chunks.extend(_split_letter_points(para_body, para_ref))
    return chunks

def _split_annex_i(body: str) -> list[ActChunk]:
    chunks: list[ActChunk] = []
    matches = list(ANNEX_I_SECTION_PATTERN.finditer(body))
    for i, m in enumerate(matches):
        letter = m.group(1)
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sub_body = body[start:end].strip()
        ref = f"Annex I §{letter}"
        chunks.append({
            "article_ref": ref,
            "title": "",
            "text": f"[{ref}] {sub_body}",
        })
    return chunks

def _split_annex_iii(body: str) -> list[ActChunk]:
    chunks: list[ActChunk] = []
    matches = list(PARAGRAPH_PATTERN.finditer(body))
    for i, m in enumerate(matches):
        num = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sub_body = body[start:end].strip()
        ref = f"Annex III §{num}"
        chunks.append({
            "article_ref": ref,
            "title": "",
            "text": f"[{ref}] {sub_body}",
        })
    return chunks

def _sub_chunks(parent_ref: str, body: str) -> list[ActChunk]:
    if parent_ref == "Art. 3":
        return _split_art3(body)
    if parent_ref in ARTICLE_PARAGRAPH_SPLIT_REFS:
        return _split_paragraphs(
            body,
            parent_ref,
            split_letters=parent_ref in ARTICLE_LETTER_POINT_SPLIT_REFS,
        )
    if parent_ref == "Annex I":
        return _split_annex_i(body)
    if parent_ref == "Annex III":
        return _split_annex_iii(body)
    return []

def load_chunks(path: str | Path) -> list[ActChunk]:
    raw = Path(path).read_text(encoding="utf-8")
    matches = list(HEADING_PATTERN.finditer(raw))
    chunks: list[ActChunk] = []
    for i, m in enumerate(matches):
        ref = m.group(1).strip()
        body_start = m.end()
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(raw)
        body = raw[body_start:body_end].strip()
        chunks.append(_make_chunk(ref, body))
        chunks.extend(_sub_chunks(ref, body))
    return chunks
