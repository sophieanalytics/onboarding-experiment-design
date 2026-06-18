# SaaS Onboarding Optimization — Multi-variate Experiment

> **Role:** Senior Product Analyst  
> **Methods:** Factorial Experiment Design, ANOVA, Interaction Analysis  
> **Tools:** Python (statsmodels, pandas, matplotlib, pyDOE2)


## Business Context

A B2B SaaS company is experiencing a **below-benchmark free-to-paid conversion rate of 8%** during the 14-day trial period. The product team has three candidate changes ready to ship. However, limited engineering capacity means we need to know *which combination* to prioritize, not just which individual changes work.

**The ask:** Run a single experiment that identifies the highest-converting onboarding combination, including whether any changes *amplify each other* when used together.


## The Problem with Testing One Thing at a Time

The default approach, which are three sequential A/B tests, has two critical flaws:

1. **It misses interaction effects.** Some changes only work *in combination*. A tooltip might have zero impact alone, but significantly boost conversion when paired with a longer email sequence. Sequential testing would incorrectly conclude "tooltips don't work" and never ship the winning combination.

2. **It's slow.** Three sequential tests at standard duration = 3× the time to a decision.

**Solution:** Test all three factors simultaneously in a single structured experiment, designed to detect both individual effects and interactions.


## What We Tested

| Factor | Control | Variant |
|--------|---------|---------|
| **A** - CTA Button Color | Grey | Blue |
| **B** - Onboarding Email Sequence | 3 emails | 7 emails |
| **C** - Feature Tooltip | Off | On |

8 treatment combinations. ~373 users per combination. ~2,984 users total.

**Primary metric:** Free-to-paid conversion within 14 days  
**Guardrail metrics:** Support ticket volume, unsubscribe rate

## Sample Size & Duration

- Baseline conversion: **8%**
- Minimum business-meaningful improvement: **+3 percentage points**
  *(below this, the revenue impact does not justify engineering cost)*
- Significance level: 95% | Power: 80%
- **Required: ~2,984 users → ~0.7 weeks at current trial volume**

![Power Sensitivity](outputs/power_sensitivity.png)

## Results

### What moved the needle

| Change | Effect on Conversion | Significant? |
|--------|---------------------|-------------|
| Blue CTA (A) | +2.55pp | ✅ Yes |
| 7-email sequence (B) | +2.95pp | ✅ Yes |
| Tooltip (C) | +1.21pp | ❌ No|
| **7-email + Tooltip (B×C)** | **+2.55pp** | **✅ Yes** |

All effects estimated from 2,984 simulated users across 8 treatment 
combinations (373 users per cell). Effect sizes represent the change 
in conversion rate when moving from control (−1) to variant (+1), 
averaged across all other factor combinations.

The BC interaction is the standout finding because tooltip delivers no significant value alone, but adds +2.55pp on top of the email 
sequence effect when both are shipped together.

![Power Sensitivity](outputs/effects_bar_chart.png)

## Business Recommendation

### Decision

Ship Blue CTA (A), 7-email sequence (B), and Tooltip (C) together.

A and B are independently significant. Tooltip alone shows no significant effect,
but the Email × Tooltip interaction (BC) is confirmed significant at p=0.0098 —
meaning tooltip delivers meaningful value when users have already received the
full email sequence. Shipping all three together maximises the combined lift.

![Power Sensitivity](outputs/main_effects_plot.png)

### Revenue Impact

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Conversion Rate | 8.0% | 16.1% | +8.1pp |
| Paid Users / month | 800 | 1,610 | +810 |
| ARR | £240,000 | £483,000 | **+£243,000** |
 
*Projection includes confirmed effects: A (+2.55pp) + B (+2.95pp) + BC (+2.55pp)*


### Implementation Order

**Ship B + C together first** — the email sequence and tooltip are interdependent.
Tooltip delivers no value without the longer email sequence in place, so they
must be shipped as a pair.
 
**Sprint 1: 7-email sequence (B) + Tooltip (C)**
- Ship together — tooltip is only effective alongside the extended email sequence
- Monitor conversion for 2 weeks before Sprint 2

**Sprint 2: Blue CTA (A)**
- Independent effect, no dependency on B or C
- Safe to ship at any point; layering on top confirms additional +2.55pp

### What Not to Ship

**Tooltip in isolation — do not ship separately.**
Tooltip alone is not statistically significant (p=0.22). The interaction plot
shows tooltip may actually *hurt* conversion when paired with only 3 emails
(5.8% vs 7.1%). Only ship tooltip as part of the B+C bundle.

## Key Insight
 
> Sequential A/B testing would have concluded "tooltip doesn't work" and never
> shipped it. The factorial design reveals tooltip works — but only in the right
> context. This +2.55pp interaction effect represents £76,500 ARR that a
> traditional testing approach would have left on the table.

![Power Sensitivity](outputs/interaction_plot.png)

### Post-launch Monitoring

- Track conversion daily for 30 days after rollout
- Watch for novelty effect decay after Week 2
- Monitor support ticket volume and unsubscribe rate as guardrail metrics
- If BC effect persists at 30 days, explore optimising email frequency beyond the binary 3 vs 7 tested here

### Limitations

- **Simulated data, not real users** Every insight is based on data we generated ourselves with known true effects. In reality, user behavior is messier. Therefore, effects may be smaller, noisier, or in the opposite direction
- **No blocking by user segment** In reality, conversion rates differ significantly across plan type and device. A blocked factorial design would have removed this variance and improved detection power, particularly for smaller effects like the BC interaction.

---

## Repository Structure

```
saas-onboarding-factorial-experiment/
│
├── README.md
├── notebooks/
│   └── full_analysis.ipynb
├── src/
│   ├── data_generation.py
│   ├── design_matrix.py
│   ├── anova_analysis.py
│   ├── interaction_plots.py
│   └── power_analysis.py
└── outputs/
    ├── effects_bar_chart.png
    ├── interaction_plot.png
    └── main_effects_plot.png
    └── power_sensitivity.png
```