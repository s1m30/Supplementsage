from langchain_community.document_loaders import (
    TextLoader, PyPDFLoader, YoutubeLoader, WebBaseLoader,Docx2txtLoader
) 
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Any, Union
from tempfile import NamedTemporaryFile
import streamlit as st
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.retrievers import BM25Retriever
from bs4 import BeautifulSoup
import requests

def clean_html(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["nav", "footer", "script", "style"]):
        tag.decompose()
    return soup.get_text(separator="\n", strip=True)

def process_html_with_loader(loader):
    documents = loader.load()
    processed_documents = []

    for doc in documents:
        cleaned_text = clean_html(doc.page_content)
        text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n\n","\n\n", "\n", " "]
    )
        chunks = text_splitter.split_text(cleaned_text)
        filtered_chunks = [
        chunk for chunk in chunks
        if 50 < len(chunk.strip()) < 2000
        and not chunk.isspace()
    ]
        #Functions for Loading HTML Sources
        for chunk in filtered_chunks:
            processed_documents.append(Document(
                page_content=chunk,
                metadata=doc.metadata
            ))

    return processed_documents

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


@st.fragment
def load_sources(doc: Dict[str, Union[List[Any], List[str]]], db, bmdocs):
    """
    Load documents grouped by type and process them.
    """
    loaders = {
        "txt": TextLoader,
        "pdf": PyPDFLoader,
        "web": WebBaseLoader,
        "youtube": YoutubeLoader,
        "docx": Docx2txtLoader,
    }

    for file_type, sources in doc.items():
        loader_class = loaders.get(file_type)
        if not loader_class:
            print(f"No loader available for type: {file_type}")
            continue

        for source in sources:
            # Initialize document metadata and load content
            if isinstance(source, str):  # For web and YouTube links
                loader = loader_class(source)
                if file_type == "youtube":
                    documents = loader.load()
                    metadata = get_youtube_metadata(source)
                else:  # For web loader
                    documents = process_html_with_loader(loader)
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

            # Split documents into smaller chunks
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=50)
            splits = text_splitter.split_documents(documents)
            print("Document splits:", splits)

            # Save document splits and get unique IDs
            new_doc_ids = db.add_documents(splits)
            print("Added document IDs:", new_doc_ids)

            # Update `bmdocs` and session state with new documents
            bmdocs[new_doc_ids[0]] = splits
            st.session_state.documents[new_doc_ids[0]] = splits

            # Rebuild BM25 retriever
            all_docs = [doc for docs in bmdocs.values() for doc in docs]
            st.session_state.bm25_retriever = BM25Retriever.from_documents(all_docs)

            # Save source details to session state
            st.session_state.saved_sources.append({
                "id": new_doc_ids[0],  # Store single ID
                "name": metadata["title"],
                "type": file_type,
            })

    print("Final documents in session state:", st.session_state.documents)
    print("Updated saved sources:", st.session_state.saved_sources)

            
@st.fragment
def group_sources(files: List, ytb_urls: str, web_urls: str) -> Dict[str, List]:
    """
    Group input sources into their respective types: text, PDF, YouTube, and web.
    """
    sources = {ext: [] for ext in ["txt", "pdf", "docx", "doc", "youtube", "web","jpg"]}
     # Add YouTube URLs

    if ytb_urls.strip():
        # Parse the URL
        print("urlL",ytb_urls)
        parsed_url = urlparse(ytb_urls)

        # Extract query parameters
        query_params = parse_qs(parsed_url.query)

        # Get the value for 'v'
        video_id = query_params.get('v')[0]

        print("Video ID:", video_id)
        sources["youtube"].append(video_id)

    # Add Web URLs
    if web_urls.strip():
        sources["web"].append(web_urls)
    for file in files:
        file_type = file.name.split('.')[-1].lower()
        if file_type in sources:
            sources[file_type].append(file)
    return sources
