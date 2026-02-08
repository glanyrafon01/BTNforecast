from collections import Counter

from .analysis import expected_seats, seat_probs_from_outcomes
from .core import simulate_election


def _adjust_shares(
    base_shares: list[float],
    target_index: int,
    delta: float,
) -> list[float] | None:
    target = base_shares[target_index] + delta
    if target <= 0 or target >= 1:
        return None

    other_total = 1 - base_shares[target_index]
    if other_total <= 0:
        return None
    remaining_total = 1 - target
    scale = remaining_total / other_total

    adjusted = base_shares[:]
    for idx in range(len(base_shares)):
        if idx == target_index:
            adjusted[idx] = target
        else:
            adjusted[idx] = base_shares[idx] * scale
    return adjusted


def sensitivity_table(
    lists: list[str],
    base_shares: list[float],
    seats: int,
    sims: int,
    concentration: float,
    swing_sd: float,
    swing_rho: float,
    left_bloc: set[str],
    right_bloc: set[str],
    seed: int | None,
    deltas: list[float] | None = None,
) -> list[dict[str, float | str]]:
    if deltas is None:
        deltas = [-0.03, -0.02, -0.01, 0.01, 0.02, 0.03]

    base_outcomes = simulate_election(
        lists,
        base_shares,
        seats,
        sims,
        concentration,
        swing_sd,
        swing_rho,
        left_bloc,
        right_bloc,
        seed,
        seed_offset=1000,
    )
    base_probs = seat_probs_from_outcomes(base_outcomes, lists, seats)
    base_expected = expected_seats(base_probs)

    rows: list[dict[str, float | str]] = []
    for idx, name in enumerate(lists):
        for delta in deltas:
            adjusted = _adjust_shares(base_shares, idx, delta)
            if adjusted is None:
                continue
            outcomes = simulate_election(
                lists,
                adjusted,
                seats,
                sims,
                concentration,
                swing_sd,
                swing_rho,
                left_bloc,
                right_bloc,
                seed,
                seed_offset=2000 + idx * 100 + int(delta * 1000),
            )
            probs = seat_probs_from_outcomes(outcomes, lists, seats)
            expected = expected_seats(probs)
            rows.append(
                {
                    "list": name,
                    "delta_pp": delta * 100,
                    "expected_seats": expected[name],
                    "delta_expected": expected[name] - base_expected[name],
                }
            )
    return rows
