from .loader import ActChunk, load_chunks
from .index import build_or_load_index, get_index
from .retriever import retrieve, retrieve_for_criterion

def format_chunks_block(chunks) -> str:
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

__all__ = [
    "ActChunk",
    "load_chunks",
    "build_or_load_index",
    "retrieve",
    "get_index",
    "retrieve_for_criterion",
    "format_chunks_block",
]
