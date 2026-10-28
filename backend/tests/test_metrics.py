from app.eval.metrics import ndcg_at_k, recall_at_k


def test_recall_at_k_perfect() -> None:
    relevant = {"a", "b", "c"}
    retrieved = ["a", "b", "c", "d", "e"]
    assert recall_at_k(relevant, retrieved, 3) == 1.0


def test_recall_at_k_partial() -> None:
    assert recall_at_k({"a", "b"}, ["a", "c", "d"], 3) == 0.5


def test_recall_at_k_empty_relevant() -> None:
    assert recall_at_k(set(), ["a"], 5) == 0.0


def test_ndcg_perfect_vs_reversed() -> None:
    rel = {"a", "b", "c"}
    perfect = ndcg_at_k(rel, ["a", "b", "c"], 3)
    reversed_order = ndcg_at_k(rel, ["c", "b", "a"], 3)
    # Both are "all relevant", so nDCG is 1 regardless of order within k.
    assert perfect == 1.0
    assert reversed_order == 1.0


def test_ndcg_rewards_earlier_hits() -> None:
    rel = {"a"}
    early = ndcg_at_k(rel, ["a", "x", "y"], 3)
    late = ndcg_at_k(rel, ["x", "y", "a"], 3)
    assert early > late
