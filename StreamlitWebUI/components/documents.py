import streamlit as st
import pandas as pd
from datetime import datetime
from utils.api import get_user_documents, delete_document, upload_document
from utils.helpers import check_authentication

def show_document_upload():
    """Enhanced document upload interface"""
    check_authentication()
    
    st.title("📄 Document Hub")
    
    # Upload section with improved UI
    with st.expander("➕ Add New Document", expanded=True):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=["pdf", "csv", "xlsx", "xls"],
                help="Supported: PDF, CSV, Excel",
                label_visibility="collapsed"
            )
        
        with col2:
            upload_btn = st.empty()
        
        if uploaded_file is not None:
            upload_btn.button(
                "Upload", 
                type="primary", 
                use_container_width=True,
                on_click=_upload_document,
                args=(uploaded_file,)
            )

def _upload_document(uploaded_file):
    """Helper function to handle document upload"""
    with st.spinner("Processing document..."):
        response = upload_document(
            file=uploaded_file,
            token=st.session_state.access_token
        )
        
        if response.status_code == 200:
            st.success(f"✅ {uploaded_file.name} uploaded successfully!")
            # Clear cached document list to refresh
            if "document_list" in st.session_state:
                del st.session_state.document_list
            st.rerun()
        else:
            st.error(f"Upload failed: {response.json().get('detail', 'Unknown error')}")

def show_document_list():
    """Enhanced document list and management interface"""
    check_authentication()
    
    # Fetch documents with error handling
    try:
        if "document_list" not in st.session_state:
            with st.spinner("Loading documents..."):
                response = get_user_documents(st.session_state.access_token)
                if response.status_code == 200:
                    st.session_state.document_list = response.json()
                else:
                    st.error("Failed to load documents")
                    return
    except Exception as e:
        st.error(f"Network error: {str(e)}")
        return

    documents = st.session_state.document_list

    if not documents:
        st.info("📂 Your document collection is empty. Upload your first document!")
        return

    # Prepare document data
    df = pd.DataFrame([{
        "Select": doc["id"],
        "Name": doc["file_name"],
        "Type": doc["file_type"],
        "Uploaded": pd.to_datetime(doc["uploaded_at"]).strftime("%Y-%m-%d %H:%M")
    } for doc in documents])

    # Document management section
    st.subheader("📋 Your Documents")
    
    # Enhanced document display
    selected_docs = st.multiselect(
        "Select documents", 
        options=df["Select"],
        format_func=lambda x: next(doc["file_name"] for doc in documents if doc["id"] == x),
        placeholder="Choose documents"
    )

    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        chat_btn = st.button("💬 Start Chat", disabled=len(selected_docs) != 1)
    
    with col2:
        delete_btn = st.button("🗑️ Delete Selected", type="primary", disabled=not selected_docs)

    # Perform actions
    if chat_btn and len(selected_docs) == 1:
        selected_doc = next(doc for doc in documents if doc["id"] == selected_docs[0])
        st.session_state.selected_document = selected_doc
        st.session_state.current_page = "Chat"
        st.rerun()

    if delete_btn and selected_docs:
        _delete_documents(selected_docs)

    # Display document table
    st.dataframe(
        df.drop(columns=["Select"]),
        use_container_width=True,
        hide_index=True
    )

def _delete_documents(document_ids):
    """Helper function to delete selected documents"""
    with st.spinner("Deleting documents..."):
        success_count = 0
        failure_count = 0
        
        for doc_id in document_ids:
            response = delete_document(doc_id, st.session_state.access_token)
            if response.status_code == 200:
                success_count += 1
            else:
                failure_count += 1
        
        if success_count > 0:
            st.success(f"✅ {success_count} document(s) deleted successfully!")
        
        if failure_count > 0:
            st.error(f"❌ Failed to delete {failure_count} document(s)")
        
        # Clear cached document list to refresh
        if "document_list" in st.session_state:
            del st.session_state.document_list
        st.rerun()