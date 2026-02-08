import os
import uuid
from typing import Any, cast

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel

from btnforecast.config import override_config, parse_config_yaml
from btnforecast.workflow import run_forecast


class SimRequest(BaseModel):
    config_yaml: str
    sims: int | None = None
    sensitivity_sims: int | None = None
    seed: int | None = None
    run_plots: bool = True


app = FastAPI()


def _default_config_text() -> str:
    path = os.environ.get("FORECAST_CONFIG", "forecast.yaml")
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return handle.read()
    except FileNotFoundError:
        return ""


def _require_token(token: str | None) -> None:
    expected = os.environ.get("AUTH_TOKEN")
    if expected and token != expected:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    config_text = _default_config_text()
    template = """
<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>BTNforecast</title>
    <script src=\"https://cdn.plot.ly/plotly-2.30.0.min.js\"></script>
    <style>
      body { font-family: "Spectral", serif; margin: 32px; color: #12222b; background: linear-gradient(180deg, #f3f6f7, #e6edf0); }
      h1 { font-size: 28px; margin-bottom: 8px; }
      .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
      textarea { width: 100%; height: 320px; font-family: "Fira Mono", monospace; }
      label { display: block; font-weight: 600; margin-top: 12px; }
      input { width: 100%; padding: 6px; }
      button { background: #0b3b4c; color: #fff; border: none; padding: 10px 16px; font-weight: 600; cursor: pointer; }
      .card { background: #fff; border-radius: 10px; padding: 16px; box-shadow: 0 10px 20px rgba(16, 24, 32, 0.08); }
      .charts { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 24px; }
      pre { background: #0d1b22; color: #d6f5ff; padding: 12px; border-radius: 8px; overflow-x: auto; }
    </style>
    <link href=\"https://fonts.googleapis.com/css2?family=Fira+Mono:wght@400;500&family=Spectral:wght@400;600&display=swap\" rel=\"stylesheet\">
  </head>
  <body>
    <h1>BTNforecast</h1>
    <p>Run seat simulations with your latest forecast, then explore the results.</p>
    <div class=\"grid\">
      <div class=\"card\">
        <label for=\"config\">Forecast YAML</label>
        <textarea id=\"config\">__CONFIG_TEXT__</textarea>
        <label for=\"sims\">Simulations</label>
        <input id=\"sims\" type=\"number\" value=\"10000\" />
        <label for=\"sensitivity\">Sensitivity sims</label>
        <input id=\"sensitivity\" type=\"number\" value=\"2000\" />
        <label for=\"seed\">Seed (optional)</label>
        <input id=\"seed\" type=\"number\" placeholder=\"Leave blank for random\" />
        <label for=\"token\">Shared token</label>
        <input id=\"token\" type=\"password\" placeholder=\"Required when hosted\" />
        <div style=\"margin-top: 16px;\">
          <button id=\"run\">Run simulation</button>
        </div>
      </div>
      <div class=\"card\">
        <h3>Status</h3>
        <div id=\"status\">Idle</div>
        <h3>Summary</h3>
        <pre id=\"summary\">No run yet.</pre>
        <h3>Downloads</h3>
        <ul id=\"downloads\"></ul>
      </div>
    </div>
    <div class=\"charts\">
      <div class=\"card\"><div id=\"expectedChart\"></div></div>
      <div class=\"card\"><div id=\"dotChart\"></div></div>
    </div>
    <script>
      const statusEl = document.getElementById("status");
      const summaryEl = document.getElementById("summary");
      const downloadsEl = document.getElementById("downloads");

      function renderDownloads(outputs) {
        downloadsEl.innerHTML = "";
        Object.entries(outputs).forEach(([key, url]) => {
          const li = document.createElement("li");
          const link = document.createElement("a");
          link.href = url;
          link.innerText = key;
          link.target = "_blank";
          li.appendChild(link);
          downloadsEl.appendChild(li);
        });
      }

      function renderExpected(summary) {
        const lists = summary.lists;
        const expected = lists.map(name => summary.expected_seats[name]);
        const data = [{ x: lists, y: expected, type: "bar", marker: { color: "#0b3b4c" } }];
        Plotly.newPlot("expectedChart", data, { title: "Expected seats", margin: { t: 40 } });
      }

      function renderDots(lists, seatProbs) {
        const x = [];
        const y = [];
        const size = [];
        lists.forEach((name, idx) => {
          Object.entries(seatProbs[name]).forEach(([seats, prob]) => {
            x.push(Number(seats));
            y.push(idx);
            size.push(1200 * prob + 10);
          });
        });
        const trace = { x, y, mode: "markers", marker: { size, color: "#f08b32", opacity: 0.7 } };
        Plotly.newPlot("dotChart", [trace], {
          title: "Seat probability dots",
          yaxis: { tickmode: "array", tickvals: lists.map((_, i) => i), ticktext: lists },
          xaxis: { title: "Seats" },
          margin: { t: 40 }
        });
      }

      document.getElementById("run").addEventListener("click", async () => {
        statusEl.innerText = "Running...";
        const configYaml = document.getElementById("config").value;
        const sims = Number(document.getElementById("sims").value || 0) || null;
        const sensitivity = Number(document.getElementById("sensitivity").value || 0) || null;
        const seedValue = document.getElementById("seed").value;
        const seed = seedValue === "" ? null : Number(seedValue);
        const token = document.getElementById("token").value;

        const response = await fetch("/simulate", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(token ? { "X-Auth-Token": token } : {})
          },
          body: JSON.stringify({
            config_yaml: configYaml,
            sims,
            sensitivity_sims: sensitivity,
            seed,
            run_plots: true
          })
        });

        if (!response.ok) {
          const errorText = await response.text();
          statusEl.innerText = "Error";
          summaryEl.innerText = errorText;
          return;
        }

        const data = await response.json();
        statusEl.innerText = "Done";
        summaryEl.innerText = JSON.stringify(data.summary, null, 2);
        renderDownloads(data.outputs);
        renderExpected(data.summary);
        renderDots(data.summary.lists, data.seat_probs);
      });
    </script>
  </body>
</html>
"""
    return template.replace("__CONFIG_TEXT__", config_text)


@app.post("/simulate")
def simulate(request: SimRequest, x_auth_token: str | None = Header(default=None)) -> dict:
    _require_token(x_auth_token)
    config = parse_config_yaml(request.config_yaml)
    config = override_config(
        config,
        sims=request.sims,
        seed=request.seed,
        sensitivity_sims=request.sensitivity_sims,
    )
    run_id = uuid.uuid4().hex
    output_dir = os.path.join("outputs", run_id)
    result = run_forecast(
        config,
        output_dir=output_dir,
        run_plots=request.run_plots,
        run_sensitivity=True,
    )

    outputs_map = cast(dict[str, Any], result["outputs"])
    outputs = {
        key: f"/outputs/{run_id}/{os.path.basename(path)}"
        for key, path in outputs_map.items()
    }
    seat_probs = {
        name: {str(seats): prob for seats, prob in probs.items()}
        for name, probs in cast(dict[str, Any], result["seat_probs"]).items()
    }
    return {
        "run_id": run_id,
        "summary": result["summary"],
        "seat_probs": seat_probs,
        "outputs": outputs,
    }


@app.get("/outputs/{run_id}/{filename}")
def download(run_id: str, filename: str) -> FileResponse:
    path = os.path.join("outputs", run_id, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
