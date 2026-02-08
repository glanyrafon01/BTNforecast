# BTNforecast Instructions

This document explains the modelling approach in plain language and gives
step-by-step instructions for running a simulation.

## A plain-English overview

This tool estimates how seats might be allocated in a 6-seat constituency
using the D'Hondt method and closed lists. It does this by running many
simulations rather than producing a single prediction. Each simulation is a
plausible election outcome based on your base forecast and a set of
assumptions about uncertainty and shared swings between parties.

Key ideas in simple terms:

- You start with a base forecast (the expected vote share for each list).
- We allow the forecast to shift in a realistic way before each simulation.
- We then allocate seats using the D'Hondt rule for that simulated outcome.
- After thousands of runs, we summarize how often each outcome occurs.

This gives you answers like:

- Expected seats for each list.
- Probability a list wins at least 1 seat (or 2 seats, etc.).
- The most common seat allocations.
- How sensitive expected seats are to small changes in vote share.

## What the model assumes

1) The base forecast is the starting point
   - The values in `forecast.yaml` are the best estimate of vote shares.
   - They should add up to 100% (the tool will renormalize if they do not).

2) Shared swings happen within blocs
   - Lists are grouped into a left bloc and a right bloc.
   - Before each simulation, the model applies a shared swing to the left bloc
     and a shared swing to the right bloc.
   - This captures the idea that parties in the same bloc often move together.

3) There is additional random variation around the swung forecast
   - After the bloc swing, the model draws a random vote share around that new
     forecast using a standard probability distribution (Dirichlet).
   - This accounts for noise and day-to-day uncertainty in polling or turnout.

4) Seats are allocated using D'Hondt
   - Each simulated vote share is converted into seats using the D'Hondt method.
   - The seat allocation is deterministic given the simulated vote shares.

## What the key settings mean

All key settings live in `forecast.yaml`:

- `base_shares`: The expected vote share for each list.
- `sims`: Number of simulations (higher = smoother results, slower).
- `concentration`: Think of this as "how steady is the forecast day to day?"
  - Use a higher value if you believe support is stable and small surprises are
    more likely than big swings.
  - Use a lower value if you think the campaign environment is volatile and
    large shifts are plausible.
  - Typical range: 20 to 200. Common example: 50.
  - Real-world signals: stable polling, quiet news cycles, and predictable
    turnout push this higher. A breaking scandal, a major policy reversal, or a
    sudden shift in the national mood makes outcomes less predictable and
    pushes this lower.
- `swing_sd`: Think of this as "how big could a bloc-wide swing be?"
  - Use a smaller number if you expect only gentle drift between blocs.
  - Use a larger number if a single event could noticeably shift opinion.
  - Typical range: 0.01 to 0.06. Common example: 0.03.
  - Real-world signals: a strong campaign launch, a high-profile endorsement,
    or a debated policy win can move an entire bloc together, so increase this.
    A fragmented media environment or low salience issues usually mean smaller
    bloc-wide moves, so reduce it.
- `swing_rho`: Think of this as "do blocs move in opposite directions or
  together?"
  - A negative value says gains for one bloc usually mean losses for the other.
  - A positive value says they often rise or fall together (for example, due to
    turnout changes affecting both blocs).
  - Typical range: -0.9 to 0.9. Common example: -0.5.
  - Real-world signals: highly polarized races or clear two-bloc narratives
    make this more negative because gains for one side usually come from the
    other. Cross-cutting persuasion events that can move voters toward or away
    from multiple blocs at once (for example a widely liked economic policy, or
    a broad loss of trust affecting many parties) make this less negative or
    even positive.
- `left_bloc` / `right_bloc`: Which lists move together.

## How to run a simulation (CLI)

1) Install dependencies (first time only)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) Edit the forecast

- Open `forecast.yaml` and update `base_shares` and other parameters.

3) Run the simulation

```bash
python -m btnforecast simulate --config forecast.yaml --out outputs
```

4) View outputs

- `outputs/summary.json` for the headline probabilities.
- `outputs/seat_outcomes.csv` and `outputs/seat_probs.csv` for raw results.
- `outputs/expected_seats.png`, `outputs/seat_distribution.png`,
  `outputs/seat_prob_dots.png` for charts.
- `outputs/sensitivity.csv` for how sensitive expected seats are to small
  vote-share changes.
- `outputs/pc_targeting.txt` for a model-based ranking of which single-party
  vote transfers would most increase PC's expected seats.

## How to run the web UI

Hosted deployment: `https://btnforecast.onrender.com/`

1) Start the server

```bash
AUTH_TOKEN=your-shared-token uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

2) Open the UI

- Visit `http://localhost:8000`.
- Paste the shared token into the UI, update the YAML, and run simulations.

## Authentication token (hosted deployment)

The hosted UI requires a shared token. Paste it into the "Shared token" field
in the web interface before running a simulation. This value should have been
provided to you by the service owner or team lead.

## How to interpret the main outputs

- Expected seats: the average seats across all simulations.
- Probability of at least 1 seat: how often a list wins any seat at all.
- Top allocations: the most common seat splits across all lists.
- Sensitivity table: how expected seats change with small vote shifts.

## Practical tips for campaign planning

- Use more simulations (`sims`) for stable comparisons between scenarios.
- Focus on lists near a 0/1 seat boundary for targeting decisions.
- Use `sensitivity.csv` to see which lists are most affected by small swings.
