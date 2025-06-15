import streamlit as st
from utils.helpers import check_authentication
from utils.api import get_user_documents, get_indexed_urls
import pandas as pd

def show():
    check_authentication()
    
    # Page header
    st.title("🏠 Welcome to RAG Document System")
    st.markdown("Your intelligent document management and query system.")
    
    # Introduction Section
    st.markdown("""
    ### What You Can Do:
    - **Upload Documents**: Store and manage your PDFs, CSVs, and Excel files.
    - **Chat with Documents**: Ask questions and get insights from your documents.
    - **Index Web Content**: Add URLs and chat with web content.
    - **Query Database**: Use natural language to query your database.
    """)
    
    # Dashboard stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        try:
            response = get_user_documents(st.session_state.access_token)
            doc_count = len(response.json()) if response.status_code == 200 else 0
        except:
            doc_count = 0
        
        st.metric("📄 Documents", doc_count)
    
    with col2:
        try:
            response = get_indexed_urls(st.session_state.access_token)
            if response.status_code == 200:
                response_data = response.json()
                if isinstance(response_data, dict):
                    url_count = len(response_data.get("urls", []))
                elif isinstance(response_data, list):
                    url_count = len(response_data)
                else:
                    url_count = 0
            else:
                url_count = 0
        except:
            url_count = 0
        
        st.metric("🔗 Indexed URLs", url_count)
    
    with col3:
        st.metric("🔍 Total Sources", doc_count + url_count)
    
    # Recent Documents Section
    st.markdown("## 📄 Your Recent Documents")
    try:
        response = get_user_documents(st.session_state.access_token)
        if response.status_code == 200:
            documents = response.json()[:3]  # Show last 3 documents
            if documents:
                for doc in documents:
                    with st.expander(f"{doc['file_name']} ({doc['file_type'].upper()})", expanded=False):
                        st.markdown(f"""
                        **Uploaded:** {pd.to_datetime(doc['uploaded_at']).strftime("%Y-%m-%d %H:%M")}
                        """)
                        if st.button("Chat with this Document", key=f"chat_{doc['id']}"):
                            st.session_state.selected_document = doc
                            st.session_state.current_page = "Chat"
                            st.rerun()
            else:
                st.info("You haven't uploaded any documents yet. Start by uploading one!")
        else:
            st.error("Could not load recent documents")
    except Exception as e:
        st.error(f"Error loading documents: {str(e)}")

    # Recent Web Content Section
    st.markdown("## 🌐 Your Indexed Web Content")
    try:
        response = get_indexed_urls(st.session_state.access_token)
        if response.status_code == 200:
            response_data = response.json()
            # Handle different response formats
            if isinstance(response_data, dict):
                urls = response_data.get("urls", [])
            elif isinstance(response_data, list):
                urls = response_data
            else:
                urls = []
            
            # Show last 3 URLs
            recent_urls = urls[:3]
            
            if recent_urls:
                for i, url in enumerate(recent_urls, 1):
                    # Convert URL to string if it's not already
                    url_str = str(url) if not isinstance(url, str) else url
                    
                    # Safe string truncation
                    display_url = url_str
                    if len(url_str) > 50:
                        display_url = url_str[:50] + "..."
                    
                    with st.expander(f"🔗 {display_url}", expanded=False):
                        st.markdown(f"**URL:** [{url_str}]({url_str})")
                        if st.button("Chat about Web Content", key=f"webchat_{i}"):
                            st.session_state.current_page = "WebChat"
                            st.rerun()
            else:
                st.info("You haven't indexed any web content yet. Start by adding URLs!")
        else:
            st.error("Could not load indexed URLs")
    except Exception as e:
        st.error(f"Error loading web content: {str(e)}")

    # Quick Actions
    st.markdown("## ⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📤 Upload Document", use_container_width=True):
            st.session_state.current_page = "Upload"
            st.rerun()
    
    with col2:
        if st.button("💬 Document Chat", use_container_width=True):
            st.session_state.current_page = "Chat"
            st.rerun()
    
    with col3:
        if st.button("🌐 Web Content", use_container_width=True):
            st.session_state.current_page = "WebRAG"
            st.rerun()
    
    with col4:
        if st.button("🔍 Run Query", use_container_width=True):
            st.session_state.current_page = "Query"
            st.rerun()

    # User Info
    st.markdown("---")
    st.markdown(f"Logged in as: **{st.session_state.email}**")