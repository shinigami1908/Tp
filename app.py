import streamlit as st

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
        .stButton>button {{
            background-color: {WF_RED};
            color: white;
            border-radius: 5px;
            border: none;
        }}
        .stButton>button:hover {{
            background-color: #b31921;
            color: white;
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
    if not st.session_state['authenticated']:
        login_page()
    else:
        dashboard_page()

if __name__ == "__main__":
    main()
