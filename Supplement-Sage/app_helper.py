import streamlit as st
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import requests
from langchain.schema import Document
from typing import List
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
def clean_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["nav", "footer", "script", "style"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)

def split_text(cleaned_text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n\n","\n\n", "\n", " "]
    )
    return text_splitter.split_text(cleaned_text)

def filter_chunks(chunks):
    return [
        chunk for chunk in chunks
        if 50 < len(chunk.strip()) < 2000
        and not chunk.isspace()
    ]
    
# Function to get YouTube metadata
def get_youtube_metadata(video_id: str): 
    title, channel = get_youtube_video_info(f"https://www.youtube.com/watch?v={video_id}")
    return {"source": f"https://www.youtube.com/watch?v={video_id}", "title": f"{title}|{channel}", "type": "youtube"}

def get_youtube_video_info(url):
    try:
        # Send a request to the YouTube video URL
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP request errors

        # Parse the webpage content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the title from the HTML
        title = soup.find("title").text
        if title.endswith(" - YouTube"):
            title = title.replace(" - YouTube", "").strip()

        # Extract the channel name
        channel_tag = soup.find("link", itemprop="name")
        channel_name = channel_tag["content"] if channel_tag else "Unknown Channel"

        return title, channel_name
    except Exception as e:
        return None, f"Error: {e}"
    
# Function to remove a source
@st.fragment
def remove_source(doc_id: str):
    # Remove the document by its unique ID from the vector store
    ids=[id[0] for id in doc_id]
    st.session_state.db.delete(ids=ids)  # Ensure it's a list
    # Update session state by removing the deleted source
    st.session_state.saved_sources = [
        source for source in st.session_state.saved_sources if source["id"] != doc_id
    ]
    # Update document IDs
    st.session_state.doc_ids = [
        existing_id for existing_id in st.session_state.doc_ids if existing_id != doc_id
    ]
    st.rerun() 
@st.fragment
def choose_llm():
    os.environ['LANGCHAIN_API_KEY'] = st.text_input('Enter Langchain API key:', type='password')
    llms=st.multiselect("Choose your AI provider", options=["openai","vertexai","huggingface"],max_selections=1,default="huggingface")
    for options in llms:
        if options=="huggingface":
            os.environ["HUGGINGFACEHUB_API_TOKEN"] = st.text_input('Enter HuggingFace API key:', type='password')
        elif options=="openai":
            os.environ["OPENAI_API_KEY"]=st.text_input('Enter Openai API key:', type='password')
        elif options=="vertexai":
            os.environ["GOOGLE_API_KEY"]=st.text_input("Enter Vertexai API key:", type='password')
        else:
            pass
    os.environ["UNSTRUCTURED_API_KEY"]= st.text_input('Enter Unstructured API key(optional):', type='password',help="Useful for websites or PDF files containing images or illustrations")
    if not (os.environ.get('LANGCHAIN_API_KEY') and (os.environ.get("HUGGINGFACEHUB_API_TOKEN") or os.environ.get("OPENAI_API_KEY") or os.environ.get("GOOGLE_API_KEY"))):
        st.warning('Please enter your credentials!', icon='⚠️')
    else:
        st.success('Credentials verified. Proceed!', icon='👉')

def add_college_questions_to_vector_store(selected_colleges, full_data):
    """
    Add college supplemental questions to the vector store.
    """
    documents = [
        Document(page_content=question, metadata={"college": college})
        for college in selected_colleges
        if college in full_data
        for question in full_data[college]
    ]
    if documents:
        st.session_state.db.add_documents(documents)
        

@st.cache_data
def get_college_data(college,_sup):
    # Fetch data from Supabase
    response = _sup.table("college_questions").select("*").eq("college_name", college).execute()
    return [i for i in response.data]

# Function to dynamically add web loader inputs
def add_web_input():
    if len(st.session_state.web_inputs) < 2:
        st.session_state.web_inputs.append("")

# Function to dynamically add YouTube loader inputs
def add_youtube_input():
    if len(st.session_state.youtube_inputs) < 2:
        st.session_state.youtube_inputs.append("")

# Function to get colleges names
@st.cache_data
def get_college_name(_sup):
   response = _sup.table("college_questions").select("college_name").execute()
   all_values = [data for data in response.data]
   # Remove duplicates using a Python set
   unique_college_names = list({item['college_name'] for item in all_values})
   return unique_college_names

if "vector_stores" not in st.session_state:
    st.session_state.vector_stores = []
# Function to add questions to the vector store
def add_to_vector_store(college, essay_data):
    if college not in st.session_state:
        st.session_state.college = InMemoryVectorStore(embedding=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"))
    
    vector_store = st.session_state.college
    
    for row in essay_data:
        metadata = {
            "Essay Type": "Supplemental essays" if college != "Personal essay" else "Personal essays",
            "College": college if college != "Personal essay" else "All"
        }
        vector_store.add_texts([row["question"]], [metadata])
    print("yes sir")
    return vector_store

# Function to delete a vector store for a college
def delete_vector_store(college):
    if college in st.session_state:
        del st.session_state[college]