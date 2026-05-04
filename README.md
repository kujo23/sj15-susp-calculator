# SJ15 Suspension Calculator

A single-file HTML tool for dialing in the suspension on a Specialized **Stumpjumper 15** (size S3, ~175 cm rider). Looks up recommended pressure and rebound clicks for the **Genie FLOAT** rear shock and **Fox Rhythm 36** fork, given rider + gear weight.

## Features

- **Two input modes:** by rider weight (with optional gear weight added), or by current air pressure
- **Unit toggle:** lbs / kg
- **Side-by-side fork data:** the official Stumpjumper 15 chart vs Fox's own Rhythm 36 chart, so you can compare
- **Interactive charts** for shock and fork — hover/scrub to see the values at any weight or pressure
- **Persists inputs** to `localStorage`, so it remembers your last setup
- **Out-of-range warnings** when weight falls outside the spec table

## Usage

Open `index.html` in any modern browser. No build step, no dependencies — it's a single self-contained file.

To host it, drop the file on any static server (GitHub Pages, Netlify, S3, etc.) or just double-click it locally.

**Live version:** [kujo23.github.io/sj15-susp-calculator](https://kujo23.github.io/sj15-susp-calculator/)

## Data sources

- Shock and SJ15 fork values: Specialized's published Stumpjumper 15 setup chart
- Fox fork values: Fox Rhythm 36 setup chart

Values outside the published weight ranges are clamped or marked out-of-range — treat any extrapolation as a starting point only.

## Disclaimer

Suspension setup is personal. Use these numbers as a baseline; tune from there based on how the bike actually feels.
