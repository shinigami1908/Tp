import streamlit as st
import pandas as pd
import json
import os
import altair as alt

def team_data_widget(manager_id):
    st.markdown("### Team Overview")
    
    try:
        # Load Employees
        employees_path = os.path.join(os.path.dirname(__file__), '../../backend/mockdata/employees.csv')
        if not os.path.exists(employees_path):
            st.error("Employees data not found.")
            return
            
        df_employees = pd.read_csv(employees_path)
        df_employees = df_employees.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        my_employees = df_employees[df_employees['manager_id'] == manager_id]
        
        if my_employees.empty:
            st.warning("No employees found for this manager.")
            return
            
        my_emp_ids = my_employees['employee_id'].tolist()
        
        # Load Combined Features for Metrics
        features_path = os.path.join(os.path.dirname(__file__), '../../backend/output/features_combined.json')
        if not os.path.exists(features_path):
            st.error("Features data not found.")
            return
            
        with open(features_path, 'r') as f:
            all_features = json.load(f)
            
        # Filter for my team
        team_data = [item for item in all_features if item['employee_id'] in my_emp_ids]
        
        if not team_data:
            st.warning("No performance data found for your team.")
            return
            
        # Convert to DataFrame for easier analysis
        df_team = pd.DataFrame(team_data)

        # Recalculate KPIs for consistency with raw data
        if 'rto__in_office_days' in df_team.columns and 'rto__required_days' in df_team.columns:
            df_team['kpi__rto_compliance_rate'] = df_team['rto__in_office_days'] / df_team['rto__required_days']
            
        if 'github_metrics__copilot_suggestions_accepted' in df_team.columns and 'github_metrics__copilot_suggestions_total' in df_team.columns:
             df_team['kpi__copilot_accept_ratio'] = df_team['github_metrics__copilot_suggestions_accepted'] / df_team['github_metrics__copilot_suggestions_total']

        # Drop name/role from df_team if present to avoid merge conflicts (suffixes)
        cols_to_drop = [c for c in ['name', 'role'] if c in df_team.columns]
        if cols_to_drop:
            df_team = df_team.drop(columns=cols_to_drop)
        
        # --- Summary Metrics ---
        st.subheader("Team Aggregates")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        avg_velocity = df_team['kpi__velocity'].mean()
        avg_sp_completion = df_team['kpi__story_point_completion_ratio'].mean()
        avg_defect_escape = df_team['kpi__defect_escape_rate'].mean()
        avg_rto = df_team['kpi__rto_compliance_rate'].mean()
        avg_copilot = df_team['kpi__copilot_accept_ratio'].mean()
        
        col1.metric("Avg Velocity", f"{avg_velocity:.1f}")
        col2.metric("Avg SP Completion", f"{avg_sp_completion:.0%}")
        col3.metric("Avg Defect Rate", f"{avg_defect_escape:.0%}")
        col4.metric("Avg RTO Compliance", f"{avg_rto:.0%}")
        col5.metric("Avg Copilot Ratio", f"{avg_copilot:.0%}")
        
        st.divider()
        
        # --- Team Table ---
        st.subheader("Team Performance Table")
        
        # Merge with employee details (Name, Role)
        df_display = df_team.merge(my_employees[['employee_id', 'name', 'role']], on='employee_id', how='left')
        
        # Select and Rename Columns
        cols_to_show = {
            'name': 'Name',
            'role': 'Role',
            'kpi__velocity': 'Velocity',
            'kpi__story_point_completion_ratio': 'SP Completion',
            'kpi__defect_escape_rate': 'Defect Rate',
            'kpi__rto_compliance_rate': 'RTO %',
            'kpi__copilot_accept_ratio': 'Copilot %',
            'kpi__expected_score': 'Expected Score'
        }
        
        df_table = df_display[cols_to_show.keys()].rename(columns=cols_to_show)
        
        # Convert ratios to percentages for display
        cols_to_pct = ['SP Completion', 'Defect Rate', 'RTO %', 'Copilot %']
        for col in cols_to_pct:
            if col in df_table.columns:
                df_table[col] = df_table[col] * 100
        
        # Format percentages for display (Streamlit dataframe handles this well if configured, but let's keep raw for sorting or format strings)
        # Using st.dataframe with column configuration is better
        st.dataframe(
            df_table,
            use_container_width=True,
            column_config={
                "SP Completion": st.column_config.NumberColumn(format="%.0f%%"),
                "Defect Rate": st.column_config.NumberColumn(format="%.1f%%"),
                "RTO %": st.column_config.NumberColumn(format="%.0f%%"),
                "Copilot %": st.column_config.NumberColumn(format="%.0f%%"),
                "Expected Score": st.column_config.NumberColumn(),
            },
            hide_index=True
        )
        
        st.divider()
        
        # --- Comparative Charts ---
        st.subheader("Comparative Insights")
        
        c_col1, c_col2 = st.columns(2)
        
        with c_col1:
            st.markdown("**Copilot Accept Ratio**")
            chart_copilot = alt.Chart(df_display).mark_bar().encode(
                x=alt.X('name', sort='-y', title=None),
                y=alt.Y('kpi__copilot_accept_ratio', axis=alt.Axis(format='%'), title='Accept Ratio'),
                color=alt.value('#D71E28'),
                tooltip=['name', alt.Tooltip('kpi__copilot_accept_ratio', format='.1%')]
            ).properties(height=300)
            st.altair_chart(chart_copilot, use_container_width=True)
            
            st.markdown("**Average Score (Expected)**")
            chart_score = alt.Chart(df_display).mark_bar().encode(
                x=alt.X('name', sort='-y', title=None),
                y=alt.Y('kpi__expected_score', title='Score'),
                color=alt.value('#FFC72C'),
                tooltip=['name', 'kpi__expected_score']
            ).properties(height=300)
            st.altair_chart(chart_score, use_container_width=True)

        with c_col2:
            st.markdown("**RTO Compliance**")
            chart_rto = alt.Chart(df_display).mark_bar().encode(
                x=alt.X('name', sort='-y', title=None),
                y=alt.Y('kpi__rto_compliance_rate', axis=alt.Axis(format='%'), title='Compliance %'),
                color=alt.value('#005E85'),
                tooltip=['name', alt.Tooltip('kpi__rto_compliance_rate', format='.1%')]
            ).properties(height=300)
            st.altair_chart(chart_rto, use_container_width=True)
            
            st.markdown("**Defect Escape Rate**")
            chart_defect = alt.Chart(df_display).mark_bar().encode(
                x=alt.X('name', sort='-y', title=None),
                y=alt.Y('kpi__defect_escape_rate', axis=alt.Axis(format='%'), title='Defect Rate'),
                color=alt.value('#5C6670'),
                tooltip=['name', alt.Tooltip('kpi__defect_escape_rate', format='.1%')]
            ).properties(height=300)
            st.altair_chart(chart_defect, use_container_width=True)

        st.divider()

        # --- Generative Insights ---
        st.subheader("Overall Team Insights (Generative AI)")
        
        insights_path = os.path.join(os.path.dirname(__file__), f'../../backend/output/manager_{manager_id}_overall_insights.json')
        
        if os.path.exists(insights_path):
            with open(insights_path, 'r') as f:
                insights = json.load(f)
            
            st.info(f"**Executive Summary:** {insights.get('executive_summary', 'N/A')}")
            
            i_col1, i_col2, i_col3 = st.columns(3)
            
            with i_col1:
                st.markdown("#### Key Strengths")
                for item in insights.get('key_strengths', []):
                    st.markdown(f"- {item}")
                    
            with i_col2:
                st.markdown("#### Areas for Improvement")
                for item in insights.get('areas_for_improvement', []):
                    st.markdown(f"- {item}")
                    
            with i_col3:
                st.markdown("#### Strategic Recommendations")
                for item in insights.get('strategic_recommendations', []):
                    st.markdown(f"- {item}")
            
            # Download Button
            json_str = json.dumps(insights, indent=2)
            st.download_button(
                label="Download Insights Report",
                data=json_str,
                file_name=f"manager_{manager_id}_insights.json",
                mime="application/json",
                use_container_width=True
            )
        else:
            st.info("No overall insights generated for this team yet.")

    except Exception as e:
        st.error(f"Error loading team data: {e}")
