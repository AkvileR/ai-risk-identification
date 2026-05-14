import numpy as np
from ..constants import AssessmentCriterion
from .embeddings import embed
from .index import get_index
from .loader import ActChunk

def retrieve(query: str, k: int = 5) -> list[tuple[ActChunk, float]]:
    vectors, chunks = get_index()
    query_vec = embed([query])[0]
    scores = vectors @ query_vec
    top = np.argsort(-scores)[:k]
    return [(chunks[i], float(scores[i])) for i in top]

def retrieve_for_criterion(
    criterion: AssessmentCriterion,
    k: int = 5,
) -> list[ActChunk]:
    target_ref = criterion["article_ref"]
    _, chunks = get_index()
    boosted: list[ActChunk] = [c for c in chunks if c["article_ref"] == target_ref]

    semantic = retrieve(criterion["question"], k=k)
    seen = {c["article_ref"] for c in boosted}
    results: list[ActChunk] = list(boosted)
    for chunk, _score in semantic:
        if chunk["article_ref"] in seen:
            continue
        seen.add(chunk["article_ref"])
        results.append(chunk)
        if len(results) >= k:
            break
    return results[:k]
