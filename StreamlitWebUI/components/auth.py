import streamlit as st
from utils.api import register_user, login_user

def show_login_form():
    # Page header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 40px;">
        <h1 style="color: #2E86C1;">Welcome to RAG Document System</h1>
        <p style="font-size: 16px; color: #566573;">
            Secure document management and intelligent query system
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Split layout
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("""
        <div style="padding: 25px; border-radius: 10px; background-color: #F8F9F9;">
            <h3 style="color: #2E86C1;">📚 Features</h3>
            <ul style="list-style-type: none; padding-left: 0;">
                <li>• Secure document storage</li>
                <li>• AI-powered chat with documents</li>
                <li>• Natural language query system</li>
                <li>• Role-based access control</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        with st.form("login_form"):
            st.subheader("Login to Your Account")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                response = login_user(email, password)
                if response.status_code == 200:
                    token_data = response.json()
                    st.session_state.update({
                        "authenticated": True,
                        "access_token": token_data["access_token"],
                        "user_id": token_data["user_id"],
                        "email": token_data["email"]
                    })
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")

        st.caption("Don't have an account? Register instead.")
        if st.button("Go to Registration"):
            st.session_state.show_registration = True
            st.rerun()

def show_registration_form():
    # Page header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 40px;">
        <h1 style="color: #2E86C1;">Create New Account</h1>
        <p style="font-size: 16px; color: #566573;">
            Get started with our document management system
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Split layout
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("""
        <div style="padding: 25px; border-radius: 10px; background-color: #F8F9F9;">
            <h3 style="color: #2E86C1;">🔒 Account Requirements</h3>
            <ul style="list-style-type: none; padding-left: 0;">
                <li>• Valid email address</li>
                <li>• Unique username</li>
                <li>• Password (8+ characters)</li>
                <li>• No special characters in username</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        with st.form("registration_form"):
            st.subheader("Registration Form")
            email = st.text_input("Email")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Register")
            
            if submitted:
                if not all([email, username, password]):
                    st.error("All fields are required")
                    return
                    
                response = register_user({
                    "email": email,
                    "username": username,
                    "password": password
                })
                
                if response.status_code == 201:
                    st.success("Registration successful! Please login.")
                    st.session_state.show_registration = False
                    st.rerun()
                else:
                    error = response.json().get("detail", "Registration failed")
                    st.error(f"Registration error: {error}")
                    
        st.caption("Already have an account? Login instead.")
        if st.button("Go to Login"):
            st.session_state.show_registration = False
            st.rerun()