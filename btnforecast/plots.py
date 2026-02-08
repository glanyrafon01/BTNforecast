import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_seat_distributions(
    seat_probs: dict[str, dict[int, float]],
    output_dir: str,
) -> dict[str, str]:
    lists = list(seat_probs.keys())
    max_seats = max(seats for probs in seat_probs.values() for seats in probs.keys())

    expected = [
        sum(seats * seat_probs[name].get(seats, 0.0) for seats in range(max_seats + 1))
        for name in lists
    ]

    expected_path = os.path.join(output_dir, "expected_seats.png")
    plt.figure(figsize=(8, 4))
    plt.bar(lists, expected)
    plt.title("Expected Seats by List")
    plt.ylabel("Expected seats")
    plt.tight_layout()
    plt.savefig(expected_path, dpi=150)
    plt.close()

    distribution_path = os.path.join(output_dir, "seat_distribution.png")
    plt.figure(figsize=(10, 5))
    bottom = [0.0] * len(lists)
    for seats in range(max_seats + 1):
        probs = [seat_probs[name].get(seats, 0.0) for name in lists]
        plt.bar(lists, probs, bottom=bottom, label=f"{seats} seats")
        bottom = [bottom[i] + probs[i] for i in range(len(lists))]

    plt.title("Seat Distribution by List")
    plt.ylabel("Probability")
    plt.legend(title="Seats", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(distribution_path, dpi=150)
    plt.close()

    dots_path = os.path.join(output_dir, "seat_prob_dots.png")
    plt.figure(figsize=(10, 5))
    x_vals: list[int] = []
    y_vals: list[int] = []
    sizes: list[float] = []
    for y, name in enumerate(lists):
        for seats in range(max_seats + 1):
            prob = seat_probs[name].get(seats, 0.0)
            x_vals.append(seats)
            y_vals.append(y)
            sizes.append(1200 * prob + 10)

    plt.scatter(x_vals, y_vals, s=sizes, alpha=0.7)
    plt.yticks(range(len(lists)), lists)
    plt.xticks(range(max_seats + 1))
    plt.xlabel("Seats")
    plt.ylabel("List")
    plt.title("Seat Probability Dot Plot")
    plt.tight_layout()
    plt.savefig(dots_path, dpi=150)
    plt.close()

    return {
        "expected_seats_png": expected_path,
        "seat_distribution_png": distribution_path,
        "seat_prob_dots_png": dots_path,
    }
