import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import backend.src.main as backend_main
import time
import streamlit as st
import pandas as pd
import os

def login_page():
    # Custom Header Styling & Hide Input Instructions
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
                z-index: 999999;
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
            /* Adjust main content padding to not be hidden behind fixed header */
            [data-testid="stAppViewContainer"] > .main > .block-container {
                padding-top: 80px; 
            }
            /* Hide "Press Enter to apply" instructions */
            [data-testid="InputInstructions"] {
                display: none;
            }
            /* Style input fields to be distinct and premium */
            .stTextInput input {
                background-color: #ffffff !important;
                border: 1px solid #d1d5db !important;
                border-radius: 6px !important;
                box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
                padding: 10px 12px !important;
            }
            .stTextInput input:focus {
                border-color: #D71E28 !important;
                box-shadow: 0 0 0 3px rgba(215, 30, 40, 0.2) !important;
                outline: none !important;
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
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container(border=True):
            st.subheader("Please Sign In")
            
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                
                submitted = st.form_submit_button("Login")
                if submitted:
                    if validate_login(username, password):
                        # Show Loading Screen
                        loading_placeholder = st.empty()
                        with loading_placeholder.container():
                            st.markdown("""
                                <style>
                                    .loading-overlay {{
                                        position: fixed;
                                        top: 0;
                                        left: 0;
                                        width: 100%;
                                        height: 100%;
                                        background: rgba(255, 255, 255, 0.98);
                                        z-index: 1000000;
                                        display: flex;
                                        flex-direction: column;
                                        justify-content: center;
                                        align-items: center;
                                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                                    }}
                                    .loader-ring {{
                                        display: inline-block;
                                        position: relative;
                                        width: 80px;
                                        height: 80px;
                                        margin-bottom: 20px;
                                    }}
                                    .loader-ring div {{
                                        box-sizing: border-box;
                                        display: block;
                                        position: absolute;
                                        width: 64px;
                                        height: 64px;
                                        margin: 8px;
                                        border: 8px solid #D71E28;
                                        border-radius: 50%;
                                        animation: loader-ring 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
                                        border-color: #D71E28 transparent transparent transparent;
                                    }}
                                    .loader-ring div:nth-child(1) {{ animation-delay: -0.45s; }}
                                    .loader-ring div:nth-child(2) {{ animation-delay: -0.3s; }}
                                    .loader-ring div:nth-child(3) {{ animation-delay: -0.15s; }}
                                    @keyframes loader-ring {{
                                        0% {{ transform: rotate(0deg); }}
                                        100% {{ transform: rotate(360deg); }}
                                    }}
                                    .loading-text {{
                                        font-size: 24px;
                                        color: #333;
                                        font-weight: bold;
                                        animation: pulse 1.5s infinite;
                                    }}
                                    .loading-subtext {{
                                        font-size: 16px;
                                        color: #666;
                                        margin-top: 10px;
                                    }}
                                    @keyframes pulse {{
                                        0% {{ opacity: 0.6; }}
                                        50% {{ opacity: 1; }}
                                        100% {{ opacity: 0.6; }}
                                    }}
                                </style>
                                <div class="loading-overlay">
                                    <div class="loader-ring"><div></div><div></div><div></div><div></div></div>
                                    <div class="loading-text">AUTHENTICATING MANAGER ID: {username}</div>
                                    <div class="loading-subtext">Initializing Dashboard Modules...</div>
                                </div>
                            """.format(username=username), unsafe_allow_html=True)
                        
                        # Run Backend Process (this will block for 10s)
                        backend_main.process_login_background(username)
                        
                        # Clear loading screen
                        loading_placeholder.empty()
                        
                        st.session_state['authenticated'] = True
                        st.rerun()
                    else:
                        st.error("Invalid Username or Password")

    st.markdown('<div class="footer">© 2023 Wells Fargo. All rights reserved.</div>', unsafe_allow_html=True)

def validate_login(username, password):
    try:
        # Path to credentials.csv in frontend/public
        credentials_path = os.path.join(os.path.dirname(__file__), '../public/credentials.csv')
        df = pd.read_csv(credentials_path)
        # Clean whitespace from string columns
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        
        user = df[(df['manager_id'] == username) & (df['password'] == password)]
        
        if not user.empty:
            st.session_state['manager_id'] = user.iloc[0]['manager_id']
            st.session_state['username'] = user.iloc[0]['manager_id']
            return True
        return False
    except Exception as e:
        st.error(f"Error reading credentials: {e}")
        return False
