from collections import Counter
from math import log2


def seat_probs_from_outcomes(
    outcomes: Counter,
    lists: list[str],
    max_seats: int,
) -> dict[str, dict[int, float]]:
    total = sum(outcomes.values())
    seat_probs: dict[str, dict[int, float]] = {
        name: {seats: 0.0 for seats in range(max_seats + 1)} for name in lists
    }
    for alloc, count in outcomes.items():
        for idx, seats in enumerate(alloc):
            seat_probs[lists[idx]][seats] += count / total
    return seat_probs


def expected_seats(seat_probs: dict[str, dict[int, float]]) -> dict[str, float]:
    expected: dict[str, float] = {}
    for name, probs in seat_probs.items():
        expected[name] = sum(seats * prob for seats, prob in probs.items())
    return expected


def probability_at_least(
    seat_probs: dict[str, dict[int, float]],
    threshold: int,
) -> dict[str, float]:
    result: dict[str, float] = {}
    for name, probs in seat_probs.items():
        result[name] = sum(prob for seats, prob in probs.items() if seats >= threshold)
    return result


def allocation_entropy(outcomes: Counter) -> float:
    total = sum(outcomes.values())
    entropy = 0.0
    for count in outcomes.values():
        p = count / total
        entropy -= p * log2(p)
    return entropy


def seat_entropy(seat_probs: dict[str, dict[int, float]]) -> dict[str, float]:
    entropies: dict[str, float] = {}
    for name, probs in seat_probs.items():
        entropy = 0.0
        for prob in probs.values():
            if prob > 0:
                entropy -= prob * log2(prob)
        entropies[name] = entropy
    return entropies


def top_allocations(
    outcomes: Counter,
    lists: list[str],
    limit: int = 10,
) -> list[dict[str, object]]:
    total = sum(outcomes.values())
    results: list[dict[str, object]] = []
    for alloc, count in outcomes.most_common(limit):
        results.append(
            {
                "allocation": dict(zip(lists, alloc)),
                "count": count,
                "probability": count / total,
            }
        )
    return results
