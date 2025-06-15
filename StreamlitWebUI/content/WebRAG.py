import streamlit as st
from components.webrag import show_url_management, show_indexed_urls
from utils.helpers import check_authentication

def show():
    check_authentication()
    
    # Two-column layout
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        show_url_management()
    
    with col2:
        show_indexed_urls()