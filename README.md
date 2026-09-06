# Learning Platform Growth Analytics

**Activation, Funnel, Experimentation, and Churn Analytics for an Online Skill-Certification Platform**

An end-to-end product analytics project modeling ~150K enrollments and 3.4M+ behavioral events for an EdTech platform, defining core funnel metrics, running a statistically rigorous A/B test, and identifying churn and payment-conversion drivers — all in SQL and Python.

---

## Business Problem

An online skill-certification platform lets users enroll in courses, complete lessons, and pay for certification once they finish. Leadership needs answers to five questions:

1. Which users activate (start genuinely learning) after enrolling?
2. Where in the enrollment → learning → completion → payment journey is the biggest drop-off?
3. Did the new onboarding experience actually improve outcomes?
4. Which users are at risk of churning before finishing their course?
5. What predicts whether a user pays for certification?

## Key Findings

| Finding | Detail |
|---|---|
| **Funnel bottleneck** | ~46% of all non-completing enrollments drop off at Lesson 1 — the single largest leak point in the entire funnel |
| **Overall conversion** | 12.8% of enrollments reach paid certification |
| **Experiment effect** | Treatment's effect is concentrated at the activation stage (+5.8pts, +7% relative); impact fades at later stages once accounting for who already got that far |
| **Churn driver** | Failure to activate (complete first lesson) is by far the strongest churn predictor (AUC 0.78) — more predictive than signup channel, age, or course count |
| **Payment drivers** | Course category and quiz performance are statistically significant (technical categories convert ~13pts higher than design), but jointly explain only modest predictive power (AUC 0.57) — most payment variation isn't captured by available data |
| **Cohort stability** | Activation rate is stable across signup cohorts over time (no significant drift, p=0.12) |

## Tech Stack

| Layer | Tool |
|---|---|
| Data generation | Python (synthetic multi-table dataset, intentional realistic messiness) |
| SQL modeling | DuckDB (staging views + analytical marts) |
| Analysis | pandas, statsmodels (z-tests, logistic regression) |
| Dashboard | Streamlit |

## Architecture

```
Synthetic Data (CSV: users, enrollments, lesson_events, payments)
    ↓  staging (clean, dedupe, normalize timestamps)
DuckDB SQL Staging Tables (stg_*)
    ↓  marts (dense-grid funnel, experiment, churn, payment)
DuckDB SQL Mart Tables (mart_*)
    ↓  analysis.py (funnel, cohort, A/B test, churn, payment drivers)
Streamlit Dashboard
```

## Data Model

- **users** (100K) — signup info, channel, experiment group
- **enrollments** (149K) — one row per course enrollment, status
- **lesson_events** (3.4M) — per-lesson interaction events (started/completed/quiz)
- **payments** (~19K) — certification purchases, linked to completed enrollments

## Core Metrics

| Metric | Definition |
|---|---|
| Signup-to-enrollment rate | Users enrolling within 7 days of signup (calibrated against p95 of actual distribution) |
| Activation rate | First lesson *completed* (not just started) after enrollment |
| Lesson-level drop-off | Dense-grid funnel: every enrollment × every lesson in its course, tracking exact abandonment point |
| Experiment lift | Step-conditional and cumulative conversion comparison, control vs. treatment, at each funnel stage |
| Churn risk | Logistic regression on recency + activation status + engagement depth |
| Payment conversion | Course category, quiz pass rate, signup channel vs. paid outcome |

## Data Quality & Limitations

- Raw data included intentional messiness (invalid ages, duplicate enrollment IDs, mixed timestamp formats, whitespace-corrupted categorical values) — resolved in the staging layer with documented, deliberate rules (e.g., dedup by earliest record, timestamp format coalescing).
- An early version of the synthetic payment-generation logic produced an unrealistic ~90% completer-to-payment conversion rate; this was identified as a data-generation artifact and corrected to a more realistic 15–35% range with category-based variation.
- The enrollment→first-lesson-started gap showed near-zero variance (data-generation artifact), which is why the activation metric was redefined around lesson *completion* instead, which showed realistic spread.
- Payment-driver model has genuine but weak predictive power (AUC 0.57) — this is reported honestly rather than overstated, since statistical significance and practical predictive strength are different things.

## License

MIT — synthetic data and analysis are original work; project structure inspired by open-source analytics portfolio conventions.