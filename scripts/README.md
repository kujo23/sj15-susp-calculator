# scripts/

## refresh-spec.py

Pulls fresh suspension recommendations from Specialized's calculator API and writes them to `data/spec-s3-raw.json`.

### What it does

For the SJ15 Comp (productId `4221395`), size S3:

1. Sweeps every integer kg from 46 to 110 — sends `weight: <int>` to the GraphQL endpoint.
2. Sweeps every integer lbs from 101 to 240 — converts to fractional kg (`lbs / 2.20462`) and sends.

Captures shock psi, shock rebound, fork psi, fork rebound for each. **No rounding** — server values are stored verbatim. Round only at display time in the UI.

The output is keyed two ways:

```json
{
  "byKg": { "46": { "shockPsi": 95.6, ... }, "47": { ... }, ... },
  "byLbs": { "101": { "shockPsi": 95.6, ... }, "102": { ... }, ... }
}
```

So the calculator can do `data.byKg[83]` or `data.byLbs[183]` — O(1) lookup with no conversion at lookup time.

### Run

From the repo root:

```bash
python3 scripts/refresh-spec.py
```

Takes ~1 minute (205 sequential HTTP requests with a 100ms delay between each, plus retries). Writes `data/spec-s3-raw.json`.

If you see `HTTP Error 403`, Specialized may have rotated their `x-code` token. Grab a fresh one by:

1. Open https://www.specialized.com/us/en/app/suspension-calculator in Chrome
2. Open DevTools → Network tab
3. Change the rider weight to trigger a request
4. Find the `GetSuspensionCalculations` call, copy its `x-code` request header
5. Paste it as the `X_CODE` constant at the top of `refresh-spec.py`

### When to refresh

- Specialized publishes a SJ15 firmware/chart update.
- You suspect the local `SPEC` table has drifted.
- You want to check a different bike — change `PRODUCT_ID` and `SIZE` constants and re-run.

### Re-running for other sizes

The script is hardcoded to S3. To capture another size, change the `SIZE` constant (`S1`–`S6`) and `OUTPUT_PATH` (e.g. `data/spec-s1-raw.json`) before running. Front fork values are size-independent; only rear shock psi and rebound differ.
