# UC Admissions Equity Dashboard
**Team:** Ayushi, Swati, Akshaj

## Analytical Framework
*   **Time Window:** 2017 to 2025 (Aligning with stable `frpm_pct` and `ag_completion_rate` reporting data).
*   **Population:** Bay Area public high school applicants, segmented by school-level poverty (measured via the percentage of students on Free/Reduced Price Meals).
*   **Metric:** System-wide True Admission Rate (Unique Students Admitted / Unique Students Applied).

## Methodological Rigor & Data Integrity
To ensure complete accuracy and avoid the statistical pitfalls common in admissions modeling, our data pipeline strictly adheres to the following constraints:
1.  **De-Duplication:** We isolated data where `campus == "Universitywide"`. Summing the individual 9 campuses inflates the applicant pool by approximately 2.6x because a single student applying to multiple campuses is counted multiple times. By using the system-wide metric, our dashboard accurately reflects "admitted to at least one UC."
2.  **Handling Redactions:** The UC system hides data for cells with fewer than 5 applicants or 3 admits to protect privacy. Instead of using `.fillna(0)`—which mathematically invents students who do not exist and skews historical averages—our script drops nulls to maintain the true mathematical distribution of the available data.
3.  **Accurate Aggregation:** High schools vary wildly in cohort size. A school with 12 applicants cannot be weighted equally against a school with 400. Therefore, our pipeline aggregates the raw applicant and admit counts first, *then* divides them (`sum(admits) / sum(applicants)`) rather than inaccurately averaging pre-calculated rates.

## Best Use of Gemini Integration
We integrated the Gemini 2.5 Flash SDK to act as an automated policy diagnostic tool. The dashboard feeds strictly formatted, aggregated time-series data to the LLM, prompting it to analyze equity gaps specifically through the lens of the Fall 2021 test-blind policy shift. This transforms the dashboard from a static visualizer into an active analytical tool.
