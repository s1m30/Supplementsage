import streamlit as st
from streamlit_supabase_auth import login_form as supabase_login, logout_button
from supabase import create_client, Client
from st_login_form import login_form
def setup_authentication():
    # Setup: Supabase
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # User Authentication
    session = supabase_login(
        url=SUPABASE_URL,
        apiKey=SUPABASE_KEY,
        providers=["github", "google"],
    )
    if not session:
        st.stop()
    with st.sidebar:
      if session:
        st.write(f"Welcome {session['user']['email']}")
        logout_button()
    return supabase,session["user"]["id"]

# def supabase_login(url, apiKey, providers):
#     """
#     Handles user authentication using Supabase and optional OAuth providers.
#     Persists the session to prevent re-prompting for login after authentication.
#     Args:
#         url (str): Supabase project URL.
#         apiKey (str): Supabase API key.
#         providers (list): List of OAuth providers (e.g., ["github", "google"]).
#     Returns:
#         dict: Session object containing user details if authentication succeeds.
#     """
#     # Initialize Supabase client
#     supabase: Client = create_client(url, apiKey)

#     # If session exists in session_state, return it immediately
#     if "auth_session" in st.session_state:
#         return st.session_state["auth_session"]

#     # UI for authentication
#     st.title("Sign In")
#     option = st.selectbox("Choose a login method", ["Email & Password"] + providers)

#     if option == "Email & Password":
#         with st.form(key="login_form"):
#             email = st.text_input("Email address")
#             password = st.text_input("Password", type="password")
#             remember_me = st.checkbox("Remember me")
#             submit = st.form_submit_button("Sign In")

#         if submit:
#             try:
#                 # Authenticate using Supabase
#                 response = supabase.auth.sign_in_with_password({"email": email, "password": password})
#                 st.session_state["auth_session"] = response  # Save session to session_state
#                 st.success("Successfully signed in!")
#                 st.rerun()  # Trigger a rerun to clear the login box
#             except Exception as e:
#                 st.error(f"Login failed: {e}")

#     elif option in providers:
#         # OAuth provider authentication
#         provider = option.lower()
#         st.write(f"Redirecting to {provider.capitalize()} for authentication...")
#         auth_url = f"{url}/auth/v1/authorize?provider={provider}&redirect_to={st.secrets['REDIRECT_URL']}"
#         st.markdown(f"[Sign in with {provider.capitalize()}]({auth_url})", unsafe_allow_html=True)

#     return None

# def logout_button():
#     """
#     Clears the session and refreshes the app.
#     """
#     if st.button("Logout"):
#         del st.session_state["auth_session"]  # Clear the stored session
#         st.rerun()  # Refresh the app



# def setup_authentication():
#     """
#     Set up Supabase authentication with streamlined user login.
#     Returns:
#         - supabase: The Supabase client instance.
#         - user_id: The authenticated user's ID.
#     """
#     # Setup: Supabase
#     SUPABASE_URL = st.secrets["SUPABASE_URL"]
#     SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
#     supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

#     # User Authentication
#     session = supabase_login(
#         url=SUPABASE_URL,
#         apiKey=SUPABASE_KEY,
#         providers=["github", "google"],  # Supports GitHub and Google OAuth
#     )

#     # Stop execution if no session is available
#     if not session:
#         st.stop()

#     # Sidebar User Info
#     with st.sidebar:
#         if session:
#             st.success(f"Welcome, {session.user.email}!")
#             logout_button()  # Custom logout button function

#     # Return the Supabase client and user ID
#     return supabase, session.user.id

