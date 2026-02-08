import csv
import json
import os
from collections import Counter


def ensure_output_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_seat_outcomes_csv(
    outcomes: Counter,
    lists: list[str],
    path: str,
) -> None:
    total = sum(outcomes.values())
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(lists + ["count", "probability"])
        for alloc, count in outcomes.most_common():
            writer.writerow(list(alloc) + [count, count / total])


def write_seat_probs_csv(
    seat_probs: dict[str, dict[int, float]],
    path: str,
) -> None:
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["list", "seats", "probability"])
        for name, probs in seat_probs.items():
            for seats, prob in probs.items():
                writer.writerow([name, seats, prob])


def write_summary_json(summary: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)


def write_sensitivity_csv(rows: list[dict], path: str) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
