import streamlit as st

def check_authentication():
    if not st.session_state.get("authenticated"):
        st.error("You need to login to access this page.")
        st.stop()
        
def initialize_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.update({
            "authenticated": False,
            "access_token": None,
            "user_id": None,
            "email": None,
            "show_registration": False
        })

def apply_query_page_styles():
    st.markdown("""
    <style>
        .stMarkdown h3 {
            color: #2E86C1;
            margin-top: 20px;
        }
        .stMarkdown code {
            background-color: #f0f2f6;
            padding: 2px 5px;
            border-radius: 3px;
        }
        .stExpander {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 10px;
            margin: 10px 0;
        }
    </style>
    """, unsafe_allow_html=True)

def apply_home_page_styles():
    st.markdown("""
    <style>
        /* Introduction section */
        .stMarkdown h3 {
            color: #2E86C1;
            margin-top: 20px;
        }
        .stMarkdown ul {
            padding-left: 20px;
        }
        .stMarkdown li {
            margin: 10px 0;
        }
        
        /* Button styling */
        .stButton button {
            width: 100%;
            padding: 10px;
            border-radius: 5px;
            font-size: 16px;
            background-color: #2E86C1;
            color: white;
            border: none;
        }
        .stButton button:hover {
            background-color: #1A5276;
        }
        
        /* Expander styling */
        .stExpander {
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 10px;
            margin: 10px 0;
        }
    </style>
    """, unsafe_allow_html=True)