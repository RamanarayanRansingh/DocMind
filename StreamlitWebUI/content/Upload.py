import streamlit as st
from components.documents import show_document_upload, show_document_list
from utils.helpers import check_authentication

def show():
    check_authentication()
    # Two-column layout
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        show_document_upload()
    
    with col2:
        show_document_list()