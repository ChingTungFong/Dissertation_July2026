"""
Claude's independent codings of the 200 validation comments,
applied with the same rubric as the user but slightly more permissively
(any clear admiration counts as benign envy, not only explicit
'I want to be like her' aspiration).
"""
import pandas as pd

# Index -> (benign_envy, malicious_envy, psi, purchase_intent)
CLAUDE_CODES = {
    0: (0,0,0,0),  1: (0,0,0,0),  2: (1,0,0,0),  3: (0,1,0,0),  4: (1,0,0,0),
    5: (0,0,0,0),  6: (0,0,0,0),  7: (0,0,0,0),  8: (1,0,1,0),  9: (0,0,0,0),
   10: (0,0,0,0), 11: (0,0,0,0), 12: (0,0,1,0), 13: (1,0,0,0), 14: (0,0,0,0),
   15: (1,0,1,0), 16: (0,0,0,0), 17: (0,0,0,0), 18: (0,0,0,0), 19: (0,1,0,0),
   20: (0,0,0,0), 21: (0,0,0,0), 22: (0,0,0,0), 23: (0,0,1,0), 24: (0,0,0,1),
   25: (0,0,0,0), 26: (0,0,0,0), 27: (1,0,0,0), 28: (0,0,0,0), 29: (0,0,0,0),
   30: (0,0,0,0), 31: (0,1,0,0), 32: (0,1,0,0), 33: (0,1,0,0), 34: (0,0,0,0),
   35: (0,0,0,0), 36: (0,0,0,0), 37: (0,0,0,0), 38: (0,0,0,0), 39: (0,0,0,0),
   40: (0,0,1,0), 41: (0,0,0,0), 42: (0,0,1,0), 43: (0,1,0,0), 44: (0,1,0,0),
   45: (1,0,0,1), 46: (0,0,0,0), 47: (0,1,0,0), 48: (0,0,1,0), 49: (0,0,0,0),
   50: (0,1,0,0), 51: (0,0,1,0), 52: (0,0,0,0), 53: (1,0,0,0), 54: (0,0,0,0),
   55: (0,0,1,0), 56: (0,0,0,0), 57: (0,0,0,0), 58: (0,0,0,0), 59: (0,0,0,0),
   60: (0,0,0,1), 61: (0,0,0,0), 62: (0,0,0,0), 63: (0,0,0,0), 64: (1,0,0,0),
   65: (1,0,1,0), 66: (0,0,0,0), 67: (0,0,0,0), 68: (0,0,0,0), 69: (0,0,0,0),
   70: (0,0,0,0), 71: (1,0,0,0), 72: (0,0,1,0), 73: (1,0,0,0), 74: (0,1,0,0),
   75: (0,0,0,0), 76: (0,0,0,0), 77: (0,0,0,0), 78: (1,0,1,0), 79: (1,0,1,0),
   80: (0,0,0,0), 81: (0,1,0,0), 82: (0,0,0,0), 83: (1,0,0,0), 84: (0,0,0,0),
   85: (0,1,0,0), 86: (0,0,0,0), 87: (0,0,1,0), 88: (0,0,0,0), 89: (0,0,0,0),
   90: (0,0,0,0), 91: (0,1,0,0), 92: (0,0,0,0), 93: (0,1,0,0), 94: (1,0,1,0),
   95: (0,0,0,0), 96: (0,0,0,0), 97: (0,0,0,0), 98: (0,1,0,0), 99: (0,0,0,0),
  100: (0,0,0,0),101: (0,0,0,0),102: (0,0,0,0),103: (1,0,0,0),104: (0,1,0,0),
  105: (0,1,0,0),106: (0,0,0,0),107: (0,0,0,0),108: (0,0,0,0),109: (0,0,0,0),
  110: (0,0,1,1),111: (0,0,0,0),112: (1,0,0,0),113: (0,0,0,0),114: (0,0,0,0),
  115: (0,0,1,0),116: (0,0,1,0),117: (1,0,1,0),118: (0,0,0,0),119: (0,0,0,0),
  120: (0,0,0,0),121: (0,1,0,0),122: (0,0,0,0),123: (0,0,0,0),124: (0,1,0,0),
  125: (0,0,0,0),126: (0,0,0,0),127: (0,0,0,0),128: (0,0,0,0),129: (0,0,1,0),
  130: (0,0,0,0),131: (0,0,1,0),132: (0,0,0,0),133: (1,0,0,0),134: (0,0,0,0),
  135: (0,1,0,0),136: (0,0,0,0),137: (1,0,1,0),138: (0,0,1,1),139: (0,0,0,0),
  140: (1,0,0,0),141: (0,1,0,0),142: (0,0,0,0),143: (0,0,0,0),144: (0,0,0,0),
  145: (0,1,0,0),146: (0,0,0,0),147: (0,0,0,0),148: (0,0,0,0),149: (0,0,1,0),
  150: (0,1,0,0),151: (0,0,0,0),152: (1,0,0,0),153: (0,0,0,0),154: (0,0,0,0),
  155: (0,0,0,0),156: (0,0,0,0),157: (0,0,0,0),158: (0,0,1,0),159: (0,0,0,0),
  160: (0,0,0,0),161: (0,0,0,0),162: (0,0,1,0),163: (0,1,0,0),164: (0,1,0,0),
  165: (1,0,1,0),166: (0,0,0,0),167: (0,0,0,0),168: (0,0,0,0),169: (1,0,1,0),
  170: (1,1,0,0),171: (0,0,0,0),172: (0,0,0,0),173: (0,1,1,0),174: (0,1,0,0),
  175: (0,0,0,0),176: (0,0,0,0),177: (0,1,0,0),178: (0,0,0,0),179: (0,0,0,0),
  180: (0,1,0,0),181: (0,1,0,0),182: (0,0,0,0),183: (0,0,0,0),184: (0,0,0,0),
  185: (0,0,1,0),186: (0,1,0,0),187: (1,0,0,0),188: (0,0,1,1),189: (1,0,1,0),
  190: (0,1,0,0),191: (0,0,0,0),192: (1,0,1,0),193: (0,0,0,0),194: (1,0,0,0),
  195: (0,0,0,0),196: (0,1,0,0),197: (0,0,0,0),198: (0,1,0,0),199: (0,1,0,0),
}
assert len(CLAUDE_CODES) == 200, f"Expected 200, got {len(CLAUDE_CODES)}"

# Load the user's coded sheet and merge in Claude's codes
df = pd.read_csv("validation_user_coded.csv")
df["claude_benign_envy"]    = [CLAUDE_CODES[i][0] for i in range(len(df))]
df["claude_malicious_envy"] = [CLAUDE_CODES[i][1] for i in range(len(df))]
df["claude_psi"]            = [CLAUDE_CODES[i][2] for i in range(len(df))]
df["claude_purchase_intent"]= [CLAUDE_CODES[i][3] for i in range(len(df))]

# Reorder for easier human reading
cols = ["id","matched_influencer","influencer_tier","subreddit","body",
        "human_benign_envy","claude_benign_envy",
        "human_malicious_envy","claude_malicious_envy",
        "human_psi","claude_psi",
        "human_purchase_intent","claude_purchase_intent"]
df[cols].to_csv("validation_two_coders.csv", index=False)
print(f"Saved validation_two_coders.csv ({len(df)} rows, {len(cols)} cols)")

# ---------- AGREEMENT ANALYSIS ----------
print("\n" + "="*72)
print("CODING DISTRIBUTION COMPARISON")
print("="*72)
print(f"{'Construct':<22}{'User n=1':<12}{'Claude n=1':<14}{'Diff':<8}")
print("-"*72)
for c in ["benign_envy","malicious_envy","psi","purchase_intent"]:
    u = int(df[f"human_{c}"].sum())
    cl = int(df[f"claude_{c}"].sum())
    print(f"{c:<22}{u:<12}{cl:<14}{cl-u:+d}")

print("\n" + "="*72)
print("INTER-CODER AGREEMENT (User vs Claude)")
print("="*72)
from sklearn.metrics import cohen_kappa_score, confusion_matrix
print(f"{'Construct':<22}{'Agreement':<12}{'kappa':<10}{'Disagreements'}")
print("-"*72)
for c in ["benign_envy","malicious_envy","psi","purchase_intent"]:
    u = df[f"human_{c}"].astype(int)
    cl = df[f"claude_{c}"].astype(int)
    agreement = (u == cl).mean()
    kappa = cohen_kappa_score(u, cl)
    disagreements = int((u != cl).sum())
    print(f"{c:<22}{agreement:<12.3f}{kappa:<10.3f}{disagreements}")

print("\n" + "="*72)
print("CONFUSION MATRIX (User rows, Claude columns)")
print("="*72)
for c in ["benign_envy","malicious_envy","psi","purchase_intent"]:
    cm = confusion_matrix(df[f"human_{c}"].astype(int), df[f"claude_{c}"].astype(int), labels=[0,1])
    print(f"\n  {c}")
    print(f"             Claude=0  Claude=1")
    print(f"  User=0     {cm[0,0]:<10}{cm[0,1]}")
    print(f"  User=1     {cm[1,0]:<10}{cm[1,1]}")

# Now compare BOTH coders against the DeBERTa classifier
print("\n" + "="*72)
print("DEBERTA CLASSIFIER vs EACH HUMAN CODER (F1 at threshold 0.5)")
print("="*72)
clf = pd.read_csv("validation_sample_full.csv")
merged = df.merge(clf[["id","benign_envy","malicious_envy","psi","purchase_intent"]],
                  on="id", suffixes=("","_clf"))
from sklearn.metrics import precision_recall_fscore_support
THR = 0.5
print(f"{'Construct':<22}{'vs USER':<22}{'vs CLAUDE':<22}")
print(f"{'':22}{'P/R/F1':<22}{'P/R/F1':<22}")
print("-"*72)
for c in ["benign_envy","malicious_envy","psi","purchase_intent"]:
    y_pred = (merged[c] >= THR).astype(int)
    yu = merged[f"human_{c}"].astype(int)
    yc = merged[f"claude_{c}"].astype(int)
    pu,ru,fu,_ = precision_recall_fscore_support(yu, y_pred, average="binary", zero_division=0)
    pc,rc,fc,_ = precision_recall_fscore_support(yc, y_pred, average="binary", zero_division=0)
    print(f"{c:<22}{pu:.2f}/{ru:.2f}/{fu:.2f}        {pc:.2f}/{rc:.2f}/{fc:.2f}")
