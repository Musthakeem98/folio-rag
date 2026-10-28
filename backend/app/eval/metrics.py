"""Retrieval + answer-quality metrics.

Retrieval metrics (recall@k, nDCG) are deterministic and cheap.
Answer-quality metrics (faithfulness, citation_precision) require an
LLM judge — kept behind the same interface so the harness is uniform.
"""

import math
from collections.abc import Sequence


def recall_at_k(relevant: set[str], retrieved: Sequence[str], k: int) -> float:
    if not relevant:
        return 0.0
    hits = len(set(retrieved[:k]) & relevant)
    return hits / len(relevant)


def ndcg_at_k(relevant: set[str], retrieved: Sequence[str], k: int) -> float:
    dcg = sum((1.0 / math.log2(i + 2)) for i, cid in enumerate(retrieved[:k]) if cid in relevant)
    ideal = sum(1.0 / math.log2(i + 2) for i in range(min(len(relevant), k)))
    return dcg / ideal if ideal else 0.0
