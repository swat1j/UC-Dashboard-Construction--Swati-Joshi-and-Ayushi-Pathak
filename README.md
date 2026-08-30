# UC Admissions Equity Intelligence Platform
**Challenge:** UC Admissions Data Challenge 2026
**Team:** Ayushi Pathak, Swati Joshi, Akshaj Karthikeyan

## I. Analytical Framework
*   **Time Window:** 2017 to 2025 (Captures pre- and post-test-blind policy shifts).
*   **Population:** Bay Area public high school applicants categorized by socioeconomic status via Free/Reduced Price Meal percentages (`frpm_pct`).
*   **Core Metric:** Systemwide True Admission Rate ($\sum \text{Admits} / \sum \text{Applicants}$).

## II. Methodological Rigor & Data Safeguards
1.  **De-Duplication of Applicant Pools:** We strictly filtered for `campus == "Universitywide"`. Summing individual campus records inflates applicant volume by ~2.6x due to multi-campus applications. This ensures we are measuring unique students.
2.  **Redaction Preservation:** Missing values in small cohorts represent state privacy redactions (<5 applicants). Dropping non-reported cells rather than applying `.fillna(0)` prevents artificial deflation of admit rates.
3.  **Weighted Aggregations:** High school cohorts vary drastically in scale. Our pipeline sums counts prior to division, preventing single small-cohort schools from skewing county-level rate averages.

## III. Best Use of Gemini Integration
We deployed the `google-genai` SDK using `gemini-3.6-flash` via the Interactions API as an automated diagnostic engine. By passing our Pandas pivot tables into the LLM context, it synthesizes empirical trends against the Fall 2021 test-blind legal injunction to instantly produce justifiable findings and institutional recommendations. The API calls are wrapped in an `@st.cache_data` decorator to ensure robust performance without exceeding rate limits.
