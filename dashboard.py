import streamlit as st
import pandas as pd
import os
from frontend.src.computed_display import computed_data_widget
from frontend.src.insights_display import generated_data_widget

def dashboard_page():
    manager_id = st.session_state.get('manager_id')
    username = st.session_state.get('username')
    
    # Header
    # Custom Header Styling
    st.markdown("""
        <style>
            .wf-header {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                background-color: #D71E28;
                padding: 10px 0;
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 999999; /* High z-index to stay on top */
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            }
            .wf-strip {
                position: fixed;
                top: 50px; /* Height of header approx */
                left: 0;
                width: 100%;
                background-color: #FFC72C;
                height: 5px;
                z-index: 999999;
            }
            /* Adjust main content padding */
            [data-testid="stAppViewContainer"] > .main > .block-container {
                padding-top: 80px; 
            }
            /* Align Title and Manager Info */
            .title-row {
                display: flex;
                align-items: center;
                margin-bottom: 20px;
            }
            h1.dashboard-title {
                margin: 0;
                padding: 0;
                font-size: 2.5rem;
                font-weight: 700;
                color: #333;
            }
            .manager-info-text {
                text-align: right;
                line-height: 1.2;
                margin-right: 10px;
            }
            /* Force vertical alignment in columns */
            [data-testid="column"] {
                align-self: center;
            }
        </style>
    """, unsafe_allow_html=True)

    # Fixed Header Elements
    st.markdown("""
        <div class="wf-header">
            <img src="https://www17.wellsfargomedia.com/assets/images/rwd/wf_logo_220x23.png" alt="Wells Fargo Logo" style="height: 30px; filter: brightness(0) invert(1);">
        </div>
        <div class="wf-strip"></div>
    """, unsafe_allow_html=True)

    # Main Title and Manager Info
    # Using columns to layout the title and the manager box
    col_title, col_manager = st.columns([3, 1])
    
    with col_title:
        st.markdown('<h1 class="dashboard-title">Performance Review Dashboard</h1>', unsafe_allow_html=True)
        
    with col_manager:
        # Create a flex container for alignment
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(
                f"<div class='manager-info-text'>"
                f"<b>{username}</b><br>"
                f"<span style='font-size: 0.8em; color: #666;'>ID: {manager_id}</span>"
                f"</div>", 
                unsafe_allow_html=True
            )
        with c2:
            if st.button("Logout", use_container_width=True):
                st.session_state['authenticated'] = False
                st.rerun()

    try:
        # Load Employees
        # Path to employees.csv in backend/mockdata
        employees_path = os.path.join(os.path.dirname(__file__), '../../backend/mockdata/employees.csv')
        df_employees = pd.read_csv(employees_path)
        
        # Clean whitespace from string columns
        df_employees = df_employees.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        
        # Filter by Manager ID
        my_employees = df_employees[df_employees['manager_id'] == manager_id]
        
        if my_employees.empty:
            st.warning("No employees found for this manager.")
            return

        # Employee Selector
        employee_options = my_employees.apply(lambda x: f"{x['name']} ({x['employee_id']})", axis=1).tolist()
        selected_option = st.selectbox("Select Employee", employee_options)
        
        if selected_option:
            selected_emp_id = selected_option.split('(')[-1].strip(' )')
            # st.write(f"Debug: Manager ID: {manager_id}, Selected Employee ID: '{selected_emp_id}'")
            selected_emp_data = my_employees[my_employees['employee_id'] == selected_emp_id].iloc[0]
            
            # Employee Details
            with st.container(border=True):
                st.markdown("### Employee Details")
                col_d1, col_d2, col_d3, col_d4 = st.columns(4)
                col_d1.metric("Name", selected_emp_data['name'])
                col_d2.metric("Role", selected_emp_data['role'])
                col_d3.metric("Org", selected_emp_data['org'])
                col_d4.metric("Employee ID", selected_emp_data['employee_id'])
            
            # Data Widgets
            col_left, col_right = st.columns(2)
            
            with col_left:
                with st.container(border=True):
                    computed_data_widget(selected_emp_id)
                
            with col_right:
                with st.container(border=True):
                    generated_data_widget(selected_emp_id)

    except Exception as e:
        st.error(f"Error loading dashboard: {e}")

    # Footer
    st.markdown('<div class="footer">© 2023 Wells Fargo. All rights reserved.</div>', unsafe_allow_html=True)
