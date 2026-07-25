"""
==============================================================================
 PullPush Reddit Comment Scraper — Dissertation Data Collection
==============================================================================

PROJECT
-------
Master's dissertation on the "dark side" of influencer marketing, applying
Natural Language Processing to user-generated Reddit comments to test a
moderated-mediation model of influencer-driven impulsive buying.

THE CONCEPTUAL MODEL THIS SCRAPE IS BUILT FOR
---------------------------------------------
                 ┌───────────────────────────┐
                 │  CONTROL (Subreddit Type) │
                 │  0 = Discussion / Neutral │
                 │  1 = Snark / Gossip       │
                 └─────────────┬─────────────┘
                               │ partials variance
                               ▼
   IV                  MEDIATORS                  DV
 ┌──────────┐    ┌──────────────────────┐   ┌────────────────────┐
 │ Influencer│    │  Benign Envy (H3a)   │   │ Impulsive Purchase │
 │   Tier   │───►│  Malicious Envy(H3b) │──►│      Intent        │
 │ (Mega vs │    └──────────┬───────────┘   └────────────────────┘
 │  Micro)  │               │
 └──────────┘               │ moderated by
                            ▼
                  ┌─────────────────────┐
                  │ MODERATOR: PSI Cues │
                  │  (H2a / H2b)        │
                  └─────────────────────┘

THE THEORETICAL BRIDGE FOR THE NEW H1
-------------------------------------
Old H1 was "High-Discrepancy post content → Envy". That required linking
each comment to a coded post, which Reddit data can't support. The new H1
re-grounds the IV in the same theory, using Influencer Tier as the
*observable proxy* for self-discrepancy magnitude:

  Self-Discrepancy Theory (Higgins, 1987) — followers feel discomfort when
  there is a perceived gap between the actual self and the ideal self.

  Mega influencers (>1M subs) curate broader, more aspirational, harder-to-
  reach lifestyles (luxury travel, designer wardrobes, professional teams).
  This makes them a *stronger* discrepancy trigger — the perceived gap is
  larger and the target feels less attainable.

  Micro/Meso influencers (50k–300k) are typically closer to the follower's
  own reachable horizon, generating a *smaller* discrepancy signal.

  Per van de Ven et al. (2009), envy directed at *unattainable* targets is
  more likely to take the malicious form (frustration, hostility), whereas
  envy at *reachable* targets is more likely to take the benign form
  (motivation, "goals"). PSI further switches between assimilation and
  contrast — high PSI nudges envy benign, low PSI nudges it malicious.

  Critically, benign and malicious envy are *competing* pathways from the
  same discrepancy trigger — assimilation vs. contrast — so the tier
  predictions go in opposite directions:

  HYPOTHESES
    H1a: Mega-influencers will elicit significantly HIGHER expressed
         Malicious Envy than Micro/Meso-influencers.
         (Mega = larger discrepancy + lower attainability → contrast)
    H1b: Micro/Meso-influencers will elicit significantly HIGHER expressed
         Benign Envy than Mega-influencers.
         (Micro = smaller discrepancy + higher attainability → assimilation)
    H2a: PSI cues positively moderate the Tier → Benign Envy pathway,
         strengthening assimilation.
    H2b: PSI cues negatively moderate the Tier → Malicious Envy pathway,
         buffering hostility.
    H3a: Expressed Benign Envy positively predicts Impulsive Purchase Intent.
    H3b: Expressed Malicious Envy positively predicts Impulsive Purchase
         Intent, with a stronger effect than Benign Envy (retail-therapy /
         coping mechanism).

  Note on operationalization: H1a and H1b are framed in terms of *rate*
  (mean expressed envy score per comment), not absolute volume. Mega
  influencers will produce more comments overall, so absolute counts of
  benign-envy comments at Mega tier may still exceed those at Micro tier
  even if the per-comment rate is lower — the mixed-effects model tests
  rates and is the correct test for these hypotheses.

  Subreddit type (snark vs discussion) is a control covariate — we partial
  out the venue's pre-existing emotional skew so we can answer the
  professor-level question: "even net of venue, does tier matter?"

WHY THE CSV HAS THESE COLUMNS
-----------------------------
Every column in the output CSV exists because some part of the analysis
will need it:

  body                  → input to NLP zero-shot classifier
                          (will produce 4 probability scores per comment:
                           Benign Envy, Malicious Envy, PSI, Purchase Intent)
  influencer_tier       → IV (0/1 dummy at analysis time)
  subreddit_stratum     → CONTROL covariate
  subreddit             → grouping variable for the random intercept in
                          mixed-effects models (handles non-independence
                          of comments within a subreddit)
  matched_influencer    → grouping variable for the second random intercept
                          (some influencers will draw louder/quieter crowds)
  created_utc           → temporal stratification & to detect time-trend
                          confounds (e.g. a single drama event spiking one
                          influencer's comments)
  score / author        → for descriptive stats and for filtering
                          AutoModerator and bot replies
  permalink             → required for the manual-coding validation pass
                          (you'll hand-label 200 random comments and need
                          to look at the original thread context)

DATA SOURCE: PullPush
---------------------
api.pullpush.io is a community Pushshift replacement. No authentication.
The /reddit/search/comment/ endpoint accepts:
  q          — keyword/phrase search inside the comment body
  subreddit  — restrict to one subreddit
  after, before — Unix timestamps, defining the time window
  size       — page size, max 100
  sort, sort_type — we use desc/created_utc to walk newest→oldest

WHY MONTH-CHUNKING IS NECESSARY
-------------------------------
PullPush returns at most ~100 comments per call. A naïve query like
"Alix Earle in r/BeautyGuruChatter from 2023-01 to today" would silently
truncate and you'd never know how much you missed. We chunk by calendar
month so each window is small enough to fully exhaust via the `before`
cursor (paging backwards through time) without hitting any per-call cap.
A 12-month run becomes 12 × (1 to ~3 pages) = manageable and complete.

DEPENDENCIES
------------
    pip install requests python-dateutil

USAGE
-----
    python pullpush_scraper.py

The scraper is *resumable*: each completed (subreddit, influencer, month)
cell is written to a checkpoint file. Re-running the script after a
crash, ctrl+C, or laptop closure picks up exactly where it left off.
==============================================================================
"""

import csv
import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Tuple

import requests
from dateutil.relativedelta import relativedelta


# =============================================================================
# 1. CONFIGURATION
# =============================================================================
# Constants live at the top so you can tune the scrape without hunting
# through function bodies. If you decide later to extend the date range,
# add an influencer, or swap in a different subreddit, those edits all
# happen in this section.
# -----------------------------------------------------------------------------

# --- PullPush endpoint settings ----------------------------------------------
PULLPUSH_COMMENT_URL = "https://api.pullpush.io/reddit/search/comment/"
PAGE_SIZE = 100              # Hard cap from PullPush — do not raise.
REQUEST_TIMEOUT = 30         # Per-request seconds before requests.get gives up.
SLEEP_BETWEEN_CALLS = 1.0    # Politeness pause between calls. Raise if you
                             # see HTTP 429 (Too Many Requests) in the log.
RETRY_BACKOFFS = [2, 5, 15, 30, 60]
# Why progressive backoff? Transient failures (server hiccups, brief network
# blips, rate-limit nudges) usually clear within seconds. Permanent failures
# (bad subreddit name, bad query) won't — but the cost of waiting up to ~2
# minutes total before giving up is small relative to the cost of losing
# data partway through a 12-hour scrape.

# --- Date range --------------------------------------------------------------
# Inclusive of START_DATE month; runs up to "now" at execution time.
START_DATE = datetime(2023, 1, 1, tzinfo=timezone.utc)
END_DATE = datetime.now(timezone.utc)
# All datetimes are explicitly UTC so we never accidentally shift comments
# across day boundaries due to the machine's local timezone.

# --- Output paths ------------------------------------------------------------
OUTPUT_DIR = "reddit_data"
RAW_CSV = os.path.join(OUTPUT_DIR, "comments_raw.csv")
CHECKPOINT_FILE = os.path.join(OUTPUT_DIR, "checkpoint.json")
LOG_FILE = os.path.join(OUTPUT_DIR, "scraper.log")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Influencer registry ----------------------------------------------------
# `tier` is your independent variable (Mega vs. Micro/Meso).
# `queries` is the list of search strings we'll send to PullPush. We include
# variants (surnames, handles like "Inthefrow") to maximize recall — at the
# cost of some false positives, which we filter out in the cleaning step.
#
# Methodological note for your professor: by storing the variants list per
# influencer we keep recall high during scraping (better to over-collect
# and filter than to silently miss comments), and we delegate precision to
# a separate cleaning script. This separation of concerns keeps each step
# auditable.
INFLUENCERS: Dict[str, Dict] = {
    # ---- MEGA TIER (≥ 1M subscribers) — IV = "mega" ----
    "Matilda Djerf":          {"tier": "mega",  "queries": ["Matilda Djerf", "Djerf"]},
    "Alix Earle":             {"tier": "mega",  "queries": ["Alix Earle"]},
    "Jaclyn Hill":            {"tier": "mega",  "queries": ["Jaclyn Hill"]},
    "Emma Chamberlain":       {"tier": "mega",  "queries": ["Emma Chamberlain"]},
    "Desi Perkins":           {"tier": "mega",  "queries": ["Desi Perkins"]},
    "NikkieTutorials":        {"tier": "mega",  "queries": ["NikkieTutorials", "Nikkie Tutorials", "Nikkie de Jager"]},
    "Jackie Aina":            {"tier": "mega",  "queries": ["Jackie Aina"]},
    "Tati Westbrook":         {"tier": "mega",  "queries": ["Tati Westbrook"]},
    "Lydia Elise Millen":     {"tier": "mega",  "queries": ["Lydia Elise Millen", "Lydia Millen"]},
    "Victoria Magrath":       {"tier": "mega",  "queries": ["Victoria Magrath", "Inthefrow", "In The Frow"]},

    # ---- MICRO / MESO TIER (50k–300k) — IV = "micro" ----
    # Several names here are common English words. The cleaning script
    # MUST re-validate by checking that the canonical name (or a clearly
    # name-derived token) appears verbatim in the comment body. Otherwise
    # "Amanda Z" will catch every comment that mentions any Amanda.
    "Hannah Louise Poston":   {"tier": "micro", "queries": ["Hannah Louise Poston", "Hannah Poston"]},
    "Kelly Gooch":            {"tier": "micro", "queries": ["Kelly Gooch"]},
    "Lauren Mae Beauty":      {"tier": "micro", "queries": ["Lauren Mae Beauty", "Lauren Mae"]},
    "Julia Adams MUA":        {"tier": "micro", "queries": ["Julia Adams MUA", "Julia Adams"]},
    "Theresa is Dead":        {"tier": "micro", "queries": ["Theresa is Dead", "TheresaIsDead"]},
    "Amanda Z":               {"tier": "micro", "queries": ["Amanda Z makeup", "AmandaZBeauty"]},
    "Kackie Reviews Beauty":  {"tier": "micro", "queries": ["Kackie Reviews", "Kackie Beauty"]},
    "Shelbey Wilson":         {"tier": "micro", "queries": ["Shelbey Wilson"]},
    "Karima McKimmie":        {"tier": "micro", "queries": ["Karima McKimmie", "Karima Beauty"]},
    "Samantha March":         {"tier": "micro", "queries": ["Samantha March beauty", "Samantha March MUA"]},
}

# --- Subreddit registry -----------------------------------------------------
# `stratum` is your control variable.
#   "discussion" (0) = neutral discussion, fan, or analytical communities.
#   "snark"      (1) = adversarial-by-design — gossip and snark subreddits.
#
# The control variable expresses the venue's pre-existing emotional bias.
# At analysis time you'll feed this into the regression as a covariate AND
# include subreddit-level random intercepts to soak up finer-grained venue
# effects (e.g., r/gymsnark behaves differently from r/blogsnark even
# though both are "snark").
SUBREDDITS: List[Tuple[str, str]] = [
    # ---- Discussion / Neutral (control = 0) ----
    ("BeautyGuruChatter",      "discussion"),  # main workhorse
    ("MakeupAddiction",        "discussion"),
    ("MakeupRehab",            "discussion"),  # NB: anti-buy bias on DV
    ("muacjdiscussion",        "discussion"),  # analytical, lower noise
    ("Sephora",                "discussion"),
    ("AsianBeauty",            "discussion"),
    ("BeautyBoxes",            "discussion"),
    # ---- Snark / Gossip (control = 1) ----
    ("blogsnark",              "snark"),
    ("NYCinfluencersnark",     "snark"),
    ("LAinfluencersnark",      "snark"),
    ("Anticonsumption",        "snark"),       # NB: anti-buy bias on DV
    ("Tiktokgossip",           "snark"),
    ("InstaCelebsGossip",      "snark"),
    ("gymsnark",               "snark"),
    ("DoWeKnowThemPodcast",    "snark"),
]

# --- Output schema ----------------------------------------------------------
# These are the columns we'll write to comments_raw.csv. See the header
# docstring for which column supports which part of the analysis.
CSV_FIELDS = [
    "id",                  # Reddit comment id; our deduplication key
    "subreddit",           # for random intercept in mixed-effects
    "author",              # for descriptive stats / bot filtering
    "body",                # input to NLP classifier
    "score",               # for descriptive stats / quality filtering
    "created_utc",         # for time-trend checks
    "created_iso",         # human-readable timestamp
    "link_id",             # parent submission id (allows thread context)
    "parent_id",           # parent comment id (for reply-tree analysis)
    "permalink",           # for manual validation pass
    "matched_influencer",  # canonical name (e.g. "Alix Earle")
    "influencer_tier",     # IV: "mega" or "micro"
    "subreddit_stratum",   # CONTROL: "discussion" or "snark"
    "search_query",        # which variant matched (for false-positive audit)
    "month_window",        # which month-chunk this came from
]


# =============================================================================
# 2. LOGGING SETUP
# =============================================================================
# A long scrape WILL hit transient errors. We want a persistent log file
# so that, hours later, we can inspect what failed and why. The console
# handler keeps you informed in real time.
# -----------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("pullpush")


# =============================================================================
# 3. HELPER FUNCTIONS
# =============================================================================

def month_chunks(start: datetime, end: datetime) -> Iterable[Tuple[int, int, str]]:
    """
    Yield one (after_unix, before_unix, label) tuple per calendar month
    between `start` and `end`.

    PullPush expects Unix timestamps. We yield them as ints so we can pass
    them straight to the API. The label string ("YYYY-MM") is used for
    logging and as a column in the CSV — it makes the data trivially
    sortable and groupable later in pandas.

    Why month-sized? See the header docstring: large enough that the
    overhead per cell is small, small enough that we never hit PullPush's
    pagination ceiling for high-volume influencer/subreddit pairs.
    """
    cur = start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    while cur < end:
        nxt = cur + relativedelta(months=1)
        upper = min(nxt, end)
        yield int(cur.timestamp()), int(upper.timestamp()), cur.strftime("%Y-%m")
        cur = nxt


def pullpush_call(params: Dict) -> List[Dict]:
    """
    One GET to PullPush with progressive retry/backoff.

    Returns the `data` list from the JSON response (possibly empty). On
    unrecoverable failure we log an error and return [] rather than
    raising — keeping a multi-hour scrape going is more important than
    failing loudly on one bad cell.

    Retry policy: HTTP 200 returns immediately. HTTP 429/5xx triggers a
    progressive backoff (2s, 5s, 15s, 30s, 60s — total ~2 min budget).
    Other 4xx codes (400, 404, etc.) are treated as permanent and we
    bail without retrying — those usually indicate a malformed query.
    """
    for attempt in range(len(RETRY_BACKOFFS) + 1):
        try:
            r = requests.get(PULLPUSH_COMMENT_URL, params=params, timeout=REQUEST_TIMEOUT)
            if r.status_code == 200:
                return r.json().get("data", []) or []
            # Transient — wait and retry
            if r.status_code in (429, 500, 502, 503, 504):
                log.warning("HTTP %s on %s — backing off", r.status_code, params)
            else:
                log.error("HTTP %s (non-retryable): %s", r.status_code, r.text[:200])
                return []
        except (requests.RequestException, ValueError) as e:
            log.warning("Request error on attempt %s: %s", attempt, e)
        if attempt < len(RETRY_BACKOFFS):
            time.sleep(RETRY_BACKOFFS[attempt])
    log.error("Giving up on %s after retries", params)
    return []


def search_window(subreddit: str, query: str, after: int, before: int) -> List[Dict]:
    """
    Pull *every* comment in (subreddit, query, [after, before)) by paging
    backwards through the time window using PullPush's `before` cursor.

    Algorithm:
      1. Ask PullPush for the newest 100 comments in the window
         (sort_type=created_utc, sort=desc).
      2. Record what we got. Dedupe within the window — PullPush
         occasionally returns overlap on cursor boundaries.
      3. If the page contained fewer than 100 results, we've exhausted
         this window — done.
      4. Otherwise: set the cursor to the timestamp of the *oldest*
         comment in the page and ask again. Each iteration walks
         further back in time.
      5. Stop when the cursor reaches `after`, or after a hard 50-page
         safety cap (which would mean ~5,000 comments in one
         influencer-month — investigate manually if this triggers).

    Returns a deduplicated list of raw PullPush comment dicts.
    """
    out: List[Dict] = []
    seen: set = set()
    cursor = before
    pages = 0

    while True:
        params = {
            "subreddit": subreddit,
            # If the query has spaces, wrap it in quotes so PullPush treats
            # it as a phrase. Single-word queries don't need quoting.
            "q": f'"{query}"' if " " in query else query,
            "after": after,
            "before": cursor,
            "size": PAGE_SIZE,
            "sort": "desc",
            "sort_type": "created_utc",
        }
        page = pullpush_call(params)
        pages += 1
        if not page:
            break  # empty window, or unrecoverable error — move on

        new_rows = [c for c in page if c.get("id") and c["id"] not in seen]
        for c in new_rows:
            seen.add(c["id"])
        out.extend(new_rows)

        # Fewer than PAGE_SIZE results means this was the last page —
        # we've exhausted the time window.
        if len(page) < PAGE_SIZE:
            break

        # Otherwise advance the cursor: jump to just before the oldest
        # comment we just received, so the next page starts there and
        # walks further back in time.
        oldest_ts = min(c.get("created_utc", before) for c in page)
        if oldest_ts <= after:
            break  # cursor would cross out of the window
        cursor = oldest_ts

        # Safety net — a malformed cursor advance would loop forever.
        if pages > 50:
            log.warning(
                "Hit 50-page safety cap on %s/%s/%s-%s — investigate",
                subreddit, query, after, before,
            )
            break

        time.sleep(SLEEP_BETWEEN_CALLS)

    return out


def load_checkpoint() -> set:
    """
    Resume support. Returns the set of (subreddit, influencer, month)
    tuples already completed in a previous run. If the scrape is killed
    midway, restarting picks up exactly where we left off.
    """
    if not os.path.exists(CHECKPOINT_FILE):
        return set()
    with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
        return {tuple(x) for x in json.load(f)}


def save_checkpoint(done: set) -> None:
    """Write the completed-cells set to disk after every cell."""
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump([list(k) for k in done], f)


def comment_to_row(c: Dict, *, influencer: str, tier: str,
                   subreddit_stratum: str, query: str, month: str) -> Dict:
    """
    Flatten one PullPush comment dict into our CSV schema. We strip
    newlines from the body so each comment fits on one CSV row — this
    keeps the file readable for spot-checks in Excel and avoids quoting
    issues downstream. The full original text is preserved (we only
    swap \r and \n for spaces).
    """
    ts = c.get("created_utc")
    iso = (datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
           if ts else "")
    perma = c.get("permalink", "")
    return {
        "id": c.get("id"),
        "subreddit": c.get("subreddit"),
        "author": c.get("author"),
        "body": (c.get("body") or "").replace("\r", " ").replace("\n", " "),
        "score": c.get("score"),
        "created_utc": ts,
        "created_iso": iso,
        "link_id": c.get("link_id"),
        "parent_id": c.get("parent_id"),
        "permalink": f"https://reddit.com{perma}" if perma else "",
        "matched_influencer": influencer,
        "influencer_tier": tier,
        "subreddit_stratum": subreddit_stratum,
        "search_query": query,
        "month_window": month,
    }


# =============================================================================
# 4. MAIN SCRAPE LOOP
# =============================================================================
# We iterate the three-dimensional cube (subreddit × influencer × month).
# For each cell we run every query variant for that influencer, dedupe
# by comment id, and append the rows to the CSV.
#
# Order of loops matters for graceful interruption: the outer loop is
# subreddit, so if you ctrl+C you'll usually only lose at most one
# subreddit's worth of "in flight" work, which the next run will redo.
# -----------------------------------------------------------------------------
def main() -> None:
    done = load_checkpoint()
    log.info("Resuming with %d completed cells in checkpoint", len(done))

    # Open CSV in append mode. Header is written only on the very first
    # run (when the file doesn't exist yet) — every subsequent run just
    # appends rows for cells not in the checkpoint.
    is_new = not os.path.exists(RAW_CSV)
    with open(RAW_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if is_new:
            writer.writeheader()

        # Pre-compute the total number of cells for nice progress logging.
        all_months = list(month_chunks(START_DATE, END_DATE))
        total_cells = len(SUBREDDITS) * len(INFLUENCERS) * len(all_months)
        cell_idx = 0

        for subreddit, stratum in SUBREDDITS:
            for canonical, meta in INFLUENCERS.items():
                tier = meta["tier"]
                for after, before, month in all_months:
                    cell_idx += 1
                    cell_key = (subreddit, canonical, month)
                    if cell_key in done:
                        continue  # already scraped on a previous run

                    cell_total = 0
                    # Run each query variant separately. We may double-count
                    # comments that match >1 variant ("Matilda Djerf" and
                    # "Djerf" both match the same comment), but we'll dedupe
                    # in the cleaning script — easier than trying to be
                    # clever here.
                    for q in meta["queries"]:
                        rows = search_window(subreddit, q, after, before)
                        for c in rows:
                            writer.writerow(comment_to_row(
                                c,
                                influencer=canonical,
                                tier=tier,
                                subreddit_stratum=stratum,
                                query=q,
                                month=month,
                            ))
                        cell_total += len(rows)
                        time.sleep(SLEEP_BETWEEN_CALLS)

                    # Flush to disk after each cell so a crash never costs
                    # more than the most recent cell's data.
                    f.flush()
                    done.add(cell_key)
                    save_checkpoint(done)

                    log.info(
                        "[%d/%d] r/%s | %s (%s) | %s → %d rows",
                        cell_idx, total_cells, subreddit, canonical, tier,
                        month, cell_total,
                    )

    log.info("Done. Output: %s", RAW_CSV)


if __name__ == "__main__":
    main()


# =============================================================================
# 5. NEXT STEPS — POST-PROCESSING & ANALYSIS PIPELINE
# =============================================================================
# Once the scrape finishes you'll have comments_raw.csv with somewhere
# between 30k and 80k rows depending on how the volume lands. The next
# stages of the pipeline are sketched below as commented skeletons —
# write each as its own .py file so the workflow stays modular and each
# step is independently re-runnable.
#
# ──────────────────────────────────────────────────────────────────────
# STEP A — clean_comments.py  (data cleaning)
# ──────────────────────────────────────────────────────────────────────
#   import pandas as pd
#   df = pd.read_csv("reddit_data/comments_raw.csv")
#
#   # 1. Dedupe — same comment may appear under multiple query variants
#   df = df.drop_duplicates(subset="id")
#
#   # 2. Drop deleted/removed bodies and bot replies
#   df = df[~df["body"].isin(["[deleted]", "[removed]"])]
#   df = df[df["author"] != "AutoModerator"]
#
#   # 3. Length filters: too short = noise, too long = pasted articles
#   df["body_len"] = df["body"].str.split().str.len()
#   df = df[(df["body_len"] >= 3) & (df["body_len"] <= 1000)]
#
#   # 4. Re-validate single-word/risky queries
#   risky = {"Djerf", "Inthefrow"}
#   def keeps(row):
#       if row["search_query"] not in risky:
#           return True
#       return row["matched_influencer"].lower() in row["body"].lower()
#   df = df[df.apply(keeps, axis=1)]
#
#   # 5. Encode IV and control as 0/1 for modelling
#   df["tier_mega"]    = (df["influencer_tier"]   == "mega").astype(int)
#   df["sub_snark"]    = (df["subreddit_stratum"] == "snark").astype(int)
#   df.to_csv("reddit_data/comments_clean.csv", index=False)
#
# ──────────────────────────────────────────────────────────────────────
# STEP B — classify.py  (NLP — zero-shot classification)
# ──────────────────────────────────────────────────────────────────────
#   from transformers import pipeline
#   clf = pipeline("zero-shot-classification",
#                  model="facebook/bart-large-mnli")
#
#   labels = ["Benign Envy", "Malicious Envy",
#             "Parasocial Affection", "Purchase Intent"]
#   # For each comment, store the probability of each label as its own
#   # column. Multi-label=True lets a comment score high on more than one
#   # construct at once (e.g. malicious envy + purchase intent).
#   # → comments_scored.csv
#
# ──────────────────────────────────────────────────────────────────────
# STEP C — analyze.py  (mixed-effects moderated mediation)
# ──────────────────────────────────────────────────────────────────────
# This is where the model design we agreed on actually lives. The key
# idea is that comments are *nested* within subreddits and within
# influencers — they aren't independent observations. A plain OLS
# regression will give standard errors that are too narrow because it
# treats every comment as independent. Mixed-effects models add random
# intercepts for the grouping variables, which corrects this.
#
#   import pandas as pd
#   import statsmodels.formula.api as smf
#
#   df = pd.read_csv("reddit_data/comments_scored.csv")
#
#   # ---- H1a: Mega tier → MORE Malicious Envy (expect tier_mega > 0) ----
#   m_h1a = smf.mixedlm(
#       "malicious_envy ~ tier_mega * sub_snark",  # main effects + interaction
#       data=df,
#       groups=df["subreddit"],                     # random intercept: subreddit
#   ).fit()
#   print(m_h1a.summary())
#   # Support for H1a: the tier_mega coefficient is POSITIVE and p < .05.
#   # The tier_mega:sub_snark interaction tells you whether the effect is
#   # bigger inside snark venues (theoretically expected) or roughly flat
#   # across venues (would suggest the discrepancy effect is venue-robust).
#
#   # ---- H1b: Micro tier → MORE Benign Envy (expect tier_mega < 0) ----
#   m_h1b = smf.mixedlm(
#       "benign_envy ~ tier_mega * sub_snark",
#       data=df,
#       groups=df["subreddit"],
#   ).fit()
#   print(m_h1b.summary())
#   # Support for H1b: the tier_mega coefficient is NEGATIVE and p < .05
#   # (i.e. mega tier shows LOWER benign envy rates than micro).
#   # If tier_mega is non-significant or positive, that's evidence that
#   # mega influencers' "aspirational goals" pull is matching or exceeding
#   # micro's assimilation pull — interesting and worth discussing in the
#   # results chapter rather than glossing over.
#
#   # ---- H2a / H2b: PSI moderation ----
#   # Add psi_score and its interaction with tier_mega:
#   m_h2 = smf.mixedlm(
#       "malicious_envy ~ tier_mega * psi_score + sub_snark",
#       data=df,
#       groups=df["subreddit"],
#   ).fit()
#
#   # ---- H3a / H3b: Envy → Purchase Intent ----
#   m_h3 = smf.mixedlm(
#       "purchase_intent ~ benign_envy + malicious_envy + tier_mega + sub_snark",
#       data=df,
#       groups=df["subreddit"],
#   ).fit()
#
#   # ---- Full moderated mediation ----
#   # For the integrated test, use semopy or pingouin's mediation_analysis,
#   # bootstrapping the indirect effects (5,000 resamples) so you can
#   # report 95% CIs that don't assume normality.
#
# ──────────────────────────────────────────────────────────────────────
# Reading the output for your professor:
#   - Coefficient on `tier_mega` in m_h1b answers H1b directly:
#     the average difference in malicious-envy expression between Mega
#     and Micro influencers, with venue partialed out and within-
#     subreddit clustering accounted for.
#   - Coefficient on `tier_mega:sub_snark` is the *interaction*:
#     does the tier effect look different in snark vs discussion subs?
#   - Random-effect variance for `subreddit` tells you how much of the
#     variation lives at the venue level vs within-comment — a
#     defensible answer to any "how do you know this isn't all
#     subreddit noise?" question.
# =============================================================================
