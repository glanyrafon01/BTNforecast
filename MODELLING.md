# BTNforecast Modelling Notes

This document explains the statistical approach used by the model in plain
language. It assumes the reader is comfortable with bachelor‑level mathematics
(basic probability, distributions, and linear algebra).

## Overview

The model produces a distribution over seat allocations in a 6‑seat
constituency. It does this by:

1) starting from a baseline vote‑share forecast,
2) applying a correlated bloc‑level swing,
3) sampling vote shares from a Dirichlet distribution around the swung forecast,
4) allocating seats using the D’Hondt method, and
5) repeating this many times to estimate probabilities.

The output is a Monte Carlo approximation to the probability of each possible
seat allocation.

## Notation

Let there be K lists (parties). Define:

- Base share vector: p = (p1, …, pK), with pi >= 0 and sum(pi) = 1.
- Seats: S = 6.
- Simulations: N.

We denote left‑bloc lists L and right‑bloc lists R. Each simulation produces a
vote share vector v and a seat allocation vector s.

## Step 1: Bloc‑level swing (correlated log‑normal factor)

We model two random swings, one for the left bloc and one for the right bloc.
They are drawn from a correlated bivariate normal:

    (xL, xR) ~ N(0, Sigma)

where Sigma has variance swing_sd^2 on the diagonal and correlation swing_rho:

    Sigma = [ s^2      rho*s^2 ]
            [ rho*s^2  s^2     ]

These swings are applied multiplicatively to the baseline shares using
exp(x), which ensures positivity and yields a log‑normal style swing:

    p'i = pi * exp(xL)  for i in L
    p'i = pi * exp(xR)  for i in R
    p'i = pi           for lists in neither bloc

The vector p' is renormalized to sum to 1. This step captures the idea that
parties within a bloc move together and that bloc swings can be correlated.

Interpretation:

- swing_sd controls the typical size of bloc swings.
- swing_rho controls whether bloc swings oppose (negative) or move together
  (positive).

## Step 2: Dirichlet sampling (within‑bloc and residual uncertainty)

After the bloc swing, the model samples a final vote‑share vector v from a
Dirichlet distribution:

    v ~ Dirichlet(alpha)
    alpha = concentration * p'

The Dirichlet distribution is a standard choice for random probability
vectors. The concentration parameter controls dispersion:

- Large concentration -> samples tightly clustered around p'.
- Small concentration -> more variable outcomes.

This step represents additional uncertainty around the swung forecast, such
as local variation, measurement noise, or unmodeled effects.

## Step 3: Seat allocation (D’Hondt)

Given a simulated vote share vector v, seats are allocated deterministically
using the D’Hondt method (highest averages). For each list i, compute:

    v_i / 1, v_i / 2, ..., v_i / S

Take the S largest quotients overall. Each quotient corresponds to one seat.
The number of times a list’s quotients appear in the top S is its seat count.

## Step 4: Monte Carlo estimation

Repeat Steps 1–3 for N simulations. Let C(a) be the count of how many times
seat allocation a occurs. Then the estimated probability of allocation a is:

    P(a) ≈ C(a) / N

From these samples we derive:

- Expected seats per list: E[seats_i]
- Probability of at least k seats: P(seats_i >= k)
- Most likely seat allocations
- Sensitivity metrics under small share changes

## Sensitivity analysis

The sensitivity output perturbs one list’s vote share by a small delta (±1–3
percentage points) and renormalizes the others. For each perturbation we rerun
simulations and compare expected seats. This approximates a local response
surface: how a small change in vote share affects expected seats.

## Targeting guidance

The PC targeting report simulates a simple transfer model:

- Increase PC by 1 percentage point.
- Decrease a single donor list by 1 percentage point.
- Keep all other lists unchanged.

The report ranks donors by the marginal increase in PC’s expected seats (and
changes in P(PC >= 1) and P(PC >= 2)). This is a model‑based marginal effect,
not a claim about persuasion likelihood.

## Limits and caveats

- The model is conditional on the baseline forecast; it does not learn the
  forecast itself.
- Bloc structure is assumed fixed and exogenous.
- The Dirichlet‑based variation is symmetric and does not encode asymmetric
  biases or systematic polling error.
- Results are probabilistic and should be combined with field intelligence.

## Mapping to configuration

Parameters in `forecast.yaml` correspond directly to the components above:

- `base_shares`: baseline p.
- `concentration`: Dirichlet concentration.
- `swing_sd`: bloc swing standard deviation.
- `swing_rho`: bloc swing correlation.
- `left_bloc`, `right_bloc`: bloc membership.
- `sims`: N, number of simulations.
