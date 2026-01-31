# BTNforecast

Election simulation for a 6-seat D'Hondt constituency with closed lists.

## Setup

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

Generate simulated seat outcomes and CSVs:

```bash
python simulate_seats.py
```

Create plots from the CSVs:

```bash
python plot_seats.py
```

## Model notes

The simulation uses a Dirichlet draw around the base forecast, plus a
correlated bloc swing applied before the Dirichlet step.

Bloc mapping:

- Left bloc: PC, GEW, Ll, LD
- Right bloc: RU, CU, Oth

Tunable parameters in `simulate_seats.py`:

- `CONCENTRATION`: lower values increase variation
- `SWING_SD`: bloc swing standard deviation
- `SWING_RHO`: correlation between left/right swings (negative = opposing)

## Outputs

- `seat_outcomes.csv`: outcome frequency by seat allocation
- `seat_probs.csv`: per-list seat probability distribution
- `expected_seats.png`: expected seats per list
- `seat_distribution.png`: stacked seat probabilities per list
