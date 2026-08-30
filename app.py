import streamlit as st
import pandas as pd
from google import genai

st.set_page_config(page_title="UC Admissions Equity Dashboard", layout="wide")
st.title("UC Admissions: Impact of School Income Levels (2017-2025)")
st.markdown("Analyzing Universitywide admission rates for Bay Area high schools based on Free/Reduced Price Meal (FRPM) percentages.")

@st.cache_data
def load_and_clean_data():
    # Load the primary modeling table
    df = pd.read_csv("bay_area_modeling_table.csv", low_memory=False)
    
    # RULE 1: Filter to 'Universitywide' to count unique students, not total applications
    # RULE 2: Filter to 2017-2025 where FRPM data is consistently available
    # RULE 3: Drop rows with missing applicants/admits (redacted data) instead of filling with 0
    clean_df = df[
        (df['campus'] == 'Universitywide') & 
        (df['fall_term'] >= 2017) & 
        (df['applicants'].notna()) & 
        (df['admits'].notna()) &
        (df['frpm_pct'].notna())
    ].copy()
    
    # Categorize schools by poverty level (FRPM %)
    clean_df['Income_Bracket'] = pd.cut(
        clean_df['frpm_pct'], 
        bins=[-1, 0.25, 0.50, 0.75, 1.0], 
        labels=['Low Poverty (<25% FRPM)', 'Moderate-Low (25-50%)', 'Moderate-High (50-75%)', 'High Poverty (>75% FRPM)']
    )
    return clean_df

df = load_and_clean_data()

# RULE 4: Sum the counts first, then divide. Never average the rates directly.
aggregated_data = df.groupby(['fall_term', 'Income_Bracket']).apply(
    lambda g: g['admits'].sum() / g['applicants'].sum() if g['applicants'].sum() > 0 else None
).reset_index(name='Admit_Rate')

# Convert to percentage for better readability
aggregated_data['Admit_Rate'] = aggregated_data['Admit_Rate'] * 100

st.subheader("System-Wide Admit Rates by High School Poverty Level")
st.line_chart(
    data=aggregated_data, 
    x='fall_term', 
    y='Admit_Rate', 
    color='Income_Bracket'
)

st.markdown("---")
st.subheader("Automated AI Diagnostics (Powered by Gemini)")

if st.button("Generate Trend Analysis"):
    try:
        # Secure the Best Use of Gemini Award
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        
        # Format the data cleanly for the prompt
        trend_summary = aggregated_data.pivot(index='fall_term', columns='Income_Bracket', values='Admit_Rate').to_dict()
        
        prompt = f"""
        You are an expert data analyst evaluating UC admissions data. 
        Here are the system-wide admit rates (percentages) from 2017-2025, grouped by the high school's Free/Reduced Price Meal (FRPM) bracket:
        {trend_summary}
        
        Provide a concise, 4-sentence analysis. Specifically account for the fact that Fall 2021 changed the rules when a court order stopped UC from looking at SAT/ACT scores. 
        Focus on how the gap between High Poverty and Low Poverty schools shifted after this 2021 policy change.
        """
        
        # UPDATED: Using the new Interactions API and 3.6-flash model
        interaction = client.interactions.create(
            model='gemini-3.6-flash',
            input=prompt
        )
        
        # UPDATED: Using interaction.output_text
        st.info(interaction.output_text)
        
    except Exception as e:
        st.error(f"Error connecting to Gemini: Make sure you added your API key to Streamlit secrets. Details: {e}")
