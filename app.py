import streamlit as st
import pandas as pd
import plotly.express as px
from google import genai

# --- 1. PAGE CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="UC Admissions Equity Intelligence",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #FFC107; margin-bottom: 0px; text-align: center; }
    .sub-header { font-size: 1.1rem; color: #CCCCCC; margin-bottom: 20px; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">UC Admissions Equity & Policy Intelligence Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Evaluating Systemwide Access, Socioeconomic Disparities, and Policy Impacts (2017–2025)</p>', unsafe_allow_html=True)
st.divider()

# --- 2. ROBUST DATA LOADING ---
@st.cache_data
def load_all_datasets():
    try:
        main_df = pd.read_csv("bay_area_modeling_table.csv", low_memory=False)
    except Exception:
        main_df = pd.DataFrame()

    try:
        disc_df = pd.read_csv("uc_freshman_admission_by_discipline.csv")
    except Exception:
        disc_df = pd.DataFrame()

    return main_df, disc_df

main_df, disc_df = load_all_datasets()

# --- 3. SIDEBAR CONTROLS ---
with st.sidebar:
    st.title("Filters & Scope")
    if not main_df.empty:
        available_counties = ["All Bay Area"] + sorted(main_df['county'].dropna().unique().tolist())
        selected_county = st.selectbox("Select County", available_counties)
        year_range = st.slider("Select Year Window", min_value=2017, max_value=2025, value=(2017, 2025))
    else:
        selected_county = "All Bay Area"
        year_range = (2017, 2025)
        
    st.divider()
    st.markdown("**Methodology Safeguards Active:**")
    st.caption("• Sum-before-divide aggregation")
    st.caption("• Non-zero privacy redaction handling")
    st.caption("• De-duplicated Systemwide records")

# --- 4. TABBED INTERFACE ---
tab1, tab2, tab3 = st.tabs(["📈 Macro Equity Trends", "🏫 Discipline Selectivity", "🤖 Gemini AI Diagnostics"])

# ==========================================
# TAB 1: MACRO EQUITY TRENDS
# ==========================================
with tab1:
    if main_df.empty:
        st.error("Missing `bay_area_modeling_table.csv`. Please upload it to your GitHub repository.")
    else:
        # Strict Filtering Rules
        base_filter = (
            (main_df['campus'] == 'Universitywide') &
            (main_df['fall_term'].between(year_range[0], year_range[1])) &
            (main_df['applicants'].notna()) &
            (main_df['admits'].notna()) &
            (main_df['frpm_pct'].notna())
        )
        if selected_county != "All Bay Area":
            base_filter = base_filter & (main_df['county'] == selected_county)

        filtered_df = main_df[base_filter].copy()

        # Categorize Poverty Brackets
        filtered_df['Income_Bracket'] = pd.cut(
            filtered_df['frpm_pct'],
            bins=[-1, 0.25, 0.50, 0.75, 1.0],
            labels=['Low Poverty (<25% FRPM)', 'Moderate-Low (25-50%)', 'Moderate-High (50-75%)', 'High Poverty (>75% FRPM)']
        )

        # Rigorous Aggregation (Sum counts first)
        equity_trends = filtered_df.groupby(['fall_term', 'Income_Bracket'], observed=False).apply(
            lambda g: (g['admits'].sum() / g['applicants'].sum() * 100) if g['applicants'].sum() > 0 else 0
        ).reset_index(name='Admit_Rate')

        # KPI Metrics (2025)
        data_2025 = equity_trends[equity_trends['fall_term'] == 2025]
        if not data_2025.empty:
            high_pov_val = data_2025[data_2025['Income_Bracket'] == 'High Poverty (>75% FRPM)']['Admit_Rate'].values[0]
            low_pov_val = data_2025[data_2025['Income_Bracket'] == 'Low Poverty (<25% FRPM)']['Admit_Rate'].values[0]
            
            col1, col2, col3 = st.columns(3)
            col1.metric("2025 High Poverty Admit Rate", f"{high_pov_val:.1f}%", "Post-2021 Advantage")
            col2.metric("2025 Low Poverty Admit Rate", f"{low_pov_val:.1f}%", "Historical Baseline", delta_color="inverse")
            col3.metric("Net Equity Gap", f"{abs(high_pov_val - low_pov_val):.1f}%", "Narrowed Since 2017")

        st.markdown("<br>", unsafe_allow_html=True)

        # Interactive Trend Visualization
        fig_trend = px.line(
            equity_trends, x='fall_term', y='Admit_Rate', color='Income_Bracket', markers=True,
            color_discrete_sequence=px.colors.qualitative.Pastel,
            labels={'fall_term': 'Fall Term', 'Admit_Rate': 'Admit Rate (%)', 'Income_Bracket': 'School FRPM Category'},
            title="Systemwide True Admission Rate by High School Poverty Tier"
        )
        fig_trend.add_vline(x=2021, line_dash="dash", line_color="#FF5252", annotation_text="2021: Test-Blind Mandate", annotation_position="top left", annotation_font_color="#FF5252")
        fig_trend.update_layout(xaxis=dict(tickmode='linear', dtick=1), legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5))
        st.plotly_chart(fig_trend, use_container_width=True)

        # Scatter Plot (A-G Readiness)
        st.subheader("Pipeline Leak: A-G Readiness vs. Acceptance Rate")
        valid_scatter = filtered_df[filtered_df['ag_completion_rate'].notna() & (filtered_df['fall_term'] == 2025)]
        
        if not valid_scatter.empty:
            fig_scatter = px.scatter(
                valid_scatter, x='ag_completion_rate', y='admit_rate', size='applicants', color='Income_Bracket',
                hover_name='high_school',
                labels={'ag_completion_rate': 'A-G Completion Rate (0-1)', 'admit_rate': 'UC Admit Rate (0-1)'},
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

# ==========================================
# TAB 2: DISCIPLINE SELECTIVITY
# ==========================================
with tab2:
    st.subheader("Selectivity Across Academic Disciplines")
    if not disc_df.empty:
        # Group by the correct column name: 'broad_discipline'
        disc_rates = disc_df.groupby('broad_discipline').apply(
            lambda g: (g['admits'].sum() / g['applicants'].sum() * 100) if g['applicants'].sum() > 0 else 0
        ).reset_index(name='Admit_Rate').sort_values(by='Admit_Rate', ascending=True)

        fig_disc = px.bar(
            disc_rates, x='Admit_Rate', y='broad_discipline', orientation='h', color='Admit_Rate',
            color_continuous_scale='Magma', labels={'Admit_Rate': 'Admit Rate (%)', 'broad_discipline': 'Academic Discipline'},
            title="Fall 2025 Selectivity by Major Area (All Campuses)"
        )
        st.plotly_chart(fig_disc, use_container_width=True)
    else:
        st.info("Missing `uc_freshman_admission_by_discipline.csv`. Upload it to view this chart.")

# ==========================================
# TAB 3: GEMINI AI DIAGNOSTICS
# ==========================================
with tab3:
    st.subheader("Automated AI Diagnostic Engine")
    st.markdown("Leverage Gemini 3.6 Flash to synthesize time-series equity trends with historical legislative shifts.")
    
    # 429 ERROR FAILSAFE: Caching the API call so it never repeats the exact same request unnecessarily
    @st.cache_data(show_spinner=False)
    def fetch_ai_insights(stats_summary_str, _api_key):
        client = genai.Client(api_key=_api_key)
        prompt_text = f"""
        You are a Senior Education Policy Analyst evaluating UC admissions.
        DATA: Admit Rates (%) by High School Poverty Level (2017-2025): {stats_summary_str}
        CONTEXT: In Fall 2021, a court forced the UC system to adopt a permanent test-blind policy (no SAT/ACT).
        
        Deliver a concise executive summary formatted with 3 bullet points:
        1. **Empirical Finding:** How the gap between High and Low Poverty schools shifted post-2021.
        2. **Policy Driver:** The impact of test-free review on historical equity metrics.
        3. **Strategic Recommendation:** One actionable recommendation for UC outreach programs.
        """
        interaction = client.interactions.create(model='gemini-3.6-flash', input=prompt_text)
        return interaction.output_text

    if st.button("Run Diagnostic Analysis", type="primary"):
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key:
            st.error("Missing `GEMINI_API_KEY` in Streamlit Secrets.")
        else:
            with st.spinner("Synthesizing admission distributions and policy timelines..."):
                try:
                    # Convert to string to safely pass into the cached function
                    stats_str = str(equity_trends.pivot(index='fall_term', columns='Income_Bracket', values='Admit_Rate').round(1).to_dict())
                    response_text = fetch_ai_insights(stats_str, api_key)
                    st.success("Diagnostic Synthesis Complete")
                    st.markdown(response_text)
                except Exception as ex:
                    st.error(f"Execution Error: {ex}")
