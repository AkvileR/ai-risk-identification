import numpy as np
from ..constants import AssessmentCriterion
from .constants import (
    CROSSREF_ANNEX_PATTERN,
    CROSSREF_ARTICLE_PATTERN,
    RAG_CROSSREF_K,
    RAG_DEFINITIONS_K,
    RAG_MAX_RESULTS,
    RAG_TOP_K,
)
from .embeddings import embed
from .index import get_index
from .loader import ActChunk

def retrieve(query: str, k: int = RAG_TOP_K) -> list[tuple[ActChunk, float]]:
    vectors, chunks = get_index()
    query_vec = embed([query])[0]
    scores = vectors @ query_vec
    top = np.argsort(-scores)[:k]
    return [(chunks[i], float(scores[i])) for i in top]

def _extract_crossrefs(text: str) -> list[str]:
    refs: list[str] = []
    body = text[text.find("]") + 1 :] if text.startswith("[") else text
    for m in CROSSREF_ARTICLE_PATTERN.finditer(body):
        num, para, letter = m.group(1), m.group(2), m.group(3)
        ref = f"Art. {num}"
        if para:
            ref += f"({para})"
            if letter:
                ref += f"({letter})"
        refs.append(ref)
    for m in CROSSREF_ANNEX_PATTERN.finditer(body):
        roman, section = m.group(1), m.group(2)
        refs.append(f"Annex {roman}")
        if section:
            refs.append(f"Annex {roman} §{section}")
    return refs

def _expand_crossrefs(
    results: list[ActChunk],
    by_ref: dict[str, ActChunk],
    seen: set[str],
    max_added: int,
) -> list[ActChunk]:
    added: list[ActChunk] = []
    for chunk in results:
        for ref in _extract_crossrefs(chunk["text"]):
            if ref in seen or ref not in by_ref:
                continue
            seen.add(ref)
            added.append(by_ref[ref])
            if len(added) >= max_added:
                return added
    return added

def retrieve_for_criterion(
    criterion: AssessmentCriterion,
    k: int = RAG_TOP_K,
) -> list[ActChunk]:
    target_ref = criterion["article_ref"]
    vectors, chunks = get_index()
    by_ref: dict[str, ActChunk] = {c["article_ref"]: c for c in chunks}

    exact: list[ActChunk] = [c for c in chunks if c["article_ref"] == target_ref]
    seen = {c["article_ref"] for c in exact}
    results: list[ActChunk] = list(exact)

    query_vec = embed([criterion["question"]])[0]
    scores = vectors @ query_vec

    for i in np.argsort(-scores)[:k]:
        chunk = chunks[i]
        if chunk["article_ref"] in seen:
            continue
        seen.add(chunk["article_ref"])
        results.append(chunk)

    if target_ref != "Art. 3" and not target_ref.startswith("Art. 3("):
        def_indices = [i for i, c in enumerate(chunks) if c["article_ref"].startswith("Art. 3(")]
        if def_indices:
            def_scores = vectors[def_indices] @ query_vec
            for j in np.argsort(-def_scores)[:RAG_DEFINITIONS_K]:
                chunk = chunks[def_indices[j]]
                if chunk["article_ref"] in seen:
                    continue
                seen.add(chunk["article_ref"])
                results.append(chunk)

    results.extend(_expand_crossrefs(results, by_ref, seen, RAG_CROSSREF_K))

    return results[:RAG_MAX_RESULTS]
