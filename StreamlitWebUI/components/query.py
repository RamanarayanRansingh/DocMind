import streamlit as st
import pandas as pd
from utils.helpers import check_authentication
from utils.api import send_nl_query, get_query_history, clear_query_history

def show_query_interface():
    """Main interface for natural language to SQL queries"""
    check_authentication()
    
    st.title("🔍 Natural Language to SQL Query")
    
    # Query input
    with st.form(key="nl_query_form", clear_on_submit=True):
        query = st.text_area(
            "Ask a question about your database",
            placeholder="e.g., How many albums does AC/DC have?",
            height=100,
            key="nl_query_input"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            submit_btn = st.form_submit_button("Send", use_container_width=True)
        with col2:
            clear_btn = st.form_submit_button("Clear History", type="secondary", use_container_width=True)
        
        if submit_btn and query.strip():
            with st.spinner("Processing your query..."):
                try:
                    response = send_nl_query(query, st.session_state.access_token)
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Create a chat-like message
                        st.markdown(f"""
                        **You:** {query}
                        
                        **AI:** {data['response']}
                        
                        *Query Details:*
                        - **SQL Query:** 
                        ```sql
                        {data['sql_query']}
                        ```
                        """)
                        
                        # Add to query history
                        if "query_history" not in st.session_state:
                            st.session_state.query_history = []
                        st.session_state.query_history.insert(0, data)
                    else:
                        st.error(f"Query failed: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error running query: {str(e)}")
        
        # Clear query history
        if clear_btn:
            with st.spinner("Clearing query history..."):
                try:
                    response = clear_query_history(st.session_state.access_token)
                    if response.status_code == 200:
                        st.session_state.query_history = []
                        st.success("Query history cleared successfully!")
                    else:
                        st.error(f"Failed to clear history: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error clearing history: {str(e)}")
            st.rerun()

def show_query_history():
    """Display past queries and results"""
    check_authentication()
    
    st.markdown("## Query History")
    
    if "query_history" not in st.session_state:
        with st.spinner("Loading query history..."):
            try:
                response = get_query_history(st.session_state.access_token)
                if response.status_code == 200:
                    st.session_state.query_history = response.json()
                else:
                    st.error("Failed to load query history")
                    return
            except Exception as e:
                st.error(f"Error loading query history: {str(e)}")
                return
    
    if not st.session_state.query_history:
        st.info("No query history yet. Run some queries to see them here!")
        return
    
    for idx, query in enumerate(st.session_state.query_history):
        st.markdown(f"""
        **You:** {query['natural_query']}
        
        **AI:** {query['response']}
        
        *Query Details:*
        - **SQL Query:** 
        ```sql
        {query['sql_query']}
        ```
        """)
        if idx < len(st.session_state.query_history) - 1:
            st.markdown("---")  # Add a separator between queries