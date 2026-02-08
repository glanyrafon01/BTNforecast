from collections import Counter

from .analysis import (
    allocation_entropy,
    expected_seats,
    probability_at_least,
    seat_entropy,
    seat_probs_from_outcomes,
    top_allocations,
)
from .config import ForecastConfig
from .core import simulate_from_config
from .outputs import (
    ensure_output_dir,
    write_seat_outcomes_csv,
    write_seat_probs_csv,
    write_summary_json,
    write_sensitivity_csv,
)
from .plots import plot_seat_distributions
from .sensitivity import sensitivity_table
from .targeting import generate_pc_targeting_report


def run_forecast(
    config: ForecastConfig,
    output_dir: str,
    run_plots: bool = True,
    run_sensitivity: bool = True,
) -> dict[str, object]:
    ensure_output_dir(output_dir)
    outcomes: Counter = simulate_from_config(config)
    seat_probs = seat_probs_from_outcomes(outcomes, config.lists, config.seats)

    summary = {
        "lists": config.lists,
        "expected_seats": expected_seats(seat_probs),
        "prob_ge_1": probability_at_least(seat_probs, 1),
        "prob_ge_2": probability_at_least(seat_probs, 2),
        "seat_entropy": seat_entropy(seat_probs),
        "allocation_entropy": allocation_entropy(outcomes),
        "top_allocations": top_allocations(outcomes, config.lists, limit=10),
        "config": {
            "seats": config.seats,
            "sims": config.sims,
            "concentration": config.concentration,
            "swing_sd": config.swing_sd,
            "swing_rho": config.swing_rho,
            "seed": config.seed,
        },
    }

    outputs = {}
    seat_outcomes_path = f"{output_dir}/seat_outcomes.csv"
    seat_probs_path = f"{output_dir}/seat_probs.csv"
    summary_path = f"{output_dir}/summary.json"
    write_seat_outcomes_csv(outcomes, config.lists, seat_outcomes_path)
    write_seat_probs_csv(seat_probs, seat_probs_path)
    write_summary_json(summary, summary_path)
    outputs.update(
        {
            "seat_outcomes_csv": seat_outcomes_path,
            "seat_probs_csv": seat_probs_path,
            "summary_json": summary_path,
        }
    )

    sensitivity_rows: list[dict] = []
    if run_sensitivity:
        sensitivity_rows = sensitivity_table(
            config.lists,
            config.base_shares,
            config.seats,
            config.sensitivity_sims,
            config.concentration,
            config.swing_sd,
            config.swing_rho,
            config.left_bloc,
            config.right_bloc,
            config.seed,
        )
        sensitivity_path = f"{output_dir}/sensitivity.csv"
        write_sensitivity_csv(sensitivity_rows, sensitivity_path)
        outputs["sensitivity_csv"] = sensitivity_path

    if run_plots:
        plot_paths = plot_seat_distributions(seat_probs, output_dir)
        outputs.update(plot_paths)

    targeting_path = f"{output_dir}/pc_targeting.txt"
    generate_pc_targeting_report(
        config.lists,
        config.base_shares,
        config.seats,
        config.sensitivity_sims,
        config.concentration,
        config.swing_sd,
        config.swing_rho,
        config.left_bloc,
        config.right_bloc,
        config.seed,
        targeting_path,
        delta=0.01,
    )
    outputs["pc_targeting_txt"] = targeting_path

    return {
        "summary": summary,
        "seat_probs": seat_probs,
        "sensitivity": sensitivity_rows,
        "outputs": outputs,
    }
