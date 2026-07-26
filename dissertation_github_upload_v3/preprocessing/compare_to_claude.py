"""
Run on your local machine after downloading validation_two_coders.csv
into the same folder as comments_scored.csv.

Computes DeBERTa classifier F1 against both human coders (you + Claude)
and compares them. If Claude-F1 is much higher than your-F1 for a given
construct, that construct's apparent failure was actually due to over-
strict human coding, not classifier failure.
"""
import pandas as pd
from sklearn.metrics import (precision_recall_fscore_support,
                              cohen_kappa_score, accuracy_score,
                              confusion_matrix)
import numpy as np

# Load
two_coders = pd.read_csv("validation_two_coders.csv")
scored     = pd.read_csv("comments_scored.csv")
m = two_coders.merge(
    scored[["id","benign_envy","malicious_envy","psi","purchase_intent"]],
    on="id", suffixes=("","_clf"))
print(f"Merged: {len(m)} rows")

constructs = ["benign_envy","malicious_envy","psi","purchase_intent"]

# ---- F1 vs each coder at threshold 0.5 ----
print("\n" + "="*78)
print("DeBERTa vs each human coder (threshold = 0.50)")
print("="*78)
print(f"{'Construct':<20}{'vs USER P/R/F1':<26}{'vs CLAUDE P/R/F1':<22}{'Δ F1'}")
print("-"*78)
for c in constructs:
    y_pred = (m[c] >= 0.5).astype(int)
    yu = m[f"human_{c}"].astype(int)
    yc = m[f"claude_{c}"].astype(int)
    pu,ru,fu,_ = precision_recall_fscore_support(yu, y_pred, average="binary", zero_division=0)
    pc,rc,fc,_ = precision_recall_fscore_support(yc, y_pred, average="binary", zero_division=0)
    print(f"{c:<20}{pu:.2f}/{ru:.2f}/{fu:.2f}              {pc:.2f}/{rc:.2f}/{fc:.2f}      {fc-fu:+.2f}")

# ---- Threshold-optimized F1 vs Claude ----
print("\n" + "="*78)
print("DeBERTa vs Claude — threshold-optimized F1")
print("="*78)
for c in constructs:
    yc = m[f"claude_{c}"].astype(int)
    best_f1, best_t = 0, 0.5
    for t in np.arange(0.05, 0.96, 0.05):
        y_pred = (m[c] >= t).astype(int)
        _,_,f,_ = precision_recall_fscore_support(yc, y_pred, average="binary", zero_division=0)
        if f > best_f1: best_f1, best_t = f, t
    print(f"  {c:<22} optimal threshold = {best_t:.2f}    F1 = {best_f1:.3f}")

# ---- Inter-coder agreement (already computed but reproducible) ----
print("\n" + "="*78)
print("Inter-coder agreement (User vs Claude)")
print("="*78)
print(f"{'Construct':<22}{'κ':<10}{'Agreement %'}")
print("-"*78)
for c in constructs:
    u = two_coders[f"human_{c}"].astype(int)
    cl = two_coders[f"claude_{c}"].astype(int)
    print(f"{c:<22}{cohen_kappa_score(u, cl):<10.3f}{(u==cl).mean()*100:.1f}")
