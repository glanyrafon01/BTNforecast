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

## Config-driven workflow

Edit `forecast.yaml` to update the core forecast and model settings. Then run:

```bash
python -m btnforecast simulate --config forecast.yaml --out outputs
```

Create plots from an output directory:

```bash
python -m btnforecast plot --input outputs/seat_probs.csv --out outputs
```

## Web UI

Start the web app locally:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Optional environment variables:

- `AUTH_TOKEN` to require a shared token for API calls
- `FORECAST_CONFIG` to set the default YAML shown in the UI

## Model notes

The simulation uses a Dirichlet draw around the base forecast, plus a
correlated bloc swing applied before the Dirichlet step.

Bloc mapping:

- Left bloc: PC, GEW, Ll, LD
- Right bloc: RU, CU, Oth

Tunable parameters now live in `forecast.yaml`:

- `CONCENTRATION`: lower values increase variation
- `SWING_SD`: bloc swing standard deviation
- `SWING_RHO`: correlation between left/right swings (negative = opposing)

## Outputs

- `seat_outcomes.csv`: outcome frequency by seat allocation
- `seat_probs.csv`: per-list seat probability distribution
- `expected_seats.png`: expected seats per list
- `seat_distribution.png`: stacked seat probabilities per list
- `seat_prob_dots.png`: per-seat probability dot plot
- `summary.json`: decision-support summary stats
- `sensitivity.csv`: expected-seat deltas for +/- vote-share shifts
