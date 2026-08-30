import pandas as pd

def run_sprint():
    print("--- UC QUESTION SPRINT SOLVER ---")
    
    # Load primary dataset
    df = pd.read_csv("bay_area_modeling_table.csv", low_memory=False)
    discipline_df = pd.read_csv("uc_freshman_admission_by_discipline.csv")
    
    # Question Example 1: Highest overall admit rate by high school (2025)
    # Rule: Sum counts then divide
    df_25 = df[(df['fall_term'] == 2025) & (df['campus'] == 'Universitywide')]
    rates = df_25.groupby('high_school').apply(
        lambda g: g['admits'].sum() / g['applicants'].sum() if g['applicants'].sum() > 100 else 0
    )
    print(f"Highest Admit Rate HS (Min 100 apps): {rates.idxmax()} ({round(rates.max()*100, 2)}%)")
    
    # Question Example 2: Most competitive discipline (Fall 2025)
    disc_rates = discipline_df.groupby('Discipline').apply(
        lambda g: g['Admits'].sum() / g['Applicants'].sum()
    )
    print(f"Most Competitive Discipline (Fall 2025): {disc_rates.idxmin()} ({round(disc_rates.min()*100, 2)}%)")
    
    print("Sprint execution complete. Input answers into the Google Form.")

if __name__ == "__main__":
    run_sprint()
