from langchain_community.document_loaders import (
    TextLoader, PyPDFLoader, UnstructuredHTMLLoader, YoutubeLoader, WebBaseLoader,Docx2txtLoader
) 
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Any, Union
from tempfile import NamedTemporaryFile
import streamlit as st
import uuid
import requests
from langchain.schema import Document
from langchain.storage import InMemoryByteStore
from app_helper import get_youtube_metadata,clean_html,split_text,filter_chunks
from langchain.text_splitter import RecursiveCharacterTextSplitter

def process_html_with_loader(loader):
    documents = loader.load()
    processed_documents = []

    for doc in documents:
        cleaned_text = clean_html(doc.page_content)
        chunks = split_text(cleaned_text)
        filtered_chunks = filter_chunks(chunks)

        for chunk in filtered_chunks:
            processed_documents.append(Document(
                page_content=chunk,
                metadata=doc.metadata
            ))

    return processed_documents

# def download_html(url):
#     """
#     Downloads the HTML content of a webpage, saves it temporarily,
#     and passes the content to another function for processing.
#     """
#     try:
#         # Send a GET request to the URL
#         response = requests.get(url)
#         response.raise_for_status()  # Raise an error for bad HTTP responses

#         # Save the content temporarily
#         with NamedTemporaryFile(delete=False, suffix=".html") as temp_file:
#             temp_file.write(response.text.encode('utf-8'))
#             temp_file_path = temp_file.name

#         print(f"HTML file temporarily saved at: {temp_file_path}")

#         # Pass the content to the processing function
#         return temp_file_path

#     except requests.exceptions.RequestException as e:
#         print(f"An error occurred: {e}")
        

@st.fragment
def load_sources(doc: Dict[str, Union[List[Any], List[str]]], db,id,supabase):
    """
    Load documents grouped by type and process them.
    """
    loaders = {
        "txt": TextLoader,
        "pdf": PyPDFLoader,
        "web": WebBaseLoader, #UnstructuredHTMLLoader if os.environ["UNSTRUCTURED_API_KEY"] else WebBaseLoader,
        "youtube": YoutubeLoader,
        "docx": Docx2txtLoader,
    }
    for file_type, sources in doc.items():
        loader_class = loaders.get(file_type)
        if not loader_class:
            print(f"No loader available for type: {file_type}")
            continue

        for source in sources:
            if isinstance(source, str):  # For web and YouTube links
                loader = loader_class(source)
                if file_type == "youtube":
                    documents = loader.load()
                    metadata = get_youtube_metadata(source)
                else: # For web loader
                    documents=process_html_with_loader(loader)
                    print("processed_html: ",documents)
                    metadata = documents[0].metadata  # Keep web metadata as is

            else:  # For file uploads
                with NamedTemporaryFile(delete=False, suffix=f".{file_type}") as temp_file:
                    temp_file.write(source.getvalue())
                    loader = loader_class(temp_file.name)
                documents = loader.load()
                metadata = {"title": source.name, "type": file_type}

            # Add metadata to documents
            for doc in documents:
                doc.metadata.update(metadata)
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=50)
            splits = text_splitter.split_documents(documents)
            print("My freaking id:",id)
            # print("the freaking metadata", splits[0].metadata)
            new_doc_ids=[]
            for i in splits:
                gen_id = str(uuid.uuid4())  # Generate a random UUID
                new_doc_id = db.add_texts([i.page_content], user_id=id, id=gen_id)
                supabase.table("vector_store").update({"metadata":i.metadata}).eq("id",gen_id).execute()
                new_doc_ids.append(new_doc_id)

            # Save source details to session state
            st.session_state.saved_sources.append({"id": new_doc_ids, "name": metadata["title"], "type": file_type})
            st.session_state.doc_ids.extend(new_doc_ids)

@st.fragment
def group_sources(files: List, ytb_urls: str, web_urls: str) -> Dict[str, List]:
    """
    Group input sources into their respective types: text, PDF, YouTube, and web.
    """
    sources = {ext: [] for ext in ["txt", "pdf", "docx", "doc", "youtube", "web","jpg"]}
     # Add YouTube URLs
    for url in ytb_urls:
        if url.strip():
            # Parse the URL
            print("urlL",url)
            parsed_url = urlparse(url)

            # Extract query parameters
            query_params = parse_qs(parsed_url.query)

            # Get the value for 'v'
            video_id = query_params.get('v')[0]

            print("Video ID:", video_id)
            sources["youtube"].append(video_id)

    # Add Web URLs
    for url in web_urls:
        if url.strip():
            sources["web"].append(url)
    for file in files:
        file_type = file.name.split('.')[-1].lower()
        if file_type in sources:
            sources[file_type].append(file)
    return sources
