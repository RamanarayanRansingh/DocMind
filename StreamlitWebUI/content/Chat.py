import streamlit as st
from components.chat import chat_interface
from utils.helpers import check_authentication
from utils.api import get_user_documents
import pandas as pd

def show():
    check_authentication()
    
    # Check for documents
    try:
        response = get_user_documents(st.session_state.access_token)
        if response.status_code == 200:
            documents = response.json()
        else:
            documents = []
    except Exception as e:
        st.error(f"Error loading documents: {str(e)}")
        documents = []

    # No documents uploaded
    if not documents:
        st.markdown("## 📚 Welcome to Document Chat")
        st.info("You need to upload at least one document before starting a chat.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 Upload Document", use_container_width=True):
                # Explicitly set to the Upload page
                st.session_state.current_page = "Upload"
                st.rerun()
        
        with col2:
            if st.button("🏠 Back to Home", use_container_width=True):
                # Explicitly set to the Home page
                st.session_state.current_page = "Home"
                st.rerun()
        return

    # Document selection if none selected
    if "selected_document" not in st.session_state:
        st.markdown("## 📚 Select a Document to Chat With")
        
        # Display documents in a grid
        cols = st.columns(3)
        for idx, doc in enumerate(documents):
            with cols[idx % 3]:
                st.markdown(f"""
                <div style="border: 1px solid #e0e0e0; border-radius: 10px; padding: 15px; margin: 10px 0;">
                    <h4>{doc['file_name']}</h4>
                    <p>Type: {doc['file_type'].upper()}</p>
                    <p>Uploaded: {pd.to_datetime(doc['uploaded_at']).strftime("%Y-%m-%d")}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Use Streamlit button instead of JavaScript
                if st.button("Select", key=f"select_{doc['id']}"):
                    st.session_state.selected_document = doc
                    st.rerun()
        
        # Option to upload more documents or go back
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Upload More Documents", use_container_width=True):
                st.session_state.current_page = "Upload"
                st.rerun()
        
        with col2:
            if st.button("🏠 Back to Home", use_container_width=True):
                st.session_state.current_page = "Home"
                st.rerun()
        return

    # Show chat interface if document is selected
    document = st.session_state.selected_document
    chat_interface(
        document_id=document["id"],
        document_name=document["file_name"]
    )
    
    # Add navigation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Change Document", use_container_width=True):
            del st.session_state.selected_document
            st.rerun()
    
    with col2:
        if st.button("📤 Upload Document", use_container_width=True):
            st.session_state.current_page = "Upload"
            st.rerun()
    
    with col3:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.current_page = "Home"
            st.rerun()