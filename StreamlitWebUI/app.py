import streamlit as st
from utils.helpers import initialize_session_state
from components.auth import show_login_form, show_registration_form

# Initialize session state
initialize_session_state()

# Set page config - MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="RAG Document System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
hide_streamlit_style = """
    <style>
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stDeployButton {display:none;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

if not st.session_state.authenticated:
    # Hide sidebar for unauthenticated users
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    if st.session_state.get("show_registration"):
        show_registration_form()
    else:
        show_login_form()
else:
    # Show custom sidebar
    with st.sidebar:
        st.title("RAG System Navigation")
        
        # Main navigation
        page = st.radio(
            "Main Menu",
            ["Home", "Upload", "Chat", "WebRAG", "WebChat", "Query"],
            index=["Home", "Upload", "Chat", "WebRAG", "WebChat", "Query"].index(
                st.session_state.get("current_page", "Home")
            )
        )
        
        # Update current page in session state
        if page != st.session_state.get("current_page", "Home"):
            st.session_state.current_page = page
            st.rerun()
        
        st.markdown("---")
        
        # Quick actions section
        st.markdown("### Quick Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Docs", use_container_width=True):
                st.session_state.current_page = "Upload"
                st.rerun()
        
        with col2:
            if st.button("🌐 Web", use_container_width=True):
                st.session_state.current_page = "WebRAG"
                st.rerun()
        
        col3, col4 = st.columns(2)
        with col3:
            if st.button("💬 Chat", use_container_width=True):
                st.session_state.current_page = "Chat"
                st.rerun()
        
        with col4:
            if st.button("🌐💬 WebChat", use_container_width=True):
                st.session_state.current_page = "WebChat"
                st.rerun()
        
        st.markdown("---")
        
        # Logout button
        if st.button("🔓 Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        
        # User info
        st.markdown(f"""
            <div style="margin-top: 30px;">
                <p style="margin-bottom: 0;">Logged in as:</p>
                <strong>{st.session_state.email}</strong>
            </div>
        """, unsafe_allow_html=True)

    # Load selected page
    current_page = st.session_state.get("current_page", "Home")
    
    if current_page == "Home":
        from content import Home
        Home.show()
    elif current_page == "Upload":
        from content import Upload
        Upload.show()
    elif current_page == "Chat":
        from content import Chat
        Chat.show()
    elif current_page == "WebRAG":
        from content import WebRAG
        WebRAG.show()
    elif current_page == "WebChat":
        from content import WebChat
        WebChat.show()
    elif current_page == "Query":
        from content import Query
        Query.show()