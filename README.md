# SaaS Onboarding Optimization - Multi-variate Experiment

> **Role:** Senior Product Analyst  
> **Methods:** Factorial Experiment Design, ANOVA, Interaction Analysis  
> **Tools:** Python (statsmodels, pandas, matplotlib, pyDOE2)


## Business Context

A B2B SaaS company has 10,000 month trial users and is experiencing a **below-benchmark free-to-paid conversion rate of 8%** during the 14-day trial period. The product team has three candidate changes ready to ship. However, limited engineering capacity means we need to know *which combination* to prioritize, not just which individual changes work.

**Requirement:** Run a single experiment that identifies the highest-converting onboarding combination, including whether any changes *amplify each other* when used together.


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

Since we're testing 3 changes at once, and each change has 2 versions 
(old vs new), there are 2 × 2 × 2 = 8 possible combinations a user could 
see

**Primary metric:** Free-to-paid conversion within 14 days  
**Guardrail metrics:** Support ticket volume, unsubscribe rate

## Sample Size & Duration

- Baseline conversion: **8%**
- Minimum business-meaningful improvement: **+3 percentage points**
- Significance level: 95% | Power: 80%
- **Recruitment: ~2,984 users → ~0.7 weeks to enroll all users**
- **Total experiment duration: ~3 weeks** (0.7 weeks enrollment + 14 days 
  conversion window for the last cohort to complete their trial)

![Power Sensitivity](outputs/power_sensitivity.png)


## Results

| Factor | Effect (pp) | CI Low | CI High | p-value | Significant |
|--------|------------|--------|---------|---------|-------------|
| A — CTA Color | 2.55 | 0.62 | 4.48 | 0.0098 | ✅ |
| B — Email Sequence | 2.95 | 1.02 | 4.88 | 0.0028 | ✅ |
| C — Tooltip | 1.21 | -0.72 | 3.14 | 0.2207 | ❌ |
| AB — CTA × Email | 0.40 | -1.53 | 2.33 | 0.6831 | ❌ |
| AC — CTA × Tooltip | -0.27 | -2.20 | 1.66 | 0.7855 | ❌ |
| **BC — Email × Tooltip** | **2.55** | **0.62** | **4.48** | **0.0098** | **✅** |
| ABC — Three-way | 1.61 | -0.32 | 3.54 | 0.1026 | ❌ |

Effect sizes represent the change in conversion rate when moving from control (−1) to variant (+1), 
averaged across all other factor combinations. A and B are independently significant. Tooltip alone shows no significant effect, but the Email × Tooltip interaction (BC) is confirmed significant at p=0.0098,
meaning tooltip delivers meaningful value when users have already received the
full email sequence. Shipping all A,B,C together maximises the combined lift.

![Power Sensitivity](outputs/effects_bar_chart.png)

![Power Sensitivity](outputs/main_effects_plot.png)

## Business Recommendation

### Decision

Before shipping, conversion lift alone is not enough. We weigh it against 
guardrail metrics to confirm the change is safe to release. Here are 4 
scenarios depending on what the guardrail data shows:

| Scenario | Conversion | Support Tickets | Unsubscribe Rate | Decision |
|----------|-----------|-----------------|-------------------|----------|
| **Best case** | +8.1pp | Flat | Flat | Ship immediately |
| **Acceptable** | +8.1pp | Slight increase (<10%) | Flat | Ship, monitor closely |
| **Caution** | +8.1pp | Flat | Increase (>5%) | Ship B only, hold C |
| **Do not ship** | +8.1pp | Large increase (>20%) | Large increase | Investigate root cause first |


### Revenue Impact

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Conversion Rate | 8.0% | 16.1% | +8.1pp |
| Paid Users / month | 800 | 1,610 | +810 |
| ARR | £240,000 | £483,000 | **+£243,000** |
 
*Projection includes confirmed effects: A (+2.55pp) + B (+2.95pp) + BC (+2.55pp)*


### Implementation Order (if we decide to ship features)

**Ship B + C together first**: the email sequence and tooltip are interdependent.
Tooltip delivers no value without the longer email sequence in place, so they
must be shipped as a pair.
 
**Sprint 1: 7-email sequence (B) + Tooltip (C)**
- Ship together — tooltip is only effective alongside the extended email sequence
- Monitor conversion for 2 weeks before Sprint 2

**Sprint 2: Blue CTA (A)**
- Independent effect, no dependency on B or C
- Safe to ship at any point; layering on top confirms additional +2.55pp

### What Not to Ship

**Tooltip in isolation.**
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

### Real-World Practice

This project uses a full factorial design to demonstrate understanding of 
interaction effects, a concept often missed in standard A/B testing. In 
practice, most companies run experiments through platforms like Optimizely, 
Statsig, or in-house tools that apply CUPED for variance reduction and 
sequential testing for early stopping, rather than fixed-sample factorial 
designs with manually coded ANOVA.

This project intentionally builds the analysis from first principles to 
show the underlying statistical reasoning.

### With More Time or Resources

**Block by user segment.** Conversion rates likely differ across plan type 
(Free vs Pro) and device. A blocked factorial design would isolate this 
variance from the error term, improving detection power — particularly 
valuable for the borderline ABC interaction (p=0.10).

**Extend the email factor beyond binary levels.** We tested 3 vs 7 emails 
only. A Response Surface Design could identify the optimal number between 
3 and 10, rather than assuming the endpoints are best.

**Run a confirmatory experiment.** Before full rollout, validate the BC 
interaction with a dedicated, larger-sample experiment isolating just B and 
C — removing A entirely to free up sample size and tighten the confidence 
interval on the interaction effect.

**Segment the analysis post-launch.** Even without blocking upfront, 
post-hoc segmentation by plan type and device would reveal whether the 
effects we found apply uniformly or are concentrated in a specific user group.

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
