"""
anova_analysis.py
-----------------
Fit OLS linear model on the factorial experiment data.
Extract main effects, interaction effects, p-values, and confidence intervals.

Model:
  Y = β0 + βA·A + βB·B + βC·C + βAB·AB + βAC·AC + βBC·BC + βABC·ABC + ε

In coded (-1/+1) units, each coefficient = half the effect size.
Effect = 2 × coefficient.
"""

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import statsmodels.api as sm
from scipy.stats import shapiro
import warnings
warnings.filterwarnings("ignore")


# ── Fit Model ─────────────────────────────────────────────────────────────────

def fit_model(df):
    """
    Fit OLS model with all main effects and interactions.
    Returns the fitted model object.
    """
    formula = "converted ~ A + B + C + A:B + A:C + B:C + A:B:C"
    model   = smf.ols(formula, data=df).fit()
    return model


# ── Extract Effects Table ─────────────────────────────────────────────────────

TERM_LABELS = {
    "Intercept": "Baseline (Intercept)",
    "A":         "A — CTA Color",
    "B":         "B — Email Sequence",
    "C":         "C — Tooltip",
    "A:B":       "AB — CTA × Email",
    "A:C":       "AC — CTA × Tooltip",
    "B:C":       "BC — Email × Tooltip ⭐",
    "A:B:C":     "ABC — Three-way",
}

def extract_effects(model):
    """
    Convert model coefficients to effect sizes (2 × coef in coded units).
    Effect size = change in conversion probability when factor goes from -1 to +1.
    """
    results = []

    for term, label in TERM_LABELS.items():
        if term not in model.params.index:
            continue

        coef    = model.params[term]
        se      = model.bse[term]
        pval    = model.pvalues[term]
        ci_low  = model.conf_int().loc[term, 0]
        ci_high = model.conf_int().loc[term, 1]

        # Effect = 2 × coef (coded contrast)
        effect      = coef * 2 if term != "Intercept" else coef
        effect_pp   = effect * 100
        ci_low_pp   = ci_low  * 2 * 100 if term != "Intercept" else ci_low  * 100
        ci_high_pp  = ci_high * 2 * 100 if term != "Intercept" else ci_high * 100

        sig = "✅" if pval < 0.05 else "❌"

        results.append({
            "term":        term,
            "label":       label,
            "effect_pp":   round(effect_pp, 2),
            "ci_low_pp":   round(ci_low_pp, 2),
            "ci_high_pp":  round(ci_high_pp, 2),
            "p_value":     round(pval, 4),
            "significant": sig,
        })

    return pd.DataFrame(results)


# ── Multiple Testing Correction ───────────────────────────────────────────────

def apply_bonferroni(effects_df, n_tests=7):
    """
    Apply Bonferroni correction to p-values (excluding intercept).
    Adjusted alpha = 0.05 / 7 ≈ 0.007
    """
    df = effects_df.copy()
    alpha_adjusted = 0.05 / n_tests

    df["p_bonferroni"]    = (df["p_value"] * n_tests).clip(upper=1.0).round(4)
    df["sig_bonferroni"]  = df["p_bonferroni"].apply(
        lambda p: "✅" if p < 0.05 else "❌"
    )
    df["alpha_adjusted"]  = alpha_adjusted

    return df


# ── Residual Diagnostics ──────────────────────────────────────────────────────

def check_residuals(model):
    """
    Shapiro-Wilk normality test on residuals.
    For large n, residuals will be approximately normal — this is a sanity check.
    """
    residuals = model.resid
    stat, pval = shapiro(residuals[:500])  # Shapiro reliable up to n=5000

    status = "✅ PASS" if pval > 0.05 else "⚠️  CHECK"
    print(f"\n  Shapiro-Wilk normality test: W={stat:.4f}, p={pval:.4f}  {status}")
    if pval <= 0.05:
        print("  → Minor violation expected for binary outcomes at large n. "
              "Consider logistic regression for final model.")


# ── Print Summary ─────────────────────────────────────────────────────────────

def print_effects_table(effects_df):
    print("=" * 75)
    print("  FACTORIAL EFFECTS TABLE  (effect = change in conversion rate pp)")
    print("=" * 75)
    print(f"  {'Term':<30} {'Effect':>8}  {'95% CI':^18}  {'p-value':>8}  {'Sig':>4}")
    print("  " + "-" * 70)

    for _, row in effects_df.iterrows():
        if row["term"] == "Intercept":
            continue
        ci = f"[{row['ci_low_pp']:+.1f}, {row['ci_high_pp']:+.1f}]"
        print(f"  {row['label']:<30} {row['effect_pp']:>+7.2f}pp  "
              f"{ci:^18}  {row['p_value']:>8.4f}  {row['significant']:>4}")

    print("=" * 75)


def print_model_fit(model):
    print(f"\n  Model R²: {model.rsquared:.4f}  |  "
          f"Adj. R²: {model.rsquared_adj:.4f}  |  "
          f"F-stat p-value: {model.f_pvalue:.4e}")


# ── Save ──────────────────────────────────────────────────────────────────────

def save_effects(effects_df, path="../outputs/anova_table.csv"):
    effects_df.to_csv(path, index=False)
    print(f"\n  ANOVA table saved → {path}")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Load simulated data
    df = pd.read_csv("../outputs/experiment_data.csv")

    # Fit model
    model = fit_model(df)

    # Extract and display effects
    effects = extract_effects(model)
    effects = apply_bonferroni(effects)

    print_effects_table(effects)
    print_model_fit(model)
    check_residuals(model)
    save_effects(effects)