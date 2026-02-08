from collections import Counter

import numpy as np

from .config import ForecastConfig


def dhondt_seats(votes: list[float], seats: int) -> list[int]:
    quotients: list[tuple[float, int]] = []
    for i, v in enumerate(votes):
        for d in range(1, seats + 1):
            quotients.append((v / d, i))
    quotients.sort(reverse=True, key=lambda x: x[0])
    winners = [idx for _, idx in quotients[:seats]]
    seat_counts = [0] * len(votes)
    for idx in winners:
        seat_counts[idx] += 1
    return seat_counts


def _make_rng(seed: int | None, offset: int) -> np.random.Generator:
    if seed is None:
        return np.random.default_rng()
    return np.random.default_rng(seed + offset)


def _apply_bloc_swing(
    lists: list[str],
    base_shares: list[float],
    left_bloc: set[str],
    right_bloc: set[str],
    swing_sd: float,
    swing_rho: float,
    rng: np.random.Generator,
) -> np.ndarray:
    mean = np.array([0.0, 0.0])
    cov = np.array(
        [
            [swing_sd**2, swing_rho * swing_sd**2],
            [swing_rho * swing_sd**2, swing_sd**2],
        ]
    )
    left_swing, right_swing = rng.multivariate_normal(mean, cov)

    swung = []
    for name, share in zip(lists, base_shares):
        if name in left_bloc:
            swung.append(share * np.exp(left_swing))
        elif name in right_bloc:
            swung.append(share * np.exp(right_swing))
        else:
            swung.append(share)

    swung = np.array(swung)
    swung /= swung.sum()
    return swung


def simulate_election(
    lists: list[str],
    base_shares: list[float],
    seats: int,
    sims: int,
    concentration: float,
    swing_sd: float,
    swing_rho: float,
    left_bloc: set[str],
    right_bloc: set[str],
    seed: int | None = None,
    seed_offset: int = 0,
) -> Counter:
    rng = _make_rng(seed, seed_offset)
    outcomes: Counter = Counter()

    for _ in range(sims):
        swung = _apply_bloc_swing(
            lists,
            base_shares,
            left_bloc,
            right_bloc,
            swing_sd,
            swing_rho,
            rng,
        )
        alpha = swung * concentration
        shares = rng.dirichlet(alpha)
        seats_alloc = tuple(dhondt_seats(shares, seats))
        outcomes[seats_alloc] += 1

    return outcomes


def simulate_from_config(config: ForecastConfig, seed_offset: int = 0) -> Counter:
    return simulate_election(
        lists=config.lists,
        base_shares=config.base_shares,
        seats=config.seats,
        sims=config.sims,
        concentration=config.concentration,
        swing_sd=config.swing_sd,
        swing_rho=config.swing_rho,
        left_bloc=config.left_bloc,
        right_bloc=config.right_bloc,
        seed=config.seed,
        seed_offset=seed_offset,
    )
