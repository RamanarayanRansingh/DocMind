import streamlit as st
from components.query import show_query_interface, show_query_history
from utils.helpers import check_authentication

def show():
    check_authentication()
    # Two-column layout
    col1, col2 = st.columns([2, 1], gap="large")
    
    with col1:
        show_query_interface()
    
    with col2:
        show_query_history()