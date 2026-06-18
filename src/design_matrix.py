"""
design_matrix.py
----------------
Build the 2^3 full factorial design matrix.

Factors:
  A — CTA Button Color     : -1 = Grey (control), +1 = Blue (variant)
  B — Email Sequence       : -1 = 3 emails,       +1 = 7 emails
  C — Feature Tooltip      : -1 = Off,             +1 = On
"""

import numpy as np
import pandas as pd


# ── Factor Definitions ────────────────────────────────────────────────────────

FACTORS = {
    "A_cta_color":      {-1.0: "Grey (control)",  1.0: "Blue (variant)"},
    "B_email_sequence": {-1.0: "3 emails",         1.0: "7 emails"},
    "C_tooltip":        {-1.0: "Off",              1.0: "On"},
}

FACTOR_LABELS = list(FACTORS.keys())


# ── Build Design Matrix ───────────────────────────────────────────────────────

def build_design_matrix():
    """
    Generate 2^3 full factorial design in coded units (-1, +1).
    Add interaction columns: AB, AC, BC, ABC.
    Returns a DataFrame with all main effects and interactions.
    """
    # Hardcoded 2^3 full factorial — no external library dependency
    coded = np.array([
        [-1, -1, -1],
        [-1, -1, +1],
        [-1, +1, -1],
        [-1, +1, +1],
        [+1, -1, -1],
        [+1, -1, +1],
        [+1, +1, -1],
        [+1, +1, +1],
    ], dtype=float)

    df = pd.DataFrame(coded, columns=["A", "B", "C"])
    df.index = df.index + 1  # runs start at 1
    df.index.name = "run"

    # Interaction columns
    df["AB"]  = df["A"] * df["B"]
    df["AC"]  = df["A"] * df["C"]
    df["BC"]  = df["B"] * df["C"]
    df["ABC"] = df["A"] * df["B"] * df["C"]

    return df


def add_labels(design_df):
    """
    Add human-readable labels for each factor level.
    """
    df = design_df.copy()
    for col, factor_key in zip(["A", "B", "C"], FACTOR_LABELS):
        mapping = FACTORS[factor_key]
        df[f"{col}_label"] = df[col].map(mapping)
    return df


def print_design(design_df):
    labeled = add_labels(design_df)

    print("=" * 70)
    print("  2^3 FULL FACTORIAL DESIGN MATRIX")
    print("=" * 70)
    print(f"  Factors  : A (CTA Color), B (Email Sequence), C (Tooltip)")
    print(f"  Levels   : -1 = Control, +1 = Variant")
    print(f"  Runs     : {len(design_df)}")
    print("-" * 70)

    display_cols = ["A", "B", "C", "AB", "AC", "BC", "ABC",
                    "A_label", "B_label", "C_label"]
    print(labeled[display_cols].to_string())
    print("=" * 70)


def save_design(design_df, path="../outputs/design_matrix.csv"):
    labeled = add_labels(design_df)
    labeled.to_csv(path)
    print(f"  Design matrix saved → {path}")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    design = build_design_matrix()
    print_design(design)
    save_design(design)