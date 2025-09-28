import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np

app = FastAPI()

# Enable CORS for POST requests from any website
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# Load the telemetry data from the JSON file
data_path = os.path.join(os.path.dirname(__file__), 'q-vercel-latency.json')
df = pd.read_json(data_path)

@app.post("/")
async def get_latency_metrics(request: Request):
    """
    Accepts a POST request with a JSON body like:
    {"regions": ["amer", "emea"], "threshold_ms": 173}

    Returns per-region metrics based on the input data.
    """
    body = await request.json()
    regions_to_process = body.get("regions", [])
    latency_threshold = body.get("threshold_ms", 0)

    results = {}

    for region in regions_to_process:
        # Filter the DataFrame for the current region
        region_df = df[df["region"] == region]

        if not region_df.empty:
            # Calculate metrics
            avg_latency = region_df["latency_ms"].mean()
            p95_latency = region_df["latency_ms"].quantile(0.95)
            # Convert uptime percentage to a mean value (e.g., 98.5 -> 0.985)
            avg_uptime = region_df["uptime_pct"].mean() / 100
            # Count how many records are above the threshold
            breaches = len(region_df[region_df["latency_ms"] > latency_threshold])

            results[region] = {
                "avg_latency": round(avg_latency, 2),
                "p95_latency": round(p95_latency, 2),
                "avg_uptime": round(avg_uptime, 4),
                "breaches": breaches,
            }

    return results

# A simple root endpoint to confirm the API is running
@app.get("/")
def read_root():
    return {"status": "ok"}
