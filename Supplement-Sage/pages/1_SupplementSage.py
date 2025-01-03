# Imports
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Union
import streamlit as st
from app_helper import add_to_vector_store, delete_vector_store
# from streamlit_option_menu import option_menus
from supa import SupabaseVectorStore
from langchain_core.messages import HumanMessage, AIMessage
from langchain_huggingface import HuggingFaceEmbeddings, HuggingFaceEndpoint
from app_load_llm import get_response
from app_authentication import setup_authentication
from app_loader import group_sources, load_sources
from app_helper import choose_llm, add_web_input, add_youtube_input, get_college_data, add_college_questions_to_vector_store, remove_source, get_college_name
# from cryptography.fernet import Fernet
# import uuid
# import datetime


#Functions
# Initialize session state for additional inputs
supabase,user_id=setup_authentication()
if "web_inputs" not in st.session_state:
    st.session_state.web_inputs = []

if "youtube_inputs" not in st.session_state:
    st.session_state.youtube_inputs = []

# Initialize session state for saved sources
if "saved_sources" not in st.session_state:
    st.session_state.saved_sources = []
# Initialize unique document IDs if not present
if "doc_ids" not in st.session_state:
    st.session_state.doc_ids = []
    
if "db" not in st.session_state:
    st.session_state.db= SupabaseVectorStore(
    client=supabase,
    table_name="vector_store",
    query_name="match_documents",
    
    embedding= HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
)

if "dbs" not in st.session_state:
    st.session_state.dbs=[]

# Sidebar: User Inputs
with st.sidebar:
    st.title("🤖💬 Supplement Sage")
    choose_llm()
    
    st.title("Sources")
    files = st.file_uploader("Upload files", accept_multiple_files=True, type=["txt", "pdf", "docx", "csv"])
    # Prepare inputs for grouping
    # Base web and YouTube inputs
    web_url = st.text_input("Web Loader URL (default)")
    ytb_url = st.text_input("YouTube Loader URL (default)")

    # Buttons to add more inputs
    if st.button("Add another Web Loader URL"):
        add_web_input()

    if st.button("Add another YouTube Loader URL"):
        add_youtube_input()

    # Display additional inputs for Web Loader
    for i, value in enumerate(st.session_state.web_inputs):
        st.session_state.web_inputs[i] = st.text_input(f"Additional Web Loader URL {i+1}", value=value)

    # Display additional inputs for YouTube Loader
    for i, value in enumerate(st.session_state.youtube_inputs):
        st.session_state.youtube_inputs[i] = st.text_input(f"Additional YouTube Loader URL {i+1}", value=value)
    all_web_urls = [web_url] + st.session_state.web_inputs
    all_ytb_urls = [ytb_url] + st.session_state.youtube_inputs

    # Fetch data
    st.session_state.college_names = get_college_name(supabase)
    selected_colleges = st.multiselect("Search or select a college:", options= st.session_state.college_names)
    # Handle colleges being removed from selection
    if "last_selected_colleges" not in st.session_state:
        st.session_state.last_selected_colleges = []

    # Find removed colleges and delete their vector stores
    removed_colleges = set(st.session_state.last_selected_colleges) - set(selected_colleges)
    for college in removed_colleges:
        delete_vector_store(college)

    st.session_state.last_selected_colleges = selected_colleges
    if st.button("See Questions"):  
        for college in selected_colleges:
            st.subheader(college)
            st.session_state.essay_data=get_college_data(college,supabase)
            
            # Display questions and add to vector store
            st.session_state.dbs.append(add_to_vector_store(college, st.session_state.essay_data))
            for row in st.session_state.essay_data:
                st.write(row["question"])

    st.divider()

    # Save Sources
    if st.button("Save Sources"):
        grouped_sources = group_sources(files, all_ytb_urls, all_web_urls)
        # if selected_colleges:
        #     add_college_questions_to_vector_store(selected_colleges, college_data)
        if grouped_sources:
            load_sources(grouped_sources,st.session_state.db,user_id,supabase)

        st.success("Sources saved and questions added to the vector store!")
    # Display saved sources in an expander
    with st.expander("Saved Sources", expanded=True):
        for source in st.session_state.saved_sources:
            col1, col2 = st.columns([4, 1])  # Create columns for source name and cancel button
            with col1:
                st.text(f"{source['name']}")  # Display source name and type
            with col2:
                if st.button(f"Remove", key=source["id"]):
                    remove_source(source["id"])  # Remove source when cancel button is clicked
                    
# Main Application
st.title("🧠 SupplementSage: Your AI-Powered College Essay Assistant")
st.markdown("""
#### Supplementsage is your #1 A.I. powered tool for college essays.

## Features 🌟
- ##### Upload from multiple sources- Youtube, Websites, PDFs, Texts, Microsoft Word(docx)
- ##### Summarize or analyze content from university websites, youtube videos, essay sample documents e.t.c.
- ##### Access 110+ supplemental essays easily on the app.
- ##### Choose the role of your AI bot(University Analysis, Essay Grading, Essay Comparison)
- ##### 👈 Refer to the Walkthrough for examples**
- ##### Saved Chats coming soon
""",unsafe_allow_html= True)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message("Human" if isinstance(message, HumanMessage) else "AI"):
        st.write(message.content)
st.multiselect("Role",options=["General","Essay grader","University Analysis", "Grammar Correction"])

if prompt := st.chat_input("Ask a question"):
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("Human"):
        st.markdown(prompt)

    with st.chat_message("AI"):
        # human_prompt=HumanMessage(prompt)
        response=st.write_stream(get_response(prompt, st.session_state.messages,st.session_state.db,  st.session_state.dbs))
    st.session_state.messages.append(AIMessage(content=response))

  