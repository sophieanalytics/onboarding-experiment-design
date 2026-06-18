"""
data_generation.py
------------------
Simulate user-level conversion data for the 2^3 factorial experiment.

True effects injected (ground truth we expect ANOVA to recover):
  A  (CTA Color)      : +0.025  (+2.5pp)
  B  (Email Sequence) : +0.030  (+3.0pp)
  C  (Tooltip)        : +0.010  (+1.0pp)  — not significant alone
  BC (Email × Tooltip): +0.020  (+2.0pp)  — key interaction
  AB, AC, ABC         :  0.000  (no effect)

Baseline conversion: 8%
"""

import numpy as np
import pandas as pd
from design_matrix import build_design_matrix

# ── Ground Truth Parameters ───────────────────────────────────────────────────

SEED             = 42
BASELINE         = 0.08
N_PER_CELL       = 400   # users per treatment combination

TRUE_EFFECTS = {
    "A":   0.025,   # CTA color
    "B":   0.030,   # email sequence
    "C":   0.010,   # tooltip (not significant alone)
    "AB":  0.000,
    "AC":  0.000,
    "BC":  0.020,   # KEY interaction: tooltip amplifies email
    "ABC": 0.000,
}


# ── Conversion Probability per Cell ──────────────────────────────────────────

def cell_conversion_probability(row):
    """
    Compute true conversion probability for a given design cell.
    Uses the coded (-1/+1) values and true effect sizes.
    """
    p = BASELINE
    for col, effect in TRUE_EFFECTS.items():
        p += row[col] * effect * 0.5  # coded contrast → half-effect
    # Clip to valid probability range
    return np.clip(p, 0.01, 0.99)


# ── Simulate Data ─────────────────────────────────────────────────────────────

def simulate_data(n_per_cell=400, seed=SEED):
    """
    Generate user-level Bernoulli conversion outcomes.

    Returns a DataFrame with one row per user:
      - user_id
      - run (which of the 8 design cells)
      - A, B, C (coded factor values)
      - A_label, B_label, C_label (human-readable)
      - true_prob (ground truth conversion probability)
      - converted (0/1 outcome)
    """
    np.random.seed(seed)
    design = build_design_matrix()

    records = []
    user_id = 1

    for run, row in design.iterrows():
        p_true = cell_conversion_probability(row)

        outcomes = np.random.binomial(1, p_true, size=n_per_cell)

        for outcome in outcomes:
            records.append({
                "user_id":   user_id,
                "run":       run,
                "A":         int(row["A"]),
                "B":         int(row["B"]),
                "C":         int(row["C"]),
                "AB":        int(row["AB"]),
                "AC":        int(row["AC"]),
                "BC":        int(row["BC"]),
                "ABC":       int(row["ABC"]),
                "true_prob": round(p_true, 4),
                "converted": int(outcome),
            })
            user_id += 1

    df = pd.DataFrame(records)

    # Human-readable labels
    df["A_label"] = df["A"].map({-1: "Grey",    +1: "Blue"})
    df["B_label"] = df["B"].map({-1: "3 emails", +1: "7 emails"})
    df["C_label"] = df["C"].map({-1: "Off",      +1: "On"})

    return df


# ── Validation ────────────────────────────────────────────────────────────────

def validate_data(df):
    """
    Check SRM (Sample Ratio Mismatch) and print observed vs expected conversion.
    Expected n per cell is inferred from the data itself.
    """
    print("=" * 60)
    print("  DATA VALIDATION")
    print("=" * 60)

    # SRM check — infer expected from actual data, not hardcode
    cell_counts = df.groupby("run").size()
    expected    = cell_counts.mean()  # use actual mean as expected
    max_deviation = ((cell_counts - expected) / expected).abs().max()
    srm_status  = "✅ PASS" if max_deviation < 0.02 else "❌ FAIL"
    print(f"\n  SRM Check (max deviation from expected): "
          f"{max_deviation:.1%}  {srm_status}")

    # Observed vs true conversion per cell
    summary = df.groupby("run").agg(
        n         = ("converted", "count"),
        true_prob = ("true_prob", "first"),
        observed  = ("converted", "mean"),
    ).reset_index()
    summary["delta"] = summary["observed"] - summary["true_prob"]

    print("\n  Observed vs True Conversion by Cell:\n")
    print(f"  {'Run':>4}  {'N':>6}  {'True':>8}  {'Observed':>10}  {'Delta':>8}")
    print("  " + "-" * 44)
    for _, r in summary.iterrows():
        print(f"  {int(r['run']):>4}  {int(r['n']):>6}  "
              f"{r['true_prob']:>8.1%}  {r['observed']:>10.1%}  "
              f"{r['delta']:>+8.1%}")

    print(f"\n  Total users: {len(df):,}")
    print(f"  Overall conversion: {df['converted'].mean():.1%}")
    print("=" * 60)


def save_data(df, path="../outputs/experiment_data.csv"):
    df.to_csv(path, index=False)
    print(f"\n  Data saved → {path}  ({len(df):,} rows)")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    df = simulate_data()
    validate_data(df)
    save_data(df)