"""
interaction_plots.py
--------------------
Visualize experiment results:
  1. Main effects plot — individual impact of A, B, C
  2. Interaction plot — B × C (the key finding)
  3. All-effects bar chart — ranked by effect size
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Style ──────────────────────────────────────────────────────────────────────

BLUE    = "#2563EB"
RED     = "#DC2626"
GREY    = "#6B7280"
GREEN   = "#16A34A"
LIGHT   = "#F3F4F6"

plt.rcParams.update({
    "font.family":    "sans-serif",
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.grid":          True,
    "grid.alpha":         0.3,
    "grid.linestyle":     "--",
})


# ── 1. Main Effects Plot ───────────────────────────────────────────────────────

def plot_main_effects(df, save_path=None):
    """
    For each factor, show mean conversion at -1 vs +1 level.
    """
    factors = {
        "A": ("Grey", "Blue CTA"),
        "B": ("3 emails", "7 emails"),
        "C": ("Tooltip Off", "Tooltip On"),
    }

    fig, axes = plt.subplots(1, 3, figsize=(13, 5), sharey=True)
    fig.suptitle("Main Effects: Individual Factor Impact on Conversion",
                 fontsize=14, fontweight="bold", y=1.02)

    for ax, (factor, (low_label, high_label)) in zip(axes, factors.items()):
        means = df.groupby(factor)["converted"].mean() * 100
        low   = means[-1]
        high  = means[+1]
        delta = high - low

        ax.plot([-1, 1], [low, high],
                color=BLUE, linewidth=2.5, marker="o", markersize=9, zorder=3)

        ax.fill_between([-1, 1], [low, high], alpha=0.08, color=BLUE)

        ax.set_xticks([-1, 1])
        ax.set_xticklabels([low_label, high_label], fontsize=10)
        ax.set_ylabel("Conversion Rate (%)", fontsize=11)
        ax.set_title(f"Factor {factor}\nΔ = {delta:+.1f}pp", fontsize=12, fontweight="bold")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.1f}%"))

        # Annotate points
        ax.annotate(f"{low:.1f}%",  xy=(-1, low),  xytext=(-1.2, low),  fontsize=10, ha="right")
        ax.annotate(f"{high:.1f}%", xy=(+1, high), xytext=(+1.05, high), fontsize=10)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Main effects plot saved → {save_path}")
    else:
        plt.show()
    plt.close()


# ── 2. Interaction Plot: B × C ────────────────────────────────────────────────

def plot_bc_interaction(df, save_path=None):
    """
    The key finding: tooltip only works when paired with 7-email sequence.
    """
    means = df.groupby(["B", "C"])["converted"].mean() * 100

    b_labels = ["3 emails", "7 emails"]
    x_pos    = [0, 1]

    c_minus1 = [means[(-1.0, -1.0)], means[(1.0, -1.0)]]  # Tooltip Off
    c_plus1  = [means[(-1.0,  1.0)], means[(1.0,  1.0)]]  # Tooltip On

    fig, ax = plt.subplots(figsize=(7, 5))

    ax.plot(x_pos, c_minus1, color=GREY, linewidth=2.5,
            marker="o", markersize=10, label="Tooltip OFF", linestyle="--")
    ax.plot(x_pos, c_plus1,  color=BLUE, linewidth=2.5,
            marker="o", markersize=10, label="Tooltip ON")

    # Annotate endpoints
    for xi, y in zip(x_pos, c_minus1):
        ax.annotate(f"{y:.1f}%", xy=(xi, y), xytext=(8, -14),
                    textcoords="offset points", fontsize=10, color=GREY)
    for xi, y in zip(x_pos, c_plus1):
        ax.annotate(f"{y:.1f}%", xy=(xi, y), xytext=(8, 6),
                    textcoords="offset points", fontsize=10, color=BLUE)

    # Highlight interaction gap at 7 emails (x=1)
    y_off = c_minus1[1]
    y_on  = c_plus1[1]
    ax.annotate("",
                xy=(1, y_on), xytext=(1, y_off),
                arrowprops=dict(arrowstyle="<->", color=RED, lw=2))
    ax.text(1.06, (y_off + y_on) / 2,
            f"+{y_on - y_off:.1f}pp\ninteraction",
            color=RED, fontsize=10, va="center")

    ax.set_xticks(x_pos)
    ax.set_xticklabels(b_labels, fontsize=11)
    ax.set_xlim(-0.3, 1.5)
    ax.set_title("Interaction Effect: Email Sequence x Tooltip\n"
                 "Tooltip only adds value with the longer email sequence",
                 fontsize=12, fontweight="bold")
    ax.set_ylabel("Conversion Rate (%)", fontsize=11)
    ax.set_xlabel("Email Sequence", fontsize=11)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.1f}%"))
    ax.legend(fontsize=11, loc="upper left")
    fig.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Interaction plot saved → {save_path}")
    else:
        plt.show()
    plt.close()


# ── 3. Effects Bar Chart ──────────────────────────────────────────────────────

def plot_effects_bar(effects_df, save_path=None):
    """
    Ranked bar chart of all effect sizes. Significant effects highlighted.
    """
    df = effects_df[effects_df["term"] != "Intercept"].copy()
    df = df.sort_values("effect_pp", ascending=True)

    colors = [GREEN if s == "✅" else GREY for s in df["significant"]]

    fig, ax = plt.subplots(figsize=(9, 6))

    bars = ax.barh(df["term"], df["effect_pp"], color=colors, edgecolor="white",
                   height=0.6)

    # Error bars (95% CI)
    ax.errorbar(
        df["effect_pp"],
        range(len(df)),
        xerr=[df["effect_pp"] - df["ci_low_pp"],
              df["ci_high_pp"] - df["effect_pp"]],
        fmt="none", color="#111827", capsize=4, linewidth=1.5
    )

    ax.axvline(0, color="#111827", linewidth=1)

    # Annotate values
    for bar, (_, row) in zip(bars, df.iterrows()):
        xpos = row["effect_pp"] + (0.1 if row["effect_pp"] >= 0 else -0.1)
        ha   = "left" if row["effect_pp"] >= 0 else "right"
        ax.text(xpos, bar.get_y() + bar.get_height() / 2,
                f"{row['effect_pp']:+.1f}pp  {row['significant']}",
                va="center", ha=ha, fontsize=10)

    sig_patch  = mpatches.Patch(color=GREEN, label="Statistically significant (p < 0.05)")
    nsig_patch = mpatches.Patch(color=GREY,  label="Not significant")
    ax.legend(handles=[sig_patch, nsig_patch], fontsize=10, loc="lower right")

    ax.set_title("Effect Size Estimates — All Factorial Terms\n(with 95% confidence intervals)",
                 fontsize=13, fontweight="bold")
    ax.set_xlabel("Effect on Conversion Rate (percentage points)", fontsize=11)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:+.1f}pp"))
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Effects bar chart saved → {save_path}")
    else:
        plt.show()
    plt.close()


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    df      = pd.read_csv("../outputs/experiment_data.csv")
    effects = pd.read_csv("../outputs/anova_table.csv")

    plot_main_effects(df,   save_path="../outputs/main_effects_plot.png")
    plot_bc_interaction(df, save_path="../outputs/interaction_plot.png")
    plot_effects_bar(effects, save_path="../outputs/effects_bar_chart.png")

    print("\n  All plots generated successfully.")