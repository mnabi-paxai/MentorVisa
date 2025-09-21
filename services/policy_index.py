# services/policy_index.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from scipy.sparse import csr_matrix

@dataclass
class PolicyHit:
    text: str
    score: float          # weighted similarity score
    meta: Dict[str, Any]  # contains source, source_title, section, is_catalog, weight, etc.

class PolicyIndex:
    def __init__(self):
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.matrix: Optional[csr_matrix] = None
        self.chunks: List[Dict[str, Any]] = []
        self._weights: Optional[np.ndarray] = None

    @property
    def ready(self) -> bool:
        # Avoid truthiness checks on sparse matrices
        return (
            self.vectorizer is not None
            and self.matrix is not None
            and self.matrix.shape[0] > 0
            and bool(self.chunks)
        )

    def build(self, chunks: List[Dict[str, Any]]) -> None:
        """Build TF-IDF index from chunks."""
        self.chunks = chunks or []
        texts = [c["text"] for c in self.chunks]
        self.vectorizer = TfidfVectorizer(min_df=1, ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform(texts)
        # Per-chunk retrieval weights (default 1.0)
        w = [float(c.get("weight", 1.0)) for c in self.chunks]
        self._weights = np.asarray(w, dtype=float)

    def search(self, query: str, k: int = 5) -> List[PolicyHit]:
        """Return top-k weighted hits for a query."""
        if not query or not query.strip() or not self.ready:
            return []
        q_vec = self.vectorizer.transform([query])
        sims = linear_kernel(q_vec, self.matrix)[0]  # shape (N,)
        # down/up weight chunks
        if self._weights is not None:
            sims = sims * self._weights
        top_idx = np.argsort(-sims)[:k]
        hits: List[PolicyHit] = []
        for i in top_idx:
            hits.append(PolicyHit(
                text=self.chunks[i]["text"],
                score=float(sims[i]),
                meta=self.chunks[i],
            ))
        return hits
    
# ---- minimal shim for callers expecting get_policy_index() ----
# A module-level singleton + accessor (doesn't change existing behavior).
policy_index = PolicyIndex()

def get_policy_index() -> PolicyIndex:
    return policy_index
