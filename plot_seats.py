import argparse
import csv

from btnforecast.outputs import ensure_output_dir
from btnforecast.plots import plot_seat_distributions


def _load_seat_probs(path: str) -> dict[str, dict[int, float]]:
    seat_probs: dict[str, dict[int, float]] = {}
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            name = row["list"]
            seats = int(row["seats"])
            prob = float(row["probability"])
            seat_probs.setdefault(name, {})[seats] = prob
    return seat_probs


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plot seat distributions")
    parser.add_argument("--input", default="seat_probs.csv")
    parser.add_argument("--out", default=".")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    ensure_output_dir(args.out)
    seat_probs = _load_seat_probs(args.input)
    plot_seat_distributions(seat_probs, args.out)


if __name__ == "__main__":
    main()
