import time
import numpy as np
from google.genai.errors import ClientError
from ..ai_client import client
from .constants import (
    EMBEDDING_MAX_CHARS_PER_BATCH,
    EMBEDDING_MAX_ITEMS_PER_BATCH,
    EMBEDDING_MAX_RETRIES,
    EMBEDDING_MODEL,
    EMBEDDING_RETRY_BACKOFF_FACTOR,
    EMBEDDING_RETRY_INITIAL_DELAY,
    EMBEDDING_RETRY_MAX_DELAY,
    EMBEDDING_SLEEP_BETWEEN_BATCHES,
)

def _split_batch(texts: list[str]) -> list[list[int]]:
    batches: list[list[int]] = []
    current: list[int] = []
    current_chars = 0
    for i, t in enumerate(texts):
        item_chars = len(t)
        if current and (
            current_chars + item_chars > EMBEDDING_MAX_CHARS_PER_BATCH
            or len(current) >= EMBEDDING_MAX_ITEMS_PER_BATCH
        ):
            batches.append(current)
            current = []
            current_chars = 0
        current.append(i)
        current_chars += item_chars
    if current:
        batches.append(current)
    return batches

def _embed_batch(batch: list[str]) -> list[list[float]]:
    delay = EMBEDDING_RETRY_INITIAL_DELAY
    for attempt in range(EMBEDDING_MAX_RETRIES):
        try:
            response = client.models.embed_content(model=EMBEDDING_MODEL, contents=batch)
            return [e.values for e in response.embeddings]
        except ClientError as e:
            if e.code == 429 and attempt < EMBEDDING_MAX_RETRIES - 1:
                print(f"[rag] 429 quota; sleeping {delay:.1f}s")
                time.sleep(delay)
                delay = min(delay * EMBEDDING_RETRY_BACKOFF_FACTOR, EMBEDDING_RETRY_MAX_DELAY)
                continue
            if e.code == 400 and len(batch) > 1:
                mid = len(batch) // 2
                return _embed_batch(batch[:mid]) + _embed_batch(batch[mid:])
            raise
    raise RuntimeError("unreachable")

def embed(texts: list[str]) -> np.ndarray:
    if not texts:
        return np.zeros((0, 0), dtype=np.float32)
    batches = _split_batch(texts)
    print(f"[rag] embedding {len(texts)} items in {len(batches)} batches")
    out: list[list[float] | None] = [None] * len(texts)
    for i, indices in enumerate(batches):
        batch_texts = [texts[idx] for idx in indices]
        result = _embed_batch(batch_texts)
        for idx, vec in zip(indices, result):
            out[idx] = vec
        if i + 1 < len(batches):
            time.sleep(EMBEDDING_SLEEP_BETWEEN_BATCHES)
    arr = np.asarray(out, dtype=np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return arr / norms
