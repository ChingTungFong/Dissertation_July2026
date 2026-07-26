"""
Filter the two-coder file down to just the disagreements on benign_envy
where you marked 0 and Claude marked 1 (29 cases).

Outputs a small Excel-friendly CSV for quick review. After re-coding,
write your updated judgment in the 'final_benign_envy' column, then run
the merge_back step at the bottom of this script to produce a clean
validation reference.
"""
import pandas as pd

df = pd.read_csv("validation_two_coders.csv")

# Filter to just the 29 benign_envy disagreements (where you said 0, Claude said 1)
disagree = df[(df["human_benign_envy"]==0) & (df["claude_benign_envy"]==1)].copy()
print(f"Disagreements to re-review: {len(disagree)}")

# Add an empty column for your final judgment
disagree["final_benign_envy"] = ""   # fill in 0 or 1 in Excel

# Save just the columns you need to review
out_cols = ["id","matched_influencer","influencer_tier","subreddit",
            "body","human_benign_envy","claude_benign_envy","final_benign_envy"]
disagree[out_cols].to_csv("benign_envy_disagreements.csv", index=False)
print("Wrote benign_envy_disagreements.csv — open in Excel and code the "
      "'final_benign_envy' column with 0 or 1 based on the refined rubric.")

# ---------- AFTER YOU'VE FILLED IN final_benign_envy, run this part ----------
# Uncomment and re-run after coding is done:
#
# coded = pd.read_csv("benign_envy_disagreements.csv")
# # Build the merged reference:
# updated = df.copy()
# updated = updated.merge(coded[["id","final_benign_envy"]], on="id", how="left")
# # Where final_benign_envy is filled in, override the original human_benign_envy
# mask = updated["final_benign_envy"].notna() & (updated["final_benign_envy"] != "")
# updated.loc[mask, "human_benign_envy"] = updated.loc[mask, "final_benign_envy"].astype(int)
# updated = updated.drop(columns=["final_benign_envy"])
# updated.to_csv("validation_two_coders.csv", index=False)
# print(f"Updated {mask.sum()} benign_envy codes in validation_two_coders.csv")
