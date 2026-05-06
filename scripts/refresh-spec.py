#!/usr/bin/env python3
"""Refresh data/spec-s3-raw.json from Specialized's suspension calculator API.

Sweeps every integer lb 101-240, sending kg = (lb + 0.5) / 2.20462. The +0.5
mid-bucket offset avoids float-precision edge cases that can land queries in
the wrong lb bucket (the server uses floor(kg * 2.20462) to bucket inputs).
"""

import datetime
import json
import sys
import time
import urllib.error
import urllib.request

PRODUCT_ID = "4221395"
SIZE = "S3"
HEIGHT_M = 1.72
LBS_PER_KG = 2.20462
LBS_RANGE = range(101, 241)
ENDPOINT = "https://www.specialized.com/api/graphql/GetSuspensionCalculations"
X_CODE = "eyJhbGciOiJIUzI1NiJ9._v39_v0.RFXZvbiszytbLs9VudXB-FEhvEErLRda4OJHcobDj_w~"
QUERY = (
    "query GetSuspensionCalculations($productId: String!, $size: String!, "
    "$height: Float!, $weight: Float!) { "
    "getSuspensionCalculations(productId: $productId size: $size "
    "height: $height weight: $weight) }"
)
OUTPUT_PATH = "data/spec-s3-raw.json"
SLEEP_BETWEEN = 0.1
MAX_RETRIES = 5


def fetch(weight_kg):
    body = json.dumps({
        "operationName": "GetSuspensionCalculations",
        "variables": {
            "productId": PRODUCT_ID,
            "size": SIZE,
            "height": HEIGHT_M,
            "weight": weight_kg,
        },
        "query": QUERY,
    }).encode()
    req = urllib.request.Request(
        ENDPOINT,
        data=body,
        headers={
            "content-type": "application/json",
            "x-code": X_CODE,
            "x-locale": "US:en",
            "accept": "*/*",
            "origin": "https://www.specialized.com",
            "referer": "https://www.specialized.com/us/en/app/suspension-calculator",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        },
        method="POST",
    )
    for attempt in range(MAX_RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status != 200:
                    raise RuntimeError(f"HTTP {resp.status}")
                payload = json.loads(resp.read())
                if payload.get("errors"):
                    raise RuntimeError(payload["errors"][0].get("message", "graphql error"))
                d = payload["data"]["getSuspensionCalculations"]
                return {
                    "shockPsi": float(d["Shock"]["Spring"]["Setting1"]["Value"]),
                    "shockReb": int(float(d["Shock"]["Damper"]["Setting1"]["Value"])),
                    "forkPsi": float(d["Fork"]["Spring"]["Setting1"]["Value"]),
                    "forkReb": int(float(d["Fork"]["Damper"]["Setting1"]["Value"])),
                    "mass": d["mass"],
                }
        except (urllib.error.URLError, RuntimeError, json.JSONDecodeError) as e:
            if attempt == MAX_RETRIES - 1:
                raise
            time.sleep(0.5 * (attempt + 1))
    return None


def main():
    by_lbs = {}
    for lbs in LBS_RANGE:
        kg = (lbs + 0.5) / LBS_PER_KG
        print(f"  lbs={lbs} (kg={kg:.6f}, mid-bucket)", file=sys.stderr, flush=True)
        by_lbs[str(lbs)] = fetch(kg)
        time.sleep(SLEEP_BETWEEN)

    out = {
        "productId": PRODUCT_ID,
        "size": SIZE,
        "fetchedAt": datetime.datetime.now(datetime.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "endpoint": ENDPOINT,
        "lbsPerKg": LBS_PER_KG,
        "samplingMethod": "mid-bucket: kg = (lb + 0.5) / lbsPerKg",
        "byLbsNote": "key is the lb bucket the row represents (matches the lb the server returned). The actual API input was kg = (lb + 0.5) / lbsPerKg, not lb.",
        "byLbs": by_lbs,
    }
    with open(OUTPUT_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"wrote {OUTPUT_PATH}: {len(by_lbs)} lbs rows", file=sys.stderr)


if __name__ == "__main__":
    main()
