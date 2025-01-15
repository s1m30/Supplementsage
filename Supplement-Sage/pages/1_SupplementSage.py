# Imports
from typing import Dict, List, Any, Union
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from langchain_huggingface import HuggingFaceEmbeddings
from app_get_response import get_response
from app_authentication import setup_authentication
from app_component import upload_view_delete
from langchain_core.vectorstores import InMemoryVectorStore
from app_component  import choose_llm
from langchain_openai import OpenAIEmbeddings
from fpdf import FPDF
import uuid
import os
#Authentication Setup
# supabase,user_id=setup_authentication()
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

#Session States Initialization
# Initialize session state for additional inputs
if "web_inputs" not in st.session_state:
    st.session_state.web_inputs = []

if "youtube_inputs" not in st.session_state:
    st.session_state.youtube_inputs = []

# Initialize session state for saved sources
if "saved_sources" not in st.session_state:
    st.session_state.saved_sources = []

if "dbs" not in st.session_state:
    st.session_state.dbs=[]
if "documents" not in st.session_state:
    st.session_state.documents ={}  # Initialize document dictionary
    st.session_state.bm25_retriever = None
 


# Sidebar: User Inputs
with st.sidebar:
    st.title("🤖💬 Supplement Sage")
    #Component for choosing and inputting LLM creds
    llm=choose_llm()
    print("Returned LLM: ",llm)
    #Component for uploading/viewing and deleting
    upload_view_delete(supabase)
    st.session_state.embedding= OpenAIEmbeddings() if llm=="openai" else HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    print("embedding",st.session_state.embedding)
    #Initialize db session_state
    if "db" not in st.session_state:
        st.session_state.db=InMemoryVectorStore(embedding=st.session_state.embedding)
        

# Export Chats as PDF
if st.button("Save Chat as PDF"):
    if st.session_state.messages:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Add content to the PDF
        pdf.cell(200, 10, txt="Chat History", ln=True, align='C')
        pdf.ln(10)  # Add a line break

        for msg in st.session_state.messages:
            role = "Human" if isinstance(msg, HumanMessage) else "AI"
            pdf.multi_cell(0, 10, txt=f"{role}: {msg.content}")
            pdf.ln(5)  # Add spacing between messages

        # Save PDF
        pdf_file = f"chat_{str(uuid.uuid4())}_session.pdf"
        pdf.output(pdf_file)

        # Provide download button for the PDF
        with open(pdf_file, "rb") as f:
            st.download_button(
                label="Download Chat as PDF",
                data=f,
                file_name=pdf_file,
                mime="application/pdf"
            )
        
        os.remove(pdf_file)
    else:
        st.warning("No chat messages to save!")
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

if prompt := st.chat_input("Ask a question"):
    with st.chat_message("Human"):
        st.markdown(prompt)

    with st.chat_message("AI"):
        # human_prompt=HumanMessage(prompt)
        with st.spinner('Just a bit...'):   
            response=st.write_stream(get_response(prompt, st.session_state.messages,st.session_state.db,  st.session_state.dbs,llm,st.session_state.repo_id))
    st.session_state.messages.append(HumanMessage(content=prompt))
    st.session_state.messages.append(AIMessage(content=response))

