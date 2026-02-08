import argparse
from typing import Any, cast

from btnforecast.config import load_config, override_config
from btnforecast.workflow import run_forecast


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simulate D'Hondt outcomes")
    parser.add_argument("--config", default="forecast.yaml")
    parser.add_argument("--out", default=".")
    parser.add_argument("--sims", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--sensitivity-sims", type=int)
    parser.add_argument("--no-sensitivity", action="store_true")
    parser.add_argument("--no-plots", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
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
    summary = cast(dict[str, Any], result["summary"])
    for alloc in summary.get("top_allocations", []):
        print(alloc.get("allocation"), alloc.get("count"))


if __name__ == "__main__":
    main()
