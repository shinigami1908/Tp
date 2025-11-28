import streamlit as st
import json
import pandas as pd
import os

def generated_data_widget(employee_id):
    st.markdown("### Generated Data")
    manager_id = st.session_state.get('manager_id')
    
    st.markdown("### Generated Insights")
    
    try:
        # Load manager insights dynamically
        data_dir = os.path.join(os.path.dirname(__file__), '../../backend/output')
        file_path = os.path.join(data_dir, f'manager_{manager_id}_insights.json')
        
        if not os.path.exists(file_path):
            st.info(f"Insights for Manager {manager_id} are being generated...")
            return

        with open(file_path, 'r') as f:
            all_data = json.load(f)
            # Find data for the selected employee
            data = next((item for item in all_data if item["employee_id"] == employee_id), None)
            
        if data:
            # Period Summaries
            if data.get('period_summaries'):
                latest_summary = data['period_summaries'][0] # Taking the first one for now
                st.markdown(f"**Overall Highlights ({latest_summary.get('period_half')}):** {latest_summary.get('overall_highlights')}")
                st.markdown(f"**Manager Comment Rewrite:** {latest_summary.get('manager_comment_rewrite')}")
            
            st.divider()
            
            # Bias & Future Performance
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Bias Assessment")
                bias = data.get('bias_assessment', {})
                st.write(f"**Manager Rating:** {bias.get('manager_rating')}")
                st.write(f"**Expected Rating:** {bias.get('expected_rating')}")
                st.write(f"**Comparison:** {bias.get('comparison')}")
            
            with col2:
                st.markdown("#### Future Performance")
                future = data.get('future_performance', {})
                st.write(f"**Predicted:** {future.get('predicted_rating')}")
                st.write(f"**Confidence:** {future.get('confidence')}")
                st.write(f"**Rationale:** {future.get('rationale')}")

            st.divider()

            # Risks & Recommendations
            st.markdown("#### Risk Signals")
            for signal in data.get('risk_signals', []):
                st.markdown(f"- ⚠️ {signal}")
            
            st.markdown("#### Development Recommendations")
            for rec in data.get('development_recommendations', []):
                st.markdown(f"- 💡 {rec}")
            
            # Convert to DataFrame for download
            # Use the full data dictionary as requested
            df = pd.DataFrame([data])
            csv = df.to_csv(index=False).encode('utf-8')
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button(
                    label="Download Insights (CSV)",
                    data=csv,
                    file_name=f"{employee_id}_insights.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col_d2:
                # Bulk Download for Insights (all_data is already manager specific)
                if all_data:
                    df_all = pd.DataFrame(all_data)
                    csv_all = df_all.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download All Insights (CSV)",
                        data=csv_all,
                        file_name=f"Manager_{manager_id}_All_Insights.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
        else:
            st.warning("No generated insights found for this employee.")
            
    except Exception as e:
        st.error(f"Error loading data: {e}")
