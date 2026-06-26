import streamlit as st

from auth.auth import authenticate_user, create_user


def render_auth_ui():
    """
    Renders the authentication tabs (Login & Register) in Streamlit.
    Blocks downstream code execution until authentication is successful.
    """
    st.markdown(
        "<h1 style='text-align: center;'>Welcome to KakeiboAI</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; color: #888;'>Japanese-style Mindful Personal Finance Coach</p>",
        unsafe_allow_html=True,
    )

    tab_login, tab_register = st.tabs(["🔑 Login", "📝 Register"])

    with tab_login:
        st.subheader("Login to your account")
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", key="login_username").strip()
            password = st.text_input("Password", type="password", key="login_password")
            submit = st.form_submit_button("Login", use_container_width=True)

            if submit:
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    success, message, user_id = authenticate_user(username, password)
                    if success:
                        st.session_state["authenticated"] = True
                        st.session_state["user_id"] = user_id
                        st.session_state["username"] = username
                        st.session_state["chat_messages"] = []
                        st.success("Logged in successfully! Redirecting...")
                        st.rerun()
                    else:
                        st.error(message)

    with tab_register:
        st.subheader("Create a new account")
        with st.form("register_form", clear_on_submit=False):
            username = st.text_input("Username", key="register_username").strip()
            password = st.text_input("Password", type="password", key="register_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="register_confirm")
            submit = st.form_submit_button("Register", use_container_width=True)

            if submit:
                if not username:
                    st.error("Username cannot be empty.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, message = create_user(username, password)
                    if success:
                        st.success(message)
                        # Auto-login after successful registration
                        success_auth, _, user_id = authenticate_user(username, password)
                        if success_auth:
                            st.session_state["authenticated"] = True
                            st.session_state["user_id"] = user_id
                            st.session_state["username"] = username
                            st.session_state["chat_messages"] = []
                            st.rerun()
                    else:
                        st.error(message)
