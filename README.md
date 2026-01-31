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

## Outputs

- `seat_outcomes.csv`: outcome frequency by seat allocation
- `seat_probs.csv`: per-list seat probability distribution
- `expected_seats.png`: expected seats per list
- `seat_distribution.png`: stacked seat probabilities per list
