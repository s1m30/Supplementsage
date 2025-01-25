# Imports
from typing import Dict, List, Any, Union
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from langchain_RAG.app_get_response import langchain_RAG
from langchain_RAG.app_authentication import setup_authentication
from CortexSearch_RAG.helper import cortex_config,answer_question
from fpdf import FPDF
import uuid
import os
from langchain_RAG.app_component import langchain_config
from langchain.retrievers import EnsembleRetriever

def init_messages():
    # Initialize chat history
    st.session_state.messages = []
# Export Chats as PDF
def save_chat(RG_PROV):
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
                if RG_PROV=="Langchain":
                    role = "Human" if isinstance(msg, HumanMessage) else "AI"
                elif RG_PROV=="CortexSearch":
                    # For CortexSearch, use the role and content directly from the dictionary
                    role = msg["role"].capitalize()
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

def display_chat_messages(messages, method):
    """Displays chat messages based on the chosen method."""
    if method == "Langchain":
        for message in messages:
            with st.chat_message("Human" if isinstance(message, HumanMessage) else "AI"):
                st.write(message.content)
    elif method == "CortexSearch":
        for message in messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

def handle_user_input(prompt, method):
    """Handles user input and response generation for the chosen method."""
    if method == "Langchain":
        with st.chat_message("Human"):
            st.markdown(prompt)

        with st.chat_message("AI"):
            with st.spinner("Just a bit..."):
                response = st.write_stream(langchain_RAG(prompt, st.session_state.messages, st.session_state.llm, st.session_state.repo_id))
        
        st.session_state.messages.append(HumanMessage(content=prompt))
        st.session_state.messages.append(AIMessage(content=response))

    elif method == "CortexSearch":
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            question = prompt.replace("'", "")

            with st.spinner("mistral-large thinking..."):
                response = answer_question(question)
                response = response.replace("'", "")
                message_placeholder.markdown(response)
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": response})

def main():
    # Sidebar: User Inputs
    with st.sidebar:
        st.title("🤖💬 Supplement Sage")
        st.button("Start Over", key="clear_conversation", on_click=init_messages)
        #Component for choosing and inputting LLM creds
        RAG_Provider=st.selectbox("Choose a RAG Provider:",options=["CortexSearch", "Langchain"],key="RGProv",on_change=init_messages)
        if 'messages' not in st.session_state:
            init_messages()
        if RAG_Provider=="CortexSearch":
            cortex_config() 
        else:
            langchain_config()
            try:
                st.session_state.ensemble_retriever = EnsembleRetriever(retrievers=[i.as_retriever() for i in st.session_state.dbs]+ [st.session_state.db.as_retriever()]+[st.session_state.bm25_retriever])
            except:
                st.session_state.ensemble_retriever = EnsembleRetriever(retrievers=[i.as_retriever() for i in st.session_state.dbs]+ [st.session_state.db.as_retriever()])     
        
    save_chat(RAG_Provider)
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


    # Display chat messages
    display_chat_messages(st.session_state.messages, RAG_Provider)

    # Handle user input
    if prompt := st.chat_input("Ask a question"):
        handle_user_input(prompt, RAG_Provider)

if __name__ == "__main__":
    main()
