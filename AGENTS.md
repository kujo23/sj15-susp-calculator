# Agent guidelines — SJ15 Suspension Calculator

> Rules for Claude Code (and any other coding agent) working on this repo. Read this **before** writing any code in a new session.

---

## 1. Project context

A single-file HTML/CSS/JS tool for dialling in suspension on a Specialized Stumpjumper 15 (size S3, ~175 cm rider). It looks up recommended air pressure and rebound clicks for the Genie FLOAT rear shock and Fox Rhythm 36 fork from two data sources — Specialized's published SJ15 chart and Fox's own Rhythm 36 chart — based on rider + gear weight. The output is a number the user sets on their bike; correctness of the lookup math matters more than anything else.

---

## 2. Stack

- **Runtime:** Browser (modern Chrome / Safari / Firefox)
- **Language:** Vanilla JavaScript (ES6+), HTML5, CSS3
- **Framework:** None
- **Styling:** Plain CSS, inline in `index.html`
- **Testing:** Manual browser checklist (no automated test suite)
- **Tooling:** `html-validate` via CI (npx, no local install needed)
- **Hosting:** GitHub Pages — `https://kujo23.github.io/sj15-susp-calculator/`

---

## 3. Architecture rules

- **One file.** Everything lives in `index.html`. Do not split into separate `.js` or `.css` files without an explicit ask — that would require introducing a build step or module bundler.
- **No npm.** There is no `package.json` and that's intentional. Do not add one, do not suggest Husky, Prettier, or any npm-based tooling without explicit user approval.
- **Data tables are the source of truth.** `SPEC` (Specialized SJ15 data) and `FOX` (Fox Rhythm 36 data) are defined near the top of the script. Any lookup function must derive its range bounds from these arrays (`SPEC_MIN_LBS`, `SPEC_MAX_LBS`, `FOX_MIN_LBS`, `FOX_MAX_LBS`), not from hard-coded numbers.
- **Constants over magic numbers.** Unit conversions (`LBS_PER_KG = 2.20462`) and range bounds must use named constants.
- **No build artefacts.** Nothing to `.gitignore` beyond `.DS_Store` and `.obsidian/`.

---

## 4. Pre-merge quality gate

Before declaring any change "done":

```bash
# 1. HTML validation (catches structural errors, missing attrs, bad nesting)
npx --yes html-validate --config .html-validate.json index.html

# 2. Visual smoke-check in the browser
#    Open index.html directly (double-click) or via the local server:
python3 -m http.server 8743   # then visit http://localhost:8743/index.html
```

Manual checklist:
- [ ] By-weight mode: enter a weight in range → cards show PSI + clicks
- [ ] By-weight mode: enter a weight out of range → cards show `—` and OOR notice; chart marker is hidden
- [ ] PSI mode: enter a shock PSI → cards update correctly
- [ ] Unit toggle (lbs ↔ kg): values convert, min/max/step update, legends read correctly
- [ ] Series toggle (SJ15 / Fox): each can be hidden; hiding both shows empty legend, no crash
- [ ] localStorage: reload the page, inputs restore to last-used values
- [ ] Mobile: resize to 375px wide; confirm inputs, labels, and cards are readable

CI runs `html-validate` on every push (see `.github/workflows/ci.yml`). It must be green before merge.

---

## 5. Testing philosophy

There is no automated test suite. The logic is tightly coupled to the DOM inside a single file, making unit tests impractical without a significant refactor.

**If correctness is in doubt**, verify against the raw data tables in the source: check that `specAt(wLbs)` and `foxAt(wLbs)` return the expected row for a given weight, and that `nearestReb` / `foxRebByPsi` produce values consistent with the `SPEC` and `FOX` arrays.

When tests are eventually added, set initial coverage thresholds at the prevailing level — never lower them after.

---

## 6. Code style

- No formatter enforced (single-file HTML; no npm). Match the existing style: 2-space indent inside HTML, compact JS with minimal whitespace (consistent with the rest of the file).
- No comments explaining *what* code does. Only comment the *why* when it's a non-obvious invariant, a data quirk, or a workaround.
- No dead code. If you remove something, remove its helpers, constants, and any DOM elements that depended on it.

---

## 7. Commits & pull requests

### Conventional commits

- `feat:` — new user-facing feature
- `fix:` — bug fix
- `refactor:` — internal change with no behaviour change
- `docs:` — documentation
- `chore:` — tooling, CI
- `style:` — formatting only (rare — no formatter)

### One change per commit

If you find yourself writing "and also…" in a commit message, split the commit.

### Pull request descriptions

Follow `.github/PULL_REQUEST_TEMPLATE.md`. Always answer: **what changed**, **why**, **how to verify**.

---

## 8. Regular processes

### 8.1 End-of-session cleanup

**Cadence:** end of every working session. **Trigger:** Claude offers proactively.

- [ ] All work committed (`git status` clean)
- [ ] Branch pushed to GitHub
- [ ] CI green on the pushed branch (or PR open with CI green)

### 8.2 Code health pass

**Cadence:** on request (`"health check"`).

1. File size — `index.html` is currently ~640 lines. If it grows past ~900, consider whether any self-contained sections (chart engine, data tables) could be extracted without adding a build step.
2. `TODO` / `FIXME` audit
3. Data table accuracy — check Specialized and Fox published charts for updated values seasonally

---

## 9. What Claude should NOT do

- Add comments explaining what code does
- Introduce npm, a build step, or any tooling that requires `package.json` without explicit user ask
- Split `index.html` into separate files without an explicit ask
- Add backwards-compatibility shims for code with no consumers
- Introduce abstractions for hypothetical future use
- Use `--no-verify` or `git reset --hard` without explicit user OK
- Commit `.DS_Store`, `.env`, or any secrets
- Create new `.md` files unless the user asks

---

## 10. When unsure

Ask before acting. One clarifying question beats a wrong direction. Specifically pause to ask when:

- The change touches lookup math or data tables (correctness is paramount)
- The proposed fix would require adding npm or splitting the single file
- An existing behaviour looks intentional but the intent isn't documented

---

## 11. Useful commands

```bash
# Validate HTML
npx --yes html-validate --config .html-validate.json index.html

# Local dev server (port 8743)
python3 -m http.server 8743
# then open http://localhost:8743/index.html

# Git housekeeping
git status
git log --oneline -10
```
