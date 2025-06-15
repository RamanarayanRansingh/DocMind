import streamlit as st
import pandas as pd
from datetime import datetime
from utils.api import (
    add_url_to_webrag, add_multiple_urls_to_webrag, get_indexed_urls,
    remove_url_from_webrag, clear_all_webrag_urls, send_web_chat_message,
    get_web_chat_history, clear_web_chat_history
)
from utils.helpers import check_authentication
import validators
import re

def show_url_management():
    """URL management interface for WebRAG"""
    check_authentication()
    
    st.title("🌐 Web Content Hub")
    
    # URL addition section
    with st.expander("➕ Add Web Content", expanded=True):
        tab1, tab2 = st.tabs(["Single URL", "Multiple URLs"])
        
        with tab1:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                url_input = st.text_input(
                    "Enter URL",
                    placeholder="https://example.com/article",
                    help="Enter a valid URL to index for chat",
                    label_visibility="collapsed"
                )
            
            with col2:
                if st.button("Add URL", type="primary", use_container_width=True):
                    if url_input:
                        _add_single_url(url_input)
                    else:
                        st.error("Please enter a URL")
        
        with tab2:
            urls_text = st.text_area(
                "Enter multiple URLs (one per line)",
                placeholder="https://example.com/article1\nhttps://example.com/article2\nhttps://example.com/article3",
                height=100,
                label_visibility="collapsed"
            )
            
            if st.button("Add All URLs", type="primary", use_container_width=True):
                if urls_text:
                    urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
                    _add_multiple_urls(urls)
                else:
                    st.error("Please enter at least one URL")

def _add_single_url(url: str):
    """Helper function to add a single URL"""
    with st.spinner("Processing URL..."):
        response = add_url_to_webrag(url, st.session_state.access_token)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                st.success(f"✅ URL added successfully!")
                # Clear cached URL list to refresh
                if "indexed_urls" in st.session_state:
                    del st.session_state.indexed_urls
            else:
                st.error(f"Failed to add URL: {result.get('error', 'Unknown error')}")
        else:
            error_detail = response.json().get('detail', 'Unknown error') if response.headers.get('content-type') == 'application/json' else 'Server error'
            st.error(f"Failed to add URL: {error_detail}")

def _add_multiple_urls(urls: list):
    """Helper function to add multiple URLs"""
    with st.spinner(f"Processing {len(urls)} URLs..."):
        response = add_multiple_urls_to_webrag(urls, st.session_state.access_token)
        
        if response.status_code == 200:
            results = response.json().get("results", [])
            
            success_count = sum(1 for r in results if r.get("success"))
            failure_count = len(results) - success_count
            
            if success_count > 0:
                st.success(f"✅ {success_count} URL(s) added successfully!")
            
            if failure_count > 0:
                st.warning(f"⚠️ {failure_count} URL(s) failed to process")
                
                # Show failed URLs
                failed_urls = [r.get("url") for r in results if not r.get("success")]
                with st.expander("View failed URLs"):
                    for url in failed_urls:
                        st.text(url)
            
            # Clear cached URL list to refresh
            if "indexed_urls" in st.session_state:
                del st.session_state.indexed_urls
        else:
            st.error("Failed to process URLs")

def show_indexed_urls():
    """Display and manage indexed URLs"""
    check_authentication()
    
    # Fetch indexed URLs with error handling
    try:
        if "indexed_urls" not in st.session_state:
            with st.spinner("Loading indexed URLs..."):
                response = get_indexed_urls(st.session_state.access_token)
                if response.status_code == 200:
                    response_data = response.json()
                    # Handle different response formats
                    if isinstance(response_data, dict):
                        st.session_state.indexed_urls = response_data.get("urls", [])
                    elif isinstance(response_data, list):
                        st.session_state.indexed_urls = response_data
                    else:
                        st.session_state.indexed_urls = []
                else:
                    st.error("Failed to load indexed URLs")
                    return
    except Exception as e:
        st.error(f"Network error: {str(e)}")
        return

    indexed_urls = st.session_state.indexed_urls

    if not indexed_urls:
        st.info("🔗 No URLs indexed yet. Add your first URL!")
        return

    st.subheader("🔗 Indexed URLs")
    
    # Convert URLs to strings if they're not already
    url_options = []
    for url in indexed_urls:
        if isinstance(url, dict):
            # If URL is a dict, extract the URL string
            url_str = url.get('url', str(url))
        else:
            url_str = str(url)
        url_options.append(url_str)
    
    # URL selection for management
    selected_urls = st.multiselect(
        "Select URLs to manage",
        options=url_options,
        format_func=lambda x: x if len(x) <= 60 else x[:57] + "...",
        placeholder="Choose URLs"
    )

    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        chat_btn = st.button("💬 Start Web Chat", use_container_width=True)
    
    with col2:
        remove_btn = st.button("🗑️ Remove Selected", disabled=not selected_urls, use_container_width=True)
    
    with col3:
        clear_all_btn = st.button("🧹 Clear All", type="secondary", use_container_width=True)

    # Perform actions
    if chat_btn:
        st.session_state.current_page = "WebChat"
        st.rerun()

    if remove_btn and selected_urls:
        _remove_urls(selected_urls)

    if clear_all_btn:
        _clear_all_urls()

    # Display URLs in a nice format
    st.markdown("### 📋 Your Indexed URLs")
    for i, url in enumerate(url_options, 1):
        domain = re.findall(r'https?://([^/]+)', url)
        domain_name = domain[0] if domain else "Unknown"
        
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{i}.** [{domain_name}]({url})")
                st.caption(url)
            with col2:
                if st.button("Remove", key=f"remove_{i}"):
                    _remove_urls([url])

def _remove_urls(urls: list):
    """Helper function to remove selected URLs"""
    with st.spinner("Removing URLs..."):
        success_count = 0
        failure_count = 0
        
        for url in urls:
            response = remove_url_from_webrag(url, st.session_state.access_token)
            if response.status_code == 200:
                success_count += 1
            else:
                failure_count += 1
        
        if success_count > 0:
            st.success(f"✅ {success_count} URL(s) removed successfully!")
        
        if failure_count > 0:
            st.error(f"❌ Failed to remove {failure_count} URL(s)")
        
        # Clear cached URL list to refresh
        if "indexed_urls" in st.session_state:
            del st.session_state.indexed_urls
        st.rerun()

def _clear_all_urls():
    """Helper function to clear all URLs"""
    if st.session_state.get("confirm_clear_all"):
        with st.spinner("Clearing all URLs..."):
            response = clear_all_webrag_urls(st.session_state.access_token)
            
            if response.status_code == 200:
                st.success("✅ All URLs cleared successfully!")
                # Clear cached URL list
                if "indexed_urls" in st.session_state:
                    del st.session_state.indexed_urls
                st.session_state.confirm_clear_all = False
                st.rerun()
            else:
                st.error("Failed to clear URLs")
        st.session_state.confirm_clear_all = False
    else:
        st.session_state.confirm_clear_all = True
        st.warning("Click again to confirm clearing all URLs")
        st.rerun()

def web_chat_interface():
    """Web chat interface for asking questions about indexed web content"""
    check_authentication()
    
    # Check if any URLs are indexed
    try:
        response = get_indexed_urls(st.session_state.access_token)
        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, dict):
                indexed_urls = response_data.get("urls", [])
            elif isinstance(response_data, list):
                indexed_urls = response_data
            else:
                indexed_urls = []
        else:
            indexed_urls = []
    except Exception as e:
        st.error(f"Error checking indexed URLs: {str(e)}")
        indexed_urls = []

    if not indexed_urls:
        st.markdown("## 🌐 Web Content Chat")
        st.info("You need to index at least one URL before starting a web chat.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔗 Add URLs", use_container_width=True):
                st.session_state.current_page = "WebRAG"
                st.rerun()
        
        with col2:
            if st.button("🏠 Back to Home", use_container_width=True):
                st.session_state.current_page = "Home"
                st.rerun()
        return

    # Chat interface
    st.title("🌐 Web Content Chat")
    st.markdown("Ask questions about your indexed web content")

    # Initialize chat history
    if "web_chat_history" not in st.session_state:
        try:
            response = get_web_chat_history(st.session_state.access_token)
            if response.status_code == 200:
                chat_data = response.json()
                # Handle different response formats
                if isinstance(chat_data, dict):
                    st.session_state.web_chat_history = chat_data.get("history", chat_data.get("messages", []))
                elif isinstance(chat_data, list):
                    st.session_state.web_chat_history = chat_data
                else:
                    st.session_state.web_chat_history = []
            else:
                st.session_state.web_chat_history = []
        except Exception as e:
            st.error(f"Error loading chat history: {e}")
            st.session_state.web_chat_history = []

    # Display chat history
    for msg in st.session_state.web_chat_history:
        st.chat_message("human").write(msg.get('message', ''))
        
        # Show response with sources
        with st.chat_message("assistant"):
            st.write(msg.get('response', ''))
            
            # Show sources if available
            sources = msg.get('sources', [])
            if sources:
                with st.expander("📚 Sources"):
                    for source in sources:
                        if isinstance(source, str):
                            st.markdown(f"- [{source}]({source})")
                        else:
                            st.markdown(f"- {str(source)}")

    # User input
    if prompt := st.chat_input("Ask about your indexed web content..."):
        # Display user message
        st.chat_message("human").write(prompt)
        
        # Get AI response
        with st.spinner("Getting response..."):
            response = send_web_chat_message(prompt, st.session_state.access_token)
            
            if response.status_code == 200:
                result = response.json()
                
                # Display assistant response
                with st.chat_message("assistant"):
                    st.write(result.get('response', ''))
                    
                    # Show sources if available
                    sources = result.get('sources', [])
                    if sources:
                        with st.expander("📚 Sources"):
                            for source in sources:
                                if isinstance(source, str):
                                    st.markdown(f"- [{source}]({source})")
                                else:
                                    st.markdown(f"- {str(source)}")
                
                # Update chat history
                st.session_state.web_chat_history.append({
                    'message': prompt,
                    'response': result.get('response', ''),
                    'sources': sources,
                    'timestamp': datetime.now().isoformat()
                })
            else:
                st.error("Failed to get response")

    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧹 Clear Chat History", use_container_width=True):
            response = clear_web_chat_history(st.session_state.access_token)
            if response.status_code == 200:
                st.session_state.web_chat_history = []
                st.success("Chat history cleared!")
                st.rerun()
            else:
                st.error("Failed to clear chat history")
    
    with col2:
        if st.button("🔗 Manage URLs", use_container_width=True):
            st.session_state.current_page = "WebRAG"
            st.rerun()
    
    with col3:
        if st.button("🏠 Back to Home", use_container_width=True):
            st.session_state.current_page = "Home"
            st.rerun()

    # Export chat functionality
    if st.session_state.web_chat_history:
        try:
            chat_data = []
            for msg in st.session_state.web_chat_history:
                # Handle sources properly
                sources = msg.get('sources', [])
                sources_str = ""
                if sources:
                    if isinstance(sources, list):
                        sources_str = ', '.join([str(s) for s in sources])
                    else:
                        sources_str = str(sources)
                
                chat_data.append({
                    'timestamp': msg.get('timestamp', datetime.now().isoformat()),
                    'message': msg.get('message', ''),
                    'response': msg.get('response', ''),
                    'sources': sources_str
                })
            
            df = pd.DataFrame(chat_data)
            csv = df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Export Chat History",
                data=csv,
                file_name=f"web_chat_history_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Export failed: {e}")