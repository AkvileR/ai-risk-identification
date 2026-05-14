import hashlib
import json
from pathlib import Path
import numpy as np
from .constants import AI_ACT_CORPUS_PATH, AI_ACT_INDEX_PATH
from .embeddings import embed
from .loader import ActChunk, load_chunks

_cached: tuple[np.ndarray, list[ActChunk]] | None = None

def _hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def build_or_load_index(
    corpus_path: str | Path = AI_ACT_CORPUS_PATH,
    cache_path: str | Path = AI_ACT_INDEX_PATH,
) -> tuple[np.ndarray, list[ActChunk]]:
    corpus_path = Path(corpus_path)
    cache_path = Path(cache_path)
    corpus_hash = _hash_file(corpus_path)

    if cache_path.exists():
        cached = np.load(cache_path, allow_pickle=False)
        cached_hash = str(cached["corpus_hash"])
        if cached_hash == corpus_hash:
            vectors = cached["vectors"]
            cached_chunks = json.loads(str(cached["chunks_json"]))
            assert vectors.shape[0] == len(cached_chunks), (
                f"index drift: {vectors.shape[0]} vectors but {len(cached_chunks)} chunks in cache"
            )
            return vectors, cached_chunks
        print(
            f"[rag] WARNING: cache hash {cached_hash[:8]} != corpus hash {corpus_hash[:8]} — rebuilding"
        )

    chunks = load_chunks(corpus_path)
    print(f"[rag] building index for {len(chunks)} chunks...")
    vectors = embed([c["text"] for c in chunks])
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        cache_path,
        vectors=vectors,
        chunks_json=json.dumps(chunks),
        corpus_hash=corpus_hash,
    )
    print(f"[rag] wrote {cache_path}")
    return vectors, chunks

def get_index() -> tuple[np.ndarray, list[ActChunk]]:
    global _cached
    if _cached is None:
        _cached = build_or_load_index()
    return _cached
