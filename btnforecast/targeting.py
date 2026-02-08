from collections import Counter

from .analysis import expected_seats, probability_at_least, seat_probs_from_outcomes
from .core import simulate_election
from .outputs import write_text_file


def _transfer_shares(
    base_shares: list[float],
    from_index: int,
    to_index: int,
    delta: float,
) -> list[float] | None:
    if from_index == to_index:
        return None
    if base_shares[from_index] <= delta:
        return None
    adjusted = base_shares[:]
    adjusted[from_index] -= delta
    adjusted[to_index] += delta
    return adjusted


def _simulate_metrics(
    lists: list[str],
    shares: list[float],
    seats: int,
    sims: int,
    concentration: float,
    swing_sd: float,
    swing_rho: float,
    left_bloc: set[str],
    right_bloc: set[str],
    seed: int | None,
    seed_offset: int,
) -> dict[str, dict[str, float]]:
    outcomes = simulate_election(
        lists,
        shares,
        seats,
        sims,
        concentration,
        swing_sd,
        swing_rho,
        left_bloc,
        right_bloc,
        seed,
        seed_offset=seed_offset,
    )
    seat_probs = seat_probs_from_outcomes(outcomes, lists, seats)
    return {
        "expected_seats": expected_seats(seat_probs),
        "prob_ge_1": probability_at_least(seat_probs, 1),
        "prob_ge_2": probability_at_least(seat_probs, 2),
    }


def generate_pc_targeting_report(
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
    output_path: str,
    delta: float = 0.01,
) -> str:
    if "PC" not in lists:
        report = "PC not found in lists. No targeting report generated."
        write_text_file(report, output_path)
        return output_path

    pc_index = lists.index("PC")
    baseline = _simulate_metrics(
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
        seed_offset=3000,
    )
    baseline_expected = baseline["expected_seats"]["PC"]
    baseline_ge_1 = baseline["prob_ge_1"]["PC"]
    baseline_ge_2 = baseline["prob_ge_2"]["PC"]

    results: list[dict[str, float | str]] = []
    for idx, name in enumerate(lists):
        if idx == pc_index:
            continue
        adjusted = _transfer_shares(base_shares, idx, pc_index, delta)
        if adjusted is None:
            continue
        metrics = _simulate_metrics(
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
            seed_offset=4000 + idx,
        )
        pc_expected = metrics["expected_seats"]["PC"]
        pc_ge_1 = metrics["prob_ge_1"]["PC"]
        pc_ge_2 = metrics["prob_ge_2"]["PC"]
        results.append(
            {
                "donor": name,
                "delta_expected": pc_expected - baseline_expected,
                "delta_prob_ge_1": pc_ge_1 - baseline_ge_1,
                "delta_prob_ge_2": pc_ge_2 - baseline_ge_2,
            }
        )

    results.sort(key=lambda item: float(item["delta_expected"]), reverse=True)

    lines = [
        "PC Targeting Guidance (model-based)",
        "",
        f"Scenario: PC gains {delta * 100:.1f}pp from a single other list.",
        "Ranking is by increase in expected seats for PC.",
        "",
        "Rank | Donor | +Expected seats | +P(PC>=1) | +P(PC>=2)",
        "-----|-------|-----------------|-----------|----------",
    ]
    for rank, item in enumerate(results, start=1):
        lines.append(
            f"{rank:>4} | {item['donor']:<5} | {item['delta_expected']:+.3f}"
            f"         | {item['delta_prob_ge_1']:+.3f}    |"
            f" {item['delta_prob_ge_2']:+.3f}"
        )

    lines.extend(
        [
            "",
            "Notes:",
            "- This compares hypothetical transfers of a fixed vote share.",
            "- It does not say which voters are persuadable in practice.",
            "- Use alongside field intel and polling, not as a standalone guide.",
        ]
    )

    report = "\n".join(lines)
    write_text_file(report, output_path)
    return output_path
