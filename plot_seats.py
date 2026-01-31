import csv
from collections import defaultdict

import matplotlib.pyplot as plt


def main():
    seat_probs = defaultdict(dict)
    lists = []

    with open("seat_probs.csv", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["list"]
            seats = int(row["seats"])
            prob = float(row["probability"])
            seat_probs[name][seats] = prob
            if name not in lists:
                lists.append(name)

    expected = []
    for name in lists:
        exp = sum(seats * seat_probs[name].get(seats, 0.0) for seats in range(7))
        expected.append(exp)

    plt.figure(figsize=(8, 4))
    plt.bar(lists, expected)
    plt.title("Expected Seats by List")
    plt.ylabel("Expected seats")
    plt.tight_layout()
    plt.savefig("expected_seats.png", dpi=150)

    plt.figure(figsize=(10, 5))
    bottom = [0] * len(lists)
    for seats in range(7):
        probs = [seat_probs[name].get(seats, 0.0) for name in lists]
        plt.bar(lists, probs, bottom=bottom, label=f"{seats} seats")
        bottom = [bottom[i] + probs[i] for i in range(len(lists))]

    plt.title("Seat Distribution by List")
    plt.ylabel("Probability")
    plt.legend(title="Seats", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig("seat_distribution.png", dpi=150)


if __name__ == "__main__":
    main()
