import streamlit as st 
import os
import base64
from streamlit_option_menu import option_menu
# st.set_page_config(
#     page_title="Hello",
#     page_icon="👋",
# )

st.write("# Welcome to SupplementSage! 👋")
# with st.sidebar:
#     selected=option_menu(
#     menu_title=None,
#     options=["Home","Login"],
#     icons=["house","box-arrow-in-left"],
#     styles={"container":{"background-color":"#13101a"}}
    
# )
#     if selected=="Login":
#         st.switch_page("pages/1_SupplementSage.py")
st.sidebar.success("Select a demo above.")
# Call the function with your preferred image URL
# Add custom CSS styling for the background image

# def get_img_as_base64(file):
#     with open(file,"rb") as f:
#         data= f.read()
#     return base64.b64encode(data).decode()
# img=get_img_as_base64("background.jpg")
def add_bg_from_url():
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"]{{
            background-image: url("data:image/png;base64,{img}");
            background-size: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-color:rgba(0,0,0,0);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# add_bg_from_url()

# About page content
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"]{{
        background-color:rgba(0,0,0,0);
    }}
    </style>
    # SupplementSage 📝✨
    
    Welcome to **SupplementSage**, your AI-powered companion for crafting exceptional college supplemental essays.  
    Our mission is to empower students and applicants by simplifying the research and brainstorming process for supplemental essays and beyond.
    
    ## Key Features 🌟
    - **Web Scraping & Analysis**  
    Automatically fetch and analyze essay prompts and school-specific requirements from trusted sources.
    - **Personalized Guidance**  
    Upload your documents or links to receive personalized, context-aware advice and suggestions.
    - **Seamless Integration**  
    Combine the power of Langchain, OpenAI, and RAG systems to deliver precise and actionable insights.
    - **Session Management**  
    Store, retrieve, and manage chat histories for every session.  
    - **PDF Export**  
    Save your chats and recommendations as a professional PDF for later use.
    
    ## Explore Examples
    👈 Use the sidebar to explore various **demo features** and discover how SupplementSage can elevate your essay-writing process.

    ## Get Started 🚀
    - Upload essay prompts, links, or documents to begin.  
    - Let SupplementSage do the heavy lifting for you!
    
    ---
    
    **Have questions or feedback?** Contact us for support and assistance.  
    """,unsafe_allow_html= True
)


