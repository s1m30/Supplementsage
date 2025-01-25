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
    )
    if not session:
        st.stop()
    with st.sidebar:
      if session:
        st.write(f"Welcome {session['user']['email']}")
        logout_button()
    return supabase,session["user"]["id"]



