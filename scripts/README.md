# scripts/

## refresh-spec.py

Pulls fresh suspension recommendations from Specialized's calculator API and writes them to `data/spec-s3-raw.json`.

### What it does

For the SJ15 Comp (productId `4221395`), size S3, sweeps every integer lb from 101 to 240. For each lb, sends `weight: kg` where `kg = (lb + 0.5) / 2.20462` — i.e., samples in the **middle of each lb's bucket**.

Captures `shockPsi`, `shockReb`, `forkPsi`, `forkReb`, plus `mass`. PSI values are stored unrounded (server values verbatim); rebound is integer clicks. Round only at display time in the UI.

Output format (keyed by integer lb):

```json
{
  "productId": "4221395",
  "size": "S3",
  "fetchedAt": "...",
  "samplingMethod": "mid-bucket: kg = (lb + 0.5) / lbsPerKg",
  "byLbs": {
    "101": { "shockPsi": 95.6, "shockReb": 13, "forkPsi": 45.4, "forkReb": 13, "mass": ... },
    "102": { ... },
    ...
  }
}
```

**The `byLbs` key is the lb bucket the row represents** — i.e., the lb the server *returned* for that input. The actual API input was `kg = (lb + 0.5) / lbsPerKg`, not the lb itself. For example, the `"101"` row was produced by sending `kg = 46.0397`; the server applied `floor(46.0397 × 2.20462) = 101` and returned lb 101's data, which we then stored under the `"101"` key.

### Why mid-bucket sampling

Specialized's server buckets the input weight by `floor(kg * 2.20462)` to pick which lb's row to return. Sending `kg = lb / 2.20462` (the natural conversion) lands at the exact bucket boundary, which can fall in either bucket due to IEEE float rounding — for ~6 lbs in the 101–240 range, that meant pulling the previous lb's data instead of the requested lb's.

Adding `+0.5` to the lb before converting puts the query firmly in the middle of the intended bucket, immune to float-precision artifacts. Verified against a 420-row sweep (every lb at N.1, N.5, N.9) showing all three samples per lb return identical data.

### Run

From the repo root:

```bash
python3 scripts/refresh-spec.py
```

Takes ~30s (140 sequential HTTP requests with a 100ms delay between each, plus retries). Writes `data/spec-s3-raw.json`.

If you see `HTTP Error 403`, Specialized may have rotated their `x-code` token. Grab a fresh one by:

1. Open https://www.specialized.com/us/en/app/suspension-calculator in Chrome
2. Open DevTools → Network tab
3. Change the rider weight to trigger a request
4. Find the `GetSuspensionCalculations` call, copy its `x-code` request header
5. Paste it as the `X_CODE` constant at the top of `refresh-spec.py`

### When to refresh

- Specialized publishes a SJ15 firmware/chart update.
- You suspect the inline `SPEC_RAW` array in `index.html` has drifted.
- You want to capture a different bike — change `PRODUCT_ID` and `SIZE` constants and `OUTPUT_PATH` (e.g. `data/spec-s1-raw.json`) before running. Front fork values are size-independent; only rear shock psi and rebound differ across sizes.

### Updating the inline SPEC_RAW

The `SPEC_RAW` array in `index.html` is a transcription of `data/spec-s3-raw.json`'s `byLbs` values. After regenerating the JSON, manually update the inline array (or write a small generator script) — the format is `[shockPsi, forkPsi, shockReb, forkReb]` per lb, ordered 101..240.
