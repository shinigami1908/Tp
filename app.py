import streamlit as st
import sys
import os
import time

# Add backend to sys.path to support user's relative imports in backend/main.py
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    import backend.main as backend_main
except ImportError:
    # Fallback if backend.main is not found (e.g. if user structure is different)
    print("Warning: Could not import backend.main")
    backend_main = None

from frontend.src.dashboard import dashboard_page
from frontend.src.login import login_page

# Set page configuration
st.set_page_config(
    page_title="Performance Review System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Wells Fargo Colors
WF_RED = "#D71E28"
WF_GOLD = "#FFC72C"

# Custom CSS for styling
st.markdown(f"""
    <style>
        .stApp {{
            background-color: #f5f5f5;
        }}
        .header {{
            background-color: {WF_RED};
            color: white;
            padding: 1rem;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 2rem;
        }}
        .footer {{
            background-color: {WF_RED};
            color: white;
            padding: 1rem;
            text-align: center;
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            font-size: 14px;
            z-index: 999;
        }}
        .box {{
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }}
        /* Enforce equal height for the data widget containers using Flexbox */
        [data-testid="stHorizontalBlock"] {{
            align-items: stretch;
        }}
        [data-testid="column"] {{
            display: flex;
            flex-direction: column;
        }}
        /* Target the inner block of the column to ensure it grows */
        [data-testid="column"] > div {{
            flex: 1;
            display: flex;
            flex-direction: column;
        }}
        /* Target the border container to ensure it takes full height */
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            flex: 1;
            display: flex;
            flex-direction: column;
            height: 100%;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"] > div {{
            flex: 1;
            display: flex;
            flex-direction: column;
        }}
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Main routing logic
def main():
    if st.session_state.get('run_backend_processing'):
        username = st.session_state.get('username', 'User')
        
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
            
            # Run Backend Process
            if backend_main:
                backend_main.process_login_background(username)
            else:
                time.sleep(2) # Fallback simulation
            
        # Clear loading screen and reset flag
        loading_placeholder.empty()
        st.session_state['run_backend_processing'] = False
        st.rerun()

    if not st.session_state['authenticated']:
        login_page()
    else:
        dashboard_page()

if __name__ == "__main__":
    main()
