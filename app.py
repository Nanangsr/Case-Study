"""
app.py - Main Streamlit Application (Fixed & Clean)
"""
import streamlit as st
import pandas as pd
import time
import re
import logging

from config import Config
from src import database, ai_generator, visualizations

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='app.log', filemode='a')

# Page config
st.set_page_config(
    page_title=Config.APP_TITLE,
    page_icon=Config.PAGE_ICON,
    layout="wide"
)

# Initialize session state
if 'results_df' not in st.session_state:
    st.session_state.results_df = pd.DataFrame()
if 'ai_profile' not in st.session_state:
    st.session_state.ai_profile = {}
if 'selected_benchmark_ids' not in st.session_state:
    st.session_state.selected_benchmark_ids = []
if 'process_complete' not in st.session_state:
    st.session_state.process_complete = False
if 'role_name_final' not in st.session_state:
    st.session_state.role_name_final = ""
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

# Load data
@st.cache_data(ttl=Config.CACHE_TTL)
def load_initial_data():
    return database.get_employee_list(), database.get_role_list()

employee_df, role_list = load_initial_data()

if employee_df.empty:
    st.error("Failed to load employee data. Check Supabase connection.")
    logging.error("Failed to load employee data")
    st.stop()

# Title
st.title(f"{Config.PAGE_ICON} {Config.APP_TITLE}")
st.caption("Identify internal talent based on benchmark profiles")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    
    # Role selection
    role_options = [""] + sorted(role_list) + ["[New Role]"]
    role_selected = st.selectbox(
        "Role / Position",
        options=role_options,
        key="role_select"
    )
    
    # Show manual input immediately when [New Role] is selected
    if role_selected == "[New Role]":
        role_manual = st.text_input("Enter new role name:", key="role_manual")
        role_name = role_manual
    else:
        role_name = role_selected
    
    job_level = st.selectbox("Job Level", ["I", "II", "III", "IV", "V", "VI"], index=3)
    role_purpose = st.text_area("Role Purpose", placeholder="Describe main purpose...", height=100)
    
    benchmark_options = employee_df['label'].tolist()
    selected_benchmark_labels = st.multiselect(
        "Select Benchmark Employees",
        options=benchmark_options,
        help="Choose 3-5 top performers"
    )
    
    submitted = st.button("Generate Profile & Match", type="primary", use_container_width=True)

# Process on submit
if submitted:
    logging.info("Process submitted started")
    
    # Input Validation
    if not role_name or role_name == "[New Role]":
        st.warning("Please enter a valid role name.")
        logging.warning("Invalid role name")
    elif len(selected_benchmark_labels) < Config.MIN_BENCHMARKS:
        st.warning(f"Please select at least {Config.MIN_BENCHMARKS} benchmark employees.")
        logging.warning("Insufficient benchmarks")
    elif len(selected_benchmark_labels) < Config.RECOMMENDED_BENCHMARKS:
        st.warning(f"Recommended to select at least {Config.RECOMMENDED_BENCHMARKS} benchmarks for accuracy.")
    elif not role_purpose.strip():
        st.warning("Please enter role purpose.")
        logging.warning("Empty role purpose")
    else:
        try:  # Error Boundary untuk seluruh proses
            st.session_state.role_name_final = role_name
            st.session_state.process_complete = False
            st.session_state.messages = []
            
            selected_benchmark_ids = employee_df[employee_df['label'].isin(selected_benchmark_labels)]['employee_id'].tolist()
            st.session_state.selected_benchmark_ids = selected_benchmark_ids
            
            progress_bar = st.progress(0, text="Starting process...")
            
            # Calculate matches
            with st.spinner("Calculating match scores..."):
                progress_bar.progress(30, text="Loading data & calculating...")
                st.session_state.results_df = database.run_matching_query(selected_benchmark_ids)
            
            if st.session_state.results_df.empty:
                raise ValueError("Match calculation returned empty results")
            
            # Data Quality Indicators: Check benchmark completeness
            benchmark_df = st.session_state.results_df[st.session_state.results_df['employee_id'].isin(selected_benchmark_ids)]
            avg_completeness = benchmark_df['data_completeness'].mean()
            if avg_completeness < 80:
                st.warning(f"Benchmark data quality low: Average completeness {avg_completeness:.1f}%. Results may be inaccurate.")
                logging.warning(f"Low benchmark completeness: {avg_completeness:.1f}%")
            
            # Generate AI profile
            with st.spinner("Generating AI profile..."):
                progress_bar.progress(70, text="Contacting AI...")
                st.session_state.ai_profile = ai_generator.generate_job_profile(
                    role_name, role_purpose, job_level
                )
            
            progress_bar.progress(100, text="Complete!")
            time.sleep(0.5)
            progress_bar.empty()
            
            st.session_state.process_complete = True
            st.success("Profile and talent ranking generated successfully!")
            logging.info("Process completed successfully")
        
        except Exception as e:
            st.error(f"An error occurred: {str(e)}. Please check logs or try again.")
            logging.error(f"Process error: {str(e)}")
            progress_bar.empty()

# Display results
if st.session_state.process_complete:
    st.markdown("---")
    st.header("Results")
    
    tab_profile, tab_ranking, tab_dashboard, tab_compare, tab_chatbot = st.tabs([
        "AI Profile", "Ranking", "Dashboard", "Comparison", "Ask AI"
    ])
    
    # TAB 1: AI PROFILE
    with tab_profile:
        ai_profile = st.session_state.ai_profile
        
        if not ai_profile:
            st.info("AI profile not available.")
        elif "error" in ai_profile:
            st.error(f"AI generation failed: {ai_profile['error']}")
        else:
            st.subheader("Role Description")
            st.write(ai_profile.get('job_description', 'N/A'))
            
            st.subheader("Key Responsibilities")
            resp_list = ai_profile.get('responsibilities', [])
            if isinstance(resp_list, list):
                for item in resp_list:
                    st.markdown(f"- {item}")
            
            st.subheader("Minimum Qualifications")
            qual_list = ai_profile.get('qualifications', [])
            if isinstance(qual_list, list):
                for item in qual_list:
                    st.markdown(f"- {item}")
            
            st.subheader("Key Competencies")
            comp_list = ai_profile.get('key_competencies', [])
            if isinstance(comp_list, list):
                for item in comp_list:
                    st.markdown(f"- {item}")
    
    # TAB 2: RANKING
    with tab_ranking:
        results_df = st.session_state.results_df
        
        if results_df.empty:
            st.warning("No results available.")
        else:
            df_ranked = results_df.drop_duplicates(subset=['employee_id']).sort_values('final_match_rate', ascending=False)
            
            col1, col2 = st.columns(2)
            with col1:
                dir_options = ["All"] + sorted(df_ranked['directorate'].dropna().unique().tolist())
                selected_dir = st.selectbox("Filter Directorate:", dir_options)
            with col2:
                grade_options = ["All"] + sorted(df_ranked['grade'].dropna().unique().tolist())
                selected_grade = st.selectbox("Filter Grade:", grade_options)
            
            filtered_df = df_ranked.copy()
            if selected_dir != "All":
                filtered_df = filtered_df[filtered_df['directorate'] == selected_dir]
            if selected_grade != "All":
                filtered_df = filtered_df[filtered_df['grade'] == selected_grade]
            
            filtered_df['exceeds'] = filtered_df['final_match_rate'].apply(lambda x: '⭐' if pd.notna(x) and x > 100 else '')
            filtered_df['quality'] = filtered_df['data_completeness'].apply(lambda x: '✅' if x > 70 else '⚠️')
            
            max_score = max(100, filtered_df['final_match_rate'].max() if not filtered_df.empty else 100)
            
            st.caption("⭐ = Score exceeds benchmark (>100%) | ✅ = Good data (>70%), ⚠️ = Low")
            
            st.dataframe(
                filtered_df[['fullname', 'role', 'grade', 'directorate', 'quality', 'data_completeness', 'final_match_rate', 'exceeds']],
                column_config={
                    "fullname": "Name",
                    "role": "Position",
                    "grade": "Grade",
                    "directorate": "Directorate",
                    "quality": st.column_config.TextColumn("Quality", help="✅ = Good data (>70%), ⚠️ = Low"),
                    "data_completeness": st.column_config.ProgressColumn(
                        "Data Completeness (%)",
                        format="%.1f%%",
                        min_value=0,
                        max_value=100
                    ),
                    "final_match_rate": st.column_config.ProgressColumn(
                        "Match Rate (%)",
                        format="%.2f%%",
                        min_value=0,
                        max_value=max_score
                    ),
                    "exceeds": st.column_config.TextColumn(" ", width="small")
                },
                height=400,
                use_container_width=True,
                hide_index=True
            )
            
            @st.cache_data
            def convert_to_csv(df):
                return df.to_csv(index=False).encode('utf-8')
            
            safe_role_name = st.session_state.role_name_final.replace(' ', '_')
            csv_data = convert_to_csv(filtered_df[['employee_id', 'fullname', 'role', 'grade', 'directorate', 'data_completeness', 'final_match_rate']])
            
            st.download_button(
                label="Download Results (CSV)",
                data=csv_data,
                file_name=f"talent_match_{safe_role_name}.csv",
                mime='text/csv'
            )
    
    # TAB 3: DASHBOARD
    with tab_dashboard:
        results_df = st.session_state.results_df
        
        if results_df.empty:
            st.warning("No data for dashboard.")
        else:
            st.plotly_chart(visualizations.plot_match_distribution(results_df), use_container_width=True)
            st.plotly_chart(visualizations.plot_top_candidates(results_df, Config.DEFAULT_TOP_N), use_container_width=True)
            
            st.markdown("---")
            st.subheader("Benchmark Profile (Median TGV Scores)")
            
            benchmark_profile = results_df[results_df['employee_id'].isin(st.session_state.selected_benchmark_ids)]\
                .groupby('tgv_name')['tgv_match_rate'].median().reset_index()
            
            if not benchmark_profile.empty:
                import plotly.graph_objects as go
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=benchmark_profile['tgv_match_rate'],
                    theta=benchmark_profile['tgv_name'],
                    fill='toself',
                    name='Benchmark Median'
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 120])),
                    title='Benchmark TGV Profile'
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # TAB 4: COMPARISON
    with tab_compare:
        results_df = st.session_state.results_df
        
        if results_df.empty:
            st.warning("No candidates to compare.")
        else:
            candidate_list = results_df.drop_duplicates(subset=['employee_id']).sort_values('final_match_rate', ascending=False)
            
            if not candidate_list.empty:
                candidate_list['label'] = candidate_list['fullname'] + " (" + candidate_list['employee_id'] + ")"
                
                selected_candidate_label = st.selectbox(
                    "Select candidate to compare:",
                    options=[""] + candidate_list['label'].tolist()
                )
                
                if selected_candidate_label:
                    selected_candidate_id = candidate_list[candidate_list['label'] == selected_candidate_label]['employee_id'].iloc[0]
                    selected_candidate_name = candidate_list[candidate_list['label'] == selected_candidate_label]['fullname'].iloc[0]
                    
                    st.markdown(f"#### Comparing: **{selected_candidate_name}**")
                    
                    fig = visualizations.plot_profile_comparison(
                        results_df,
                        selected_candidate_id,
                        st.session_state.selected_benchmark_ids
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    with st.expander(f"View TV details for {selected_candidate_name}"):
                        detail_cols = ['tgv_name', 'tv_name', 'Meaning', 'Behavior Example', 'baseline_score', 'user_score', 'tv_match_rate', 'Note']
                        detail_cols_exist = [col for col in detail_cols if col in results_df.columns]
                        detail_df = results_df[results_df['employee_id'] == selected_candidate_id][detail_cols_exist]\
                            .sort_values(by=['tgv_name', 'tv_name'])
                        st.dataframe(detail_df, use_container_width=True, height=500, hide_index=True)
    
    # TAB 5: CHATBOT
    with tab_chatbot:
        st.header("Ask AI About Results")
        
        show_thinking = st.checkbox("Show AI thinking process?", value=False)
        
        results_df = st.session_state.results_df
        
        if not results_df.empty:
            # Display chat history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    if message["role"] == "assistant" and "thinking" in message and message["thinking"] and show_thinking:
                        with st.expander("AI Thinking Process", expanded=False):
                            st.markdown(message["thinking"])
                    st.markdown(message["content"])
            
            # Chat input
            if user_question := st.chat_input("Example: 'Who is strongest in Leadership?', 'What are Joko's gaps?'"):
                st.session_state.messages.append({"role": "user", "content": user_question})
                
                with st.chat_message("user"):
                    st.markdown(user_question)
                
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    message_placeholder.markdown("Thinking...")
                    
                    try:
                        # Prepare context
                        top_5 = results_df.drop_duplicates(subset=['employee_id'])\
                            .sort_values('final_match_rate', ascending=False).head(5)
                        
                        context_summary = f"Top 5 Candidates Summary for role '{st.session_state.role_name_final}':\n"
                        
                        for _, row in top_5.iterrows():
                            emp_id = row['employee_id']
                            name = row['fullname']
                            final_score = row['final_match_rate']
                            completeness = row['data_completeness']
                            
                            context_summary += f"\n- {name} ({emp_id}), Final Score: {final_score:.2f}%, Data Completeness: {completeness:.1f}%\n"
                            
                            # TGV summary for this employee
                            emp_data = results_df[results_df['employee_id'] == emp_id]\
                                .drop_duplicates(subset=['tgv_name'])[['tgv_name', 'tgv_match_rate']]\
                                .sort_values('tgv_match_rate', ascending=False)
                            
                            context_summary += "  Top TGV Scores:\n"
                            for _, tgv_row in emp_data.head(3).iterrows():
                                context_summary += f"    - {tgv_row['tgv_name']}: {tgv_row['tgv_match_rate']:.1f}%\n"
                        
                        # Construct prompt
                        chatbot_prompt = f"""You are an analytical HR assistant. 

                        Context: Talent matching results for role '{st.session_state.role_name_final}'. 

                        {context_summary}

                        Note: Scores >100% indicate performance exceeding benchmark average.

                        User Question: "{user_question}"

                        Instructions:
                        1. First, explain your reasoning in <think></think> tags
                        2. Then provide a clear, concise answer based on the data above
                        3. If the data doesn't support an answer, say so

                        Format: <think>YOUR REASONING</think> YOUR ANSWER"""

                        # Call AI
                        response = ai_generator.client.chat.completions.create(
                            messages=[{"role": "user", "content": chatbot_prompt}],
                            model=Config.GROQ_MODEL,
                            temperature=0.5
                        )
                        
                        ai_raw_answer = response.choices[0].message.content
                        
                        # Parse thinking and answer
                        thinking_part = ""
                        answer_part = ai_raw_answer
                        
                        match = re.search(r"<think>(.*?)</think>(.*)", ai_raw_answer, re.DOTALL | re.IGNORECASE)
                        if match:
                            thinking_part = match.group(1).strip()
                            answer_part = match.group(2).strip()
                        
                        # Display
                        if show_thinking and thinking_part:
                            with st.expander("AI Thinking Process", expanded=False):
                                st.markdown(thinking_part)
                        
                        message_placeholder.markdown(answer_part)
                        
                        # Store in history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer_part,
                            "thinking": thinking_part
                        })
                        
                    except Exception as e:
                        error_msg = f"Failed to get AI response: {str(e)}"
                        message_placeholder.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg,
                            "thinking": ""
                        })
        else:
            st.info("Chat will be available after generating results.")

# Footer
st.markdown("---")
st.caption(f"{Config.APP_TITLE} v2.0 - Clean & Optimized")