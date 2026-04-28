# Model Card: CS Master's Program Recommender

## 1. Model Name

### CS Program Advisor 1.0

A rule-based program recommender that scores and ranks CS master's programs against an applicant profile, retrieves supporting facts from local program text files, and produces fully explainable recommendations — with no external APIs, no embeddings, and no paid services.

---

## 2. Intended Use

This system is designed for prospective CS master's students who need help comparing programs across competing constraints: budget, GRE willingness, delivery mode, visa requirements, ranking preference, specialization fit, and time to graduation.

It is intended for classroom exploration and portfolio demonstration, not for production admissions advising. The program data is curated for illustration and may not reflect current admission requirements or tuition figures.

**Who it is for:**

- Students building intuition about CS graduate program tradeoffs
- Applicants who want an explainable, auditable alternative to opaque ranking tools
- Developers learning how to build retrieval-augmented rule-based recommenders

**What it does not do:**

- It does not access live program websites or admissions portals
- It does not predict admission probability
- It does not account for financial aid, scholarships, or fee waivers
- It is not a substitute for speaking directly with program advisors

---

## 3. How the Model Works

The recommender uses a 9-factor weighted scoring function. Each program in the local dataset is scored independently against the applicant's profile, then ranked by total score.

**Scoring factors:**

| Factor | Max contribution | Direction |
| --- | --- | --- |
| Tuition fit | ±3.0 | +3.0 if within budget; penalty scales with how far over |
| GRE compatibility | +1.0 / −2.5 | −2.5 if GRE required but applicant is unwilling |
| Delivery mode | +2.0 | Exact match or "any" preference required |
| Visa support | +2.0 / −1.5 | Applied only when applicant needs visa support |
| Ranking tier | ±1.5 | +1.5 if program meets or exceeds preferred tier |
| Specialization overlap | up to +1.5 | +0.75 per matched specialization, capped at 1.5 |
| Application fee | +1.0 / −0.5 | Compared to applicant's stated maximum |
| Research/industry fit | +1.0 / +0.5 | Based on applicant focus and program ranking tier |
| Duration fit | +0.5 | Awarded if program completes within the applicant's target |

After scoring, programs are sorted by total score (descending). The top-k results are returned alongside a reasons string listing each factor's contribution and a retrieved snippet from the program's local text file.

**Retrieval:** For each recommended program, the system reads a local `.txt` file containing plain-text program notes and returns sentences that contain any of the applicant's preferred specialization keywords. If no keyword matches, the first 300 characters are returned as a summary.

There is no machine learning model, no fine-tuning, and no vector search. Every output is deterministic and fully traceable to the scoring rules.

---

## 4. Data Sources

**programs.csv** — 10 curated CS master's programs with structured fields:

| Program | Tier | Delivery | Tuition |
| --- | --- | --- | --- |
| Stanford University MSCS | 1 | in-person | $67,000 |
| Carnegie Mellon University MSCS | 1 | in-person | $58,000 |
| Carnegie Mellon University MCDS | 1 | in-person | $73,000 |
| Georgia Tech OMSCS | 2 | online | $7,000 |
| University of Illinois MCS | 2 | online | $22,000 |
| Columbia University MSCS | 2 | in-person | $65,000 |
| UC San Diego MSCS | 2 | in-person | $37,000 |
| UT Austin MSCS | 2 | in-person | $20,000 |
| Northeastern University MSCS | 3 | hybrid | $42,000 |
| Arizona State University MSCS | 4 | online | $15,000 |

**data/programs/*.txt** — 10 plain-text files, one per program, containing factual notes drawn from publicly available program descriptions. These are the source documents for local retrieval.

All data is stored locally. No external data is fetched at runtime.

**Limitations of the dataset:**

- 10 programs is a very small corpus; real applicants consider 20–50+ programs
- Tuition figures are approximations and do not account for in-state discounts, fellowships, or fee waivers
- Ranking tiers are manually assigned and reflect a general consensus, not a single authoritative source
- Specialization labels are simplified; real programs have more granular tracks
- The corpus skews toward well-known US programs and does not represent international schools or HBCUs

---

## 5. Limitations

**Coverage:** Only 10 programs are included. Missing programs cannot be recommended regardless of fit.

**Deterministic weights:** Factor weights are hand-tuned and reflect the developer's judgment about typical applicant priorities. Different populations (e.g., part-time students, career changers) may weight factors very differently.

**Hard GRE penalty:** The −2.5 GRE penalty is intentionally large. For applicants who are indifferent about GRE, this creates a strong artificial tilt toward GRE-optional programs even when the GRE-required program is otherwise a much better fit.

**No personalization over time:** The system has no memory. It does not improve with feedback or adapt to stated preferences beyond a single profile.

**No uncertainty quantification:** Scores are presented as precise numbers. The system does not communicate that two programs with scores 9.75 and 9.50 are effectively equivalent for most decision purposes.

---

## 6. Bias and Fairness

**Prestige bias in research/industry fit:** The research-focus bonus is proxied by ranking tier — top-2 tier programs earn +1.0 for research-focused applicants. This conflates ranking with research opportunity and disadvantages strong research programs at lower-ranked institutions.

**Budget sensitivity asymmetry:** The tuition penalty scales with the *ratio* of overage, meaning a program $5,000 over a $25,000 budget (20% over) is penalized more severely than a program $5,000 over a $70,000 budget (7% over). This is intentional but may disadvantage low-budget applicants seeking programs in a slightly higher cost tier.

**Delivery mode as a binary:** "hybrid" delivery does not receive partial credit for online-preferring applicants. An applicant who would accept hybrid but prefers online scores Northeastern (hybrid) lower than a fully online program of any tier. This may not reflect real preferences.

**Visa support proxy:** Visa support is a binary field. In practice, the quality of international student support varies substantially; a program with minimal F-1 support counts the same as one with dedicated advising staff.

**Corpus selection:** The 10 programs were manually selected and reflect programs commonly referenced in US CS graduate admissions discussions. Programs that are regionally strong, serve non-traditional students, or are less frequently discussed online are not represented.

---

## 7. Evaluation

**Automated tests (11/11 passed):**

Five behavioral invariants were verified:

- GRE-required programs rank below GRE-optional programs for a non-willing applicant, all else equal
- Over-budget programs score lower than affordable ones
- Programs with visa support score higher for applicants who need it
- Matching specializations increase scores
- Explanations are always non-empty and reference scoring factors

Three retrieval tests confirm that the local text retrieval returns non-empty results, matches keyword-containing sentences, and handles missing files gracefully.

**Manual spot checks (5 personas):**

Each persona was run and the top-3 results were reviewed for intuitive correctness:

| Persona | Expected top result | Actual top result | Match |
| --- | --- | --- | --- |
| Budget-Focused Domestic | GT OMSCS (cheapest online, no GRE) | GT OMSCS | Yes |
| International Applicant | Stanford (top-tier, visa support, ML+AI) | Stanford | Yes |
| Online-First Learner | GT OMSCS or UIUC (online, no GRE) | GT OMSCS | Yes |
| Research-Oriented Top-Tier | Stanford (tier 1, ML+AI+theory) | Stanford | Yes |
| Ranking-Focused Career Switcher | Stanford or CMU (tier 1, in-person) | Stanford | Yes |

All 5 top results matched expectation. No failures or surprising reversals were observed in the top-3 for any persona.

**Known failure mode:** Programs that differ by only one specialization match (e.g., ml vs ml+ai) produce ties in all other factors, and tie-breaking depends on dataset order. This was partially mitigated by the specialization overlap weighting but can still produce identical scores for programs that are meaningfully different.

---

## 8. Scope Boundaries

This system is appropriate for:

- Learning how content-based recommenders work
- Demonstrating retrieval-augmented explanation generation
- Comparing tradeoff handling across explicit constraint types

This system is not appropriate for:

- Making real admissions decisions without consulting official program sources
- Representing the full landscape of CS master's programs globally
- Replacing structured advising from academic or admissions counselors
