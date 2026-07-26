# From Envy to Purchase — Dissertation Code Repository

**The Role of Parasocial Interaction in Social Media Influencer Marketing**

Code, notebooks, and analytical scripts supporting an MSc Business Analytics dissertation that investigates how influencer tier (mega vs micro/meso) shapes commenter expression of benign envy, malicious envy, parasocial interaction (PSI), and purchase intent (PI) in beauty-and-fashion Reddit discussion, and how these constructs sort commenters into distinct latent response profiles.

---

## Overview

This repository contains the computational workflow used to construct, classify, anonymise, and analyse a corpus of **4,500 Reddit comments** referencing **16 beauty-and-fashion influencers** (eight mega-tier, ≥ 1M followers; eight micro/meso-tier, 50K–300K followers) across **seven subreddits** between **January 2023 and May 2025**.

Six hypotheses are tested using mixed-effects regression on the LLM-scored construct measurements, and two extensions add methodological robustness: cross-classified random-effects (author + influencer) partitioning of variance, and a latent class analysis identifying a five-class author typology (Buyers, Envious-but-not-buying, Mild Venters, Pure Venters, Mixed-emotion). The dominant substantive finding is that influencer tier operates as an audience-sorting mechanism — mega audiences concentrate Pure Venters (malicious envy without purchase intent), micro audiences concentrate Buyers (canonical benign envy → purchase intent route).

The pipeline is implemented in Python. The raw Reddit scrape — which contains personally identifiable usernames — is **not distributed**; the pseudonymised intermediate datasets included in the `data/` folder are sufficient to reproduce every downstream analysis. See *Data availability* below.

---

## Repository structure

```
.
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
│
├── data_collection/
│   ├── pullpush_scraper.py             ← PullPush archive API client
│   └── 01_initial_analysis.ipynb       ← corpus audit, cleaning, sampling
│
├── preprocessing/
│   ├── 02b_manual_validation.ipynb     ← human-coded reference set setup
│   ├── 02c_llm_classification.ipynb    ← Claude Haiku 4.5 construct classification
│   ├── 02d_anonymise.ipynb             ← salted SHA-256 pseudonymisation
│   ├── claude_codings.py               ← AI second-coder codes (transcribed)
│   ├── claude_codes.py                 ← earlier variant of the above
│   ├── compare_to_claude.py            ← two-coder F1 comparison helper
│   └── recode_disagreements.py         ← disagreement-adjudication helper
│
├── analysis/
│   ├── 03_hypothesis_tests.ipynb       ← mixed-effects regression + bootstrap mediation
│   ├── 04_robustness_multilevel.ipynb  ← cross-classified RE + LCA + K-sensitivity
│   ├── 02e_test_retest.ipynb           ← test-retest reliability (Cohen's kappa)
│   └── 02f_verify_alignment.ipynb      ← programmatic 02c ↔ 02e alignment check
│
├── data/
│   ├── comments_scored_llm.csv         ← pseudonymised LLM-scored corpus
│   └── author_lca_classes.csv          ← LCA class assignments per pseudonym
│
└── docs/
    └── methods_summary.md              ← one-page methods reference
```

---

## End-to-end workflow

The pipeline runs in the numeric order of the notebook prefixes: **01 → 02b → 02c → 02d → 02e → 02f → 03 → 04.**

### Stage 1 — Data collection (`data_collection/`)

1. **`pullpush_scraper.py`** queries the PullPush Reddit archive for comments mentioning each of the 16 focal influencers in the seven target subreddits between Jan 2023 and May 2025.
2. **`01_initial_analysis.ipynb`** cleans the raw scrape (removes deleted/removed/empty comments, AutoModerator, and applies a token-length filter of 3 ≤ tokens ≤ 1,000), audits per-influencer volumes, and produces `comments_clean.csv`. The subreddit_stratum indicator is preserved as a variable but no filter on stratum is applied here. **The snark-stratum drop happens in the next stage** (see below).

### Stage 2 — Preprocessing (`preprocessing/`)

3. **`02b_manual_validation.ipynb`** draws a 200-comment stratified random sample from the cleaned corpus and produces a blind coding sheet for the researcher to code. An AI second coder (Claude via the claude.ai interface — see *Second-coder provenance* below) was run in parallel on the same 200 comments and its codes are stored in `claude_codings.py`. Outputs a two-coder reference set `validation_two_coders.csv`.
4. **`02c_llm_classification.ipynb`** is where the analysis-specific filters are applied. §2 restricts the corpus to the discussion stratum (excluding snark, motivated by micro-tier sparsity in the snark cell — n ≈ 20) and excludes four influencers with fewer than 20 raw-scrape comments each (Samantha March, Amanda Z, Lydia Elise Millen, Victoria Magrath). The remaining 4,500 comments across 16 retained influencers are then scored by **Claude Haiku 4.5** using a structured-rubric system prompt covering four constructs: Benign Envy, Malicious Envy, PSI, and Purchase Intent. F1 scores against the human reference set are: **PI = 0.80 (strong), ME = 0.71 (acceptable), BE = 0.58 (marginal), PSI = 0.29 (poor)**.
5. **`02d_anonymise.ipynb`** replaces Reddit usernames in the scored corpus with deterministic salted SHA-256 pseudonyms and scrubs embedded `/u/<username>` mentions from comment body text. Produces the pseudonymised `comments_scored_llm.csv` used by all downstream notebooks. Ethical framework: AoIR IRE 3.0 (Franzke et al., 2020) and BPS Code of Human Research Ethics (BPS, 2021).
6. **`02e_test_retest.ipynb`** re-scores a stratified 100-comment sample using the identical Claude Haiku 4.5 setup and computes Cohen's kappa per construct. Results: **κ = 0.93 (BE), 0.94 (ME), 0.78 (PSI), 0.88 (PI)** — substantial to almost-perfect intra-classifier stability.
7. **`02f_verify_alignment.ipynb`** programmatically checks that the LLM setup (system prompt, `classify_one` function, model constant) is byte-identical or semantically identical between 02c and 02e, guaranteeing the test-retest kappa reflects genuine stochasticity rather than setup drift.

### Stage 3 — Analysis (`analysis/`)

8. **`03_hypothesis_tests.ipynb`** fits mixed-effects regression with random intercepts per influencer for the six pre-registered hypotheses.

    - **H1a (Mega → more ME)**: β = +0.130 (p < .001) — SUPPORTED. Robustness check drops the dominant mega influencer **Jaclyn Hill** (~24% of corpus, ~54% of mega tier): β = +0.096 (p < .001), i.e., 74% of the effect preserved with direction and significance intact. A supplementary Alix Earle drop is also included; Alix contributes only ~1% of the corpus (97.9% of her raw commentary is in snark-stratum subreddits, which were excluded upstream).
    - **H1b (Tier × envy-type)**: β = +0.214 (p < .001) — SUPPORTED.
    - **H2a/H2b (PSI moderation)**: exploratory only; PSI F1 = 0.29 limits inference.
    - **H3a/H3b (Envy → PI)**: NOT SUPPORTED in predicted direction. β_BE = −0.036, β_ME = −0.072. Bootstrap mediation Tier → ME → PI = −0.013 [−0.015, −0.011] is the only reliable indirect pathway.

9. **`04_robustness_multilevel.ipynb`** extends the analysis with:
    - **Cross-classified random-effects** (author + influencer). Variance decomposition shows approximately 43–48% of variance between commenters, only 0.4–3.5% between influencers — indicating the tier effects operate primarily at the between-audience level.
    - **Latent Class Analysis** on author-level construct proportions (n = 340 authors with ≥ 3 comments; sensitivity at ≥ 2 comments confirms K = 5 elbow). Identifies a five-class typology: Buyers (35.0%, 81.5% micro-led), Envious-but-not-buying (19.4%), Mild Venters (19.1%), Pure Venters (15.3%, 65.4% mega-led), Mixed-emotion (11.2%). χ²(4) = 36.58, p < .001 for tier × class independence.

---

## Requirements

- **Python** ≥ 3.10
- Optional: **R** ≥ 4.2 with `lme4` for a confirmatory cross-classified re-fit

Install Python dependencies in a fresh virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate       # macOS/Linux
# .venv\Scripts\activate        # Windows PowerShell
pip install --upgrade pip
pip install -r requirements.txt
```

Key packages: `pandas`, `numpy`, `scipy`, `statsmodels`, `matplotlib`, `seaborn`, `scikit-learn`, `anthropic` (for 02c and 02e re-runs), `stepmix` (for LCA), `python-dotenv` (for salt loading in 02d).

---

## Setup

1. Clone the repository and `cd` into it.
2. Create the Python virtual environment and install dependencies.
3. Create a `.env` file at the repository root (not committed to git) with:

   ```
   ANTHROPIC_API_KEY=sk-ant-...           # only needed to re-run 02c and 02e
   PSEUDONYM_SALT=<64-char hex string>    # only needed to re-run 02d
   ```

   Generate a fresh salt with `python -c 'import secrets; print(secrets.token_hex(32))'`. The same salt must be used across all runs to produce the same pseudonyms.
4. Launch Jupyter and run the notebooks in the order listed above.

---

## Data availability

| File | Included in this repo? | Reason |
|---|---|---|
| `comments_raw_full.csv` (raw scrape with real usernames) | **No** | Contains PII |
| `pseudonym_mapping.csv` (username → pseudonym lookup) | **No** | Restricted; kept separately |
| `.env` (API key + salt) | **No** | Contains secrets |
| `comments_scored_llm.csv` (pseudonymised, LLM-scored) | **Yes** | Deterministic pseudonyms only; no PII |
| `author_lca_classes.csv` (one row per pseudonym) | **Yes** | LCA class assignments |

The pseudonymised files plus the analysis notebooks (03, 04) reproduce every result reported in the dissertation. Raw data are retained under restricted access for the institutional minimum retention period and may be requested by academic examiners via the author's supervisor.

---

## Ethics statement

This study was conducted in accordance with:

- [Association of Internet Researchers Internet Research Ethics 3.0](https://aoir.org/reports/ethics3.pdf) (Franzke, Bechmann, Zimmer, Ess, & the Association of Internet Researchers, 2020)
- [British Psychological Society Code of Human Research Ethics](https://www.bps.org.uk/guideline/bps-code-human-research-ethics) (BPS, 2021)
- Institutional ethics approval

Key protections:

- Reddit usernames replaced with salted SHA-256 pseudonyms before analysis (Notebook 02d)
- Inline `/u/<username>` mentions scrubbed from comment body text
- No verbatim quotations reproduced in the dissertation (composite paraphrases only, per Bruckman, 2002)
- Aggregate-level reporting only — no individual is identifiable in any published output
- Right-to-erasure documented: if a Reddit user contacts the researcher requesting removal, the corresponding pseudonym is removed from the dataset and the analysis is re-run

---

## Second-coder provenance (methodological note)

The AI second coder used in the 200-comment validation reference set was **Claude (Anthropic), accessed via the claude.ai chat interface** prior to the setup of the API-based classification pipeline in `02c`. The specific model version used during that coding session is not preserved in the pipeline metadata; based on Anthropic's default-model schedule in May 2026, the most probable model was Claude Sonnet 4.6, but this cannot be verified from the archived materials. The Claude codes were transcribed into a Python dictionary (`claude_codings.py`) which feeds `validation_two_coders.csv`. See the dissertation Methods and Limitations chapters for full disclosure and the same-model-family caveat that applies to the F1 numbers reported from `validation_two_coders.csv`.

---

## Reproducibility notes

- The pipeline is deterministic given the same `PSEUDONYM_SALT` and `random_state=42` (the default seed throughout).
- The Anthropic API is not perfectly deterministic even at fixed settings; small run-to-run variation is expected. The test-retest analysis in 02e quantifies this variation for the primary classification: κ = 0.78 – 0.94 across the four constructs.
- The cross-classified RE diagnostic in 04 uses a `statsmodels` two-step approximation because `pymer4` (R/lme4) was not available in the analysis environment. A confirmatory `lmer` replication is documented in the notebook.
- The LCA uses `stepmix` with `random_state=42` and 20 random EM starts. K = 5 selected by the BIC elbow and interpretability; sensitivity at K = 2..10 confirms the elbow.

---


## Acknowledgements

The classification rubrics in `02c_llm_classification.ipynb` were grounded in the psychological-measurement literature on parasocial interaction (Horton & Wohl, 1956; Rubin, Perse, & Powell, 1985), benign and malicious envy (van de Ven, Zeelenberg, & Pieters, 2009; Lange & Crusius, 2015), and impulsive buying tendency (Rook & Fisher, 1995). Full APA references are in the dissertation Methods chapter.
