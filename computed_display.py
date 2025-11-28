import streamlit as st
import json
import pandas as pd
import os
import altair as alt

def computed_data_widget(employee_id):
    st.markdown("### Computed Data")
    
    # Selection for H1, H2, or Combined
    view_option = st.radio("Select View", ["H1", "H2", "Combined"], horizontal=True)
    
    data = None
    
    try:
        if view_option in ["H1", "H2"]:
            # Find the latest report card file
            data_dir = os.path.join(os.path.dirname(__file__), '../../backend/output')
            report_files = [f for f in os.listdir(data_dir) if f.startswith('report_cards_all_') and f.endswith('.json')]
            
            if not report_files:
                st.warning("No report card data found.")
                return

            # Sort to get the latest file (assuming date format allows sorting)
            latest_file = sorted(report_files)[-1]
            file_path = os.path.join(data_dir, latest_file)
            
            with open(file_path, 'r') as f:
                all_data = json.load(f)
                # Find data for the selected employee
                emp_data = next((item for item in all_data if item["employee_id"] == employee_id), None)
                
                if emp_data and "periods" in emp_data:
                    # Filter for the selected period (e.g., "2025H1" if view_option is "H1")
                    # Assuming view_option is just "H1" or "H2", we might need to map it or check substring
                    target_suffix = view_option  # "H1" or "H2"
                    data = next((p for p in emp_data["periods"] if p["period_half"].endswith(target_suffix)), None)
                    if data:
                        # Inject ID and Name for context in CSV
                        data['employee_id'] = emp_data['employee_id']
                        data['name'] = emp_data['name']
        else:
            # Combined view logic (already implemented)
            file_path = os.path.join(os.path.dirname(__file__), '../../backend/output/features_combined.json')
            with open(file_path, 'r') as f:
                all_data = json.load(f)
                # features_combined.json is a list of objects, find the one matching employee_id
                data = next((item for item in all_data if item["employee_id"] == employee_id), None)
                
        if data:
            # Display Manager Comment (Only for H1/H2)
            if view_option in ["H1", "H2"]:
                manager_comments = data.get("manager_evaluations__manager_comment", [])
                if manager_comments:
                    # Assuming list of dicts, take the first one's comment
                    comment_text = manager_comments[0].get("comment", "No comment available.")
                    st.info(f"**Manager Comment:** {comment_text}")

            # Display Key KPIs
            st.subheader("Key Performance Indicators")
            kpi_cols = st.columns(3)
            kpi_cols[0].metric("Velocity", data.get("kpi__velocity"))
            kpi_cols[1].metric("SP Completion Ratio", f"{data.get('kpi__story_point_completion_ratio', 0):.0%}")
            kpi_cols[2].metric("Defect Escape Rate", f"{data.get('kpi__defect_escape_rate', 0):.0%}")
            
            # Calculate Average Expected Score for Combined View
            expected_score = data.get("kpi__expected_score")
            if view_option == "Combined":
                # Try to calculate average from report cards
                try:
                    data_dir = os.path.join(os.path.dirname(__file__), '../../backend/output')
                    report_files = [f for f in os.listdir(data_dir) if f.startswith('report_cards_all_') and f.endswith('.json')]
                    if report_files:
                        latest_file = sorted(report_files)[-1]
                        with open(os.path.join(data_dir, latest_file), 'r') as f:
                            rc_data = json.load(f)
                            emp_rc = next((item for item in rc_data if item["employee_id"] == employee_id), None)
                            if emp_rc and "periods" in emp_rc:
                                scores = [p.get("kpi__expected_score") for p in emp_rc["periods"] if p.get("kpi__expected_score") is not None]
                                if scores:
                                    expected_score = sum(scores) / len(scores)
                                    expected_score = round(expected_score, 2) # Round for display
                except Exception as e:
                    print(f"Error calculating average score: {e}")

            kpi_cols2 = st.columns(3)
            kpi_cols2[0].metric("RTO Compliance", f"{data.get('kpi__rto_compliance_rate', 0):.0%}")
            kpi_cols2[1].metric("Copilot Accept Ratio", f"{data.get('kpi__copilot_accept_ratio', 0):.0%}")
            kpi_cols2[2].metric("Expected Score", expected_score)

            st.divider()
            
            # Visualization Selector
            viz_option = st.selectbox(
                "Select Visual Insight",
                ["Defect Severity", "Workday Sentiment", "GitHub Activity", "Jira Performance", "RTO Compliance"],
                key=f"viz_{employee_id}"
            )
            
            if viz_option == "Defect Severity":
                source = pd.DataFrame({
                    'Severity': ['Critical', 'Major', 'Minor', 'Trivial'],
                    'Count': [
                        data.get("defects__severity_Critical", 0),
                        data.get("defects__severity_Major", 0),
                        data.get("defects__severity_Minor", 0),
                        data.get("defects__severity_Trivial", 0)
                    ]
                })
                chart = alt.Chart(source).mark_bar().encode(
                    x=alt.X('Severity', sort=['Critical', 'Major', 'Minor', 'Trivial']),
                    y='Count',
                    color=alt.value('#D71E28'),  # WF Red
                    tooltip=['Severity', 'Count']
                ).properties(height=300)
                st.altair_chart(chart, use_container_width=True)

            elif viz_option == "Workday Sentiment":
                source = pd.DataFrame({
                    'Sentiment': ['Positive', 'Neutral', 'Mixed', 'Constructive'],
                    'Count': [
                        data.get("workday_checkins__sentiment_positive", 0),
                        data.get("workday_checkins__sentiment_neutral", 0),
                        data.get("workday_checkins__sentiment_mixed", 0),
                        data.get("workday_checkins__sentiment_constructive", 0)
                    ]
                })
                chart = alt.Chart(source).mark_bar().encode(
                    x=alt.X('Sentiment', sort=None),
                    y='Count',
                    color=alt.Color('Sentiment', scale=alt.Scale(domain=['Positive', 'Neutral', 'Mixed', 'Constructive'], range=['#2e7d32', '#757575', '#f9a825', '#c62828'])),
                    tooltip=['Sentiment', 'Count']
                ).properties(height=300)
                st.altair_chart(chart, use_container_width=True)

            elif viz_option == "GitHub Activity":
                source = pd.DataFrame({
                    'Metric': ['Commits', 'PRs', 'Reviews'],
                    'Count': [
                        data.get("github_metrics__commits", 0),
                        data.get("github_metrics__pull_requests", 0),
                        data.get("github_metrics__reviews_done", 0)
                    ]
                })
                chart = alt.Chart(source).mark_bar().encode(
                    x='Metric',
                    y='Count',
                    color=alt.value('#FFC72C'), # WF Gold
                    tooltip=['Metric', 'Count']
                ).properties(height=300)
                st.altair_chart(chart, use_container_width=True)

            elif viz_option == "Jira Performance":
                source = pd.DataFrame({
                    'Metric': ['Points Committed', 'Points Completed', 'Bugs Fixed', 'Bugs Introduced'],
                    'Value': [
                        data.get("jira_metrics__story_points_committed", 0),
                        data.get("jira_metrics__story_points_completed", 0),
                        data.get("jira_metrics__bugs_fixed", 0),
                        data.get("jira_metrics__bugs_introduced", 0)
                    ]
                })
                chart = alt.Chart(source).mark_bar().encode(
                    y=alt.Y('Metric', sort=None),
                    x='Value',
                    color=alt.value('#003087'), # Dark Blue
                    tooltip=['Metric', 'Value']
                ).properties(height=300)
                st.altair_chart(chart, use_container_width=True)

            elif viz_option == "RTO Compliance":
                source = pd.DataFrame({
                    'Category': ['In Office', 'Remote/Other'],
                    'Days': [
                        data.get("rto__in_office_days", 0),
                        max(0, data.get("rto__required_days", 60) - data.get("rto__in_office_days", 0)) # Assuming 60 is total for simplicity or just showing split
                    ]
                })
                base = alt.Chart(source).encode(theta=alt.Theta("Days", stack=True))
                pie = base.mark_arc(outerRadius=120).encode(
                    color=alt.Color("Category", scale=alt.Scale(range=['#D71E28', '#E0E0E0'])),
                    order=alt.Order("Days", sort="descending"),
                    tooltip=["Category", "Days"]
                )
                text = base.mark_text(radius=140).encode(
                    text="Days",
                    order=alt.Order("Days", sort="descending"),
                    color=alt.value("black")  
                )
                st.altair_chart(pie + text, use_container_width=True)

            with st.expander("View Raw Data"):
                st.json(data)
            
            # Convert to DataFrame for download
            df = pd.DataFrame([data])
            # Ensure employee_id and name are first
            cols = ['employee_id', 'name'] + [c for c in df.columns if c not in ['employee_id', 'name']]
            df = df[cols]
            csv = df.to_csv(index=False).encode('utf-8')
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button(
                    label=f"Download {view_option} Data (CSV)",
                    data=csv,
                    file_name=f"{employee_id}_{view_option}_computed.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            # Bulk Download Logic
            with col_d2:
                try:
                    manager_id = st.session_state.get('manager_id')
                    employees_path = os.path.join(os.path.dirname(__file__), '../../backend/mockdata/employees.csv')
                    if os.path.exists(employees_path):
                        df_emps = pd.read_csv(employees_path)
                        df_emps = df_emps.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
                        my_emp_ids = df_emps[df_emps['manager_id'] == manager_id]['employee_id'].tolist()
                        
                        bulk_data = []
                        if view_option in ["H1", "H2"]:
                            # Re-use file_path from earlier (it's still valid in this scope? No, it's inside if/else)
                            # Need to reconstruct file path or store it. 
                            # Actually, file_path variable scope in python is function-level if assigned in if/else.
                            # So `file_path` should be available here.
                            if os.path.exists(file_path):
                                with open(file_path, 'r') as f:
                                    all_data_bulk = json.load(f)
                                    for item in all_data_bulk:
                                        if item["employee_id"] in my_emp_ids and "periods" in item:
                                            p_data = next((p for p in item["periods"] if p["period_half"].endswith(view_option)), None)
                                            if p_data:
                                                # Inject employee_id and name for context
                                                p_data_copy = p_data.copy()
                                                p_data_copy['employee_id'] = item['employee_id']
                                                p_data_copy['name'] = item['name']
                                                bulk_data.append(p_data_copy)
                        else:
                            # Combined
                            if os.path.exists(file_path):
                                with open(file_path, 'r') as f:
                                    all_data_bulk = json.load(f)
                                    bulk_data = [item for item in all_data_bulk if item["employee_id"] in my_emp_ids]
                        
                        if bulk_data:
                            df_bulk = pd.DataFrame(bulk_data)
                            # Ensure employee_id and name are first
                            cols = ['employee_id', 'name'] + [c for c in df_bulk.columns if c not in ['employee_id', 'name']]
                            df_bulk = df_bulk[cols]
                            csv_bulk = df_bulk.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label=f"Download All {view_option} Data (CSV)",
                                data=csv_bulk,
                                file_name=f"Manager_{manager_id}_All_{view_option}_computed.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                except Exception as e:
                    st.error(f"Error preparing bulk download: {e}")
        else:
            st.warning("No data found for this employee.")

    except Exception as e:
        st.error(f"Error loading data: {e}")
