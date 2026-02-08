import argparse
from typing import Any, cast

from .config import load_config, override_config
from .outputs import ensure_output_dir
from .plots import plot_seat_distributions
from .workflow import run_forecast


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="btnforecast")
    subparsers = parser.add_subparsers(dest="command", required=True)

    simulate_parser = subparsers.add_parser("simulate", help="Run simulations")
    simulate_parser.add_argument("--config", default="forecast.yaml")
    simulate_parser.add_argument("--out", default=".")
    simulate_parser.add_argument("--sims", type=int)
    simulate_parser.add_argument("--seed", type=int)
    simulate_parser.add_argument("--sensitivity-sims", type=int)
    simulate_parser.add_argument("--no-sensitivity", action="store_true")
    simulate_parser.add_argument("--no-plots", action="store_true")

    plot_parser = subparsers.add_parser("plot", help="Plot from seat_probs.csv")
    plot_parser.add_argument("--input", default="seat_probs.csv")
    plot_parser.add_argument("--out", default=".")

    return parser.parse_args()


def _load_seat_probs(path: str) -> dict[str, dict[int, float]]:
    import csv

    seat_probs: dict[str, dict[int, float]] = {}
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            name = row["list"]
            seats = int(row["seats"])
            prob = float(row["probability"])
            seat_probs.setdefault(name, {})[seats] = prob
    return seat_probs


def _handle_simulate(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    config = override_config(
        config,
        sims=args.sims,
        seed=args.seed,
        sensitivity_sims=args.sensitivity_sims,
    )
    result = run_forecast(
        config,
        output_dir=args.out,
        run_plots=not args.no_plots,
        run_sensitivity=not args.no_sensitivity,
    )
    outputs = cast(dict[str, Any], result["outputs"])
    summary_path = outputs.get("summary_json")
    if summary_path:
        with open(summary_path, "r", encoding="utf-8") as handle:
            print(handle.read())


def _handle_plot(args: argparse.Namespace) -> None:
    ensure_output_dir(args.out)
    seat_probs = _load_seat_probs(args.input)
    plot_seat_distributions(seat_probs, args.out)


def main() -> None:
    args = _parse_args()
    if args.command == "simulate":
        _handle_simulate(args)
    elif args.command == "plot":
        _handle_plot(args)
    else:
        raise SystemExit("Unknown command")


if __name__ == "__main__":
    main()
