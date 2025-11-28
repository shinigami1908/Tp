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
            # Period Summaries & Bias Assessment
            if data.get('period_summaries'):
                for summary in data['period_summaries']:
                    with st.container(border=True):
                        st.markdown(f"#### Period: {summary.get('period_half')}")
                        st.markdown(f"**Overall Highlights:** {summary.get('overall_highlights')}")
                        st.markdown(f"**Manager Comment Rewrite:** {summary.get('manager_comment_rewrite')}")
                        
                        # Bias Assessment (Per Period or Fallback)
                        bias = summary.get('bias_assessment')
                        if not bias:
                            # Fallback to top-level if not in period (for backward compatibility)
                            bias = data.get('bias_assessment', {})
                        
                        if bias:
                            st.markdown("**Bias Assessment:**")
                            b_col1, b_col2, b_col3 = st.columns(3)
                            b_col1.write(f"**Manager Rating:** {bias.get('manager_rating')}")
                            b_col2.write(f"**Expected Rating:** {bias.get('expected_rating')}")
                            b_col3.write(f"**Comparison:** {bias.get('comparison')}")
            
            st.divider()
            
            # Future Performance (Global)
            st.markdown("#### Future Performance")
            future = data.get('future_performance', {})
            col_f1, col_f2, col_f3 = st.columns(3)
            col_f1.write(f"**Predicted:** {future.get('predicted_rating')}")
            col_f2.write(f"**Confidence:** {future.get('confidence')}")
            col_f3.write(f"**Rationale:** {future.get('rationale')}")

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
