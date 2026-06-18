"""
power_analysis.py
-----------------
Calculate required sample size per cell for the 2^3 factorial experiment.

Business context:
- Baseline conversion: 8%
- MDE: +3 percentage points (minimum business-meaningful improvement)
- Alpha: 0.05, Power: 0.80
"""

import numpy as np
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize
import matplotlib.pyplot as plt


# ── Parameters ────────────────────────────────────────────────────────────────

BASELINE_RATE   = 0.08   # current free-to-paid conversion
MDE             = 0.03   # minimum detectable effect (pp)
ALPHA           = 0.05
POWER           = 0.80
N_FACTORS       = 3      # A, B, C
N_CELLS         = 2 ** N_FACTORS  # 8 treatment combinations


# ── Sample Size Calculation ───────────────────────────────────────────────────

def calculate_sample_size(baseline, mde, alpha, power):
    """
    Calculate n per group using Cohen's h effect size for proportions.
    Returns n per cell (not total).
    """
    variant_rate = baseline + mde
    effect_size  = proportion_effectsize(baseline, variant_rate)

    analysis = NormalIndPower()
    n_per_group = analysis.solve_power(
        effect_size=effect_size,
        alpha=alpha,
        power=power,
        alternative="two-sided"
    )
    return int(np.ceil(n_per_group))


def print_sample_size_summary(n_per_cell):
    total = n_per_cell * N_CELLS
    print("=" * 50)
    print("  POWER ANALYSIS SUMMARY")
    print("=" * 50)
    print(f"  Baseline conversion rate : {BASELINE_RATE:.0%}")
    print(f"  Minimum detectable effect: +{MDE:.0%}")
    print(f"  Significance level (α)   : {ALPHA}")
    print(f"  Statistical power        : {POWER:.0%}")
    print(f"  Treatment combinations   : {N_CELLS}")
    print("-" * 50)
    print(f"  Required per cell        : {n_per_cell:,} users")
    print(f"  Total required           : {total:,} users")
    print("=" * 50)
    return total


# ── Sensitivity Analysis ──────────────────────────────────────────────────────

def plot_sensitivity(baseline, alpha, power, total=None, save_path=None):
    """
    Show how required sample size changes with different MDE assumptions.
    total: actual factorial sample size to draw horizontal reference line.
           If not provided, calculated from MDE and N_CELLS.
    """
    mde_values = np.arange(0.01, 0.08, 0.005)
    n_values   = []
 
    for mde in mde_values:
        # Factorial: effective n per side = n_per_cell x (N_CELLS/2)
        n_eff = calculate_sample_size(baseline, mde, alpha, power)
        n_per_cell = int(np.ceil(n_eff / (N_CELLS / 2)))
        n_values.append(n_per_cell * N_CELLS)
 
    # Use provided total or calculate from MDE
    if total is None:
        n_eff  = calculate_sample_size(baseline, MDE, alpha, power)
        total  = int(np.ceil(n_eff / (N_CELLS / 2))) * N_CELLS
 
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(mde_values * 100, n_values, color="#2563EB", linewidth=2.5)
    ax.axvline(x=MDE * 100, color="#DC2626", linestyle="--", linewidth=1.5,
               label=f"Chosen MDE = {MDE:.0%}")
    ax.axhline(y=total, color="#DC2626", linestyle=":", linewidth=1,
               label=f"Factorial sample size = {total:,}")
 
    ax.set_xlabel("Minimum Detectable Effect (percentage points)", fontsize=12)
    ax.set_ylabel("Total Sample Size Required", fontsize=12)
    ax.set_title("Sample Size vs Detectable Effect\n(α=0.05, Power=80%, 8 treatment cells)",
                 fontsize=13, fontweight="bold")
    ax.legend(fontsize=10, loc="upper right")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
 
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Plot saved → {save_path}")
    else:
        plt.show()
    plt.close()


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    n_per_cell = calculate_sample_size(BASELINE_RATE, MDE, ALPHA, POWER)
    total      = print_sample_size_summary(n_per_cell)

    plot_sensitivity(
        baseline  = BASELINE_RATE,
        alpha     = ALPHA,
        power     = POWER,
        save_path = "../outputs/power_sensitivity.png"
    )