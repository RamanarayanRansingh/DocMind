import streamlit as st
import pandas as pd
from datetime import datetime
from utils.api import send_chat_message, get_chat_history, clear_chat_history
from utils.helpers import check_authentication

def chat_interface(document_id: int, document_name: str):
    check_authentication()
    
    # Chat history key
    chat_key = f"chat_{document_id}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []
    
    # Load initial chat history
    if not st.session_state[chat_key]:
        try:
            response = get_chat_history(document_id, st.session_state.access_token)
            if response.status_code == 200:
                st.session_state[chat_key] = response.json()
        except Exception as e:
            st.error(f"Error loading chat history: {e}")
    
    # Chat header
    st.markdown(f"## 💬 {document_name}")
    st.markdown("Ask questions about your document")

    # Display chat history
    for msg in st.session_state[chat_key]:
        st.chat_message("human").write(msg.get('message'))
        st.chat_message("assistant").write(msg.get('response'))
    
    # User input
    if prompt := st.chat_input(f"Ask about {document_name}..."):
        # Send user message
        st.chat_message("human").write(prompt)
        
        # Get AI response
        response = send_chat_message(
            document_id=document_id,
            message=prompt,
            token=st.session_state.access_token
        )
        
        if response.status_code == 200:
            result = response.json()
            st.chat_message("assistant").write(result.get('response'))
            
            # Update chat history
            st.session_state[chat_key].append({
                'message': prompt,
                'response': result.get('response')
            })
        else:
            st.error("Failed to get response")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear History", key="clear_chat"):
            clear_chat_history(document_id, st.session_state.access_token)
            st.session_state[chat_key] = []
            st.rerun()
    
    with col2:
        if st.button("Export Chat", key="export_chat"):
            try:
                df = pd.DataFrame(st.session_state[chat_key])
                st.download_button(
                    label="Download Chat History",
                    data=df.to_csv(index=False).encode('utf-8'),
                    file_name=f"chat_history_{document_id}.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Export failed: {e}")