import csv
from collections import Counter

import numpy as np

LISTS = ["PC", "RU", "GEW", "CU", "Ll", "LD", "Oth"]
BASE_SHARES = [0.304, 0.236, 0.147, 0.088, 0.052, 0.136, 0.037]
CONCENTRATION = 50
SWING_SD = 0.03
SWING_RHO = -0.5

LEFT_BLOC = {"PC", "GEW", "Ll", "LD"}
RIGHT_BLOC = {"RU", "CU", "Oth"}


def dhondt_seats(votes, seats):
    quotients = []
    for i, v in enumerate(votes):
        for d in range(1, seats + 1):
            quotients.append((v / d, i))
    quotients.sort(reverse=True, key=lambda x: x[0])
    winners = [idx for _, idx in quotients[:seats]]
    seat_counts = [0] * len(votes)
    for idx in winners:
        seat_counts[idx] += 1
    return seat_counts


def simulate_election(base_shares, seats=6, sims=1000, concentration=300):
    alpha = np.array(base_shares) * concentration
    outcomes = Counter()
    for _ in range(sims):
        mean = np.array([0.0, 0.0])
        cov = np.array(
            [
                [SWING_SD**2, SWING_RHO * SWING_SD**2],
                [SWING_RHO * SWING_SD**2, SWING_SD**2],
            ]
        )
        left_swing, right_swing = np.random.multivariate_normal(mean, cov)

        swung = []
        for name, share in zip(LISTS, base_shares):
            if name in LEFT_BLOC:
                swung.append(share * np.exp(left_swing))
            else:
                swung.append(share * np.exp(right_swing))

        swung = np.array(swung)
        swung /= swung.sum()

        alpha = swung * concentration
        shares = np.random.dirichlet(alpha)
        seats_alloc = tuple(dhondt_seats(shares, seats))
        outcomes[seats_alloc] += 1
    return outcomes


def main():
    outcomes = simulate_election(
        BASE_SHARES,
        seats=6,
        sims=1000,
        concentration=CONCENTRATION,
    )
    total = sum(outcomes.values())

    with open("seat_outcomes.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(LISTS + ["count", "probability"])
        for alloc, count in outcomes.most_common():
            writer.writerow(list(alloc) + [count, count / total])

    with open("seat_probs.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["list", "seats", "probability"])
        for i, name in enumerate(LISTS):
            counts = [0] * 7
            for alloc, count in outcomes.items():
                counts[alloc[i]] += count
            for seats, count in enumerate(counts):
                writer.writerow([name, seats, count / total])

    for seats_alloc, count in outcomes.most_common(10):
        print(dict(zip(LISTS, seats_alloc)), count)


if __name__ == "__main__":
    main()
