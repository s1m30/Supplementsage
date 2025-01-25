import streamlit as st
from langchain.schema import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import ChatOpenAI,OpenAI,OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings,ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler  
from langchain_community.retrievers import BM25Retriever

# Function to remove a source
@st.fragment
def remove_source(doc_id: str):
    # Remove the document by its unique ID from the vector store
    if isinstance(doc_id, list):
        doc_id = doc_id[0]  # Extract the ID from the list if necessary
    
    st.session_state.db.delete(ids=[doc_id])  # Ensure `ids` is a list

    # Update session state by removing the deleted document
    if doc_id in st.session_state.documents:
        del st.session_state.documents[doc_id]
    else:
        print(f"Document with ID {doc_id} not found in session state.")

    # Rebuild the BM25 retriever with updated documents
    if st.session_state.documents:
        # Flatten all document lists into a single list
        all_docs = [doc for docs in st.session_state.documents.values() for doc in docs]
        st.session_state.bm25_retriever = BM25Retriever.from_documents(all_docs)
    else:
        st.session_state.bm25_retriever = None  # Clear retriever if no documents are left

    # Update `saved_sources` to reflect the removal
    st.session_state.saved_sources = [
        source for source in st.session_state.saved_sources if doc_id not in source["id"]
    ]

    print("Remaining documents:", st.session_state.documents)
    print("Updated saved sources:", st.session_state.saved_sources)

    st.rerun() 

#Function to get college essay prompts
@st.cache_data
def get_college_data(college,_sup):
    # Fetch data from Supabase
    response = _sup.table("college_questions").select("*").eq("college_name", college).execute()
    return [i for i in response.data]

# Function to get colleges names
@st.cache_data
def get_college_name(_sup):
   response = _sup.table("college_questions").select("college_name").execute()
   all_values = [data for data in response.data]
   # Remove duplicates using a Python set
   unique_college_names = list({item['college_name'] for item in all_values})
   return unique_college_names

# Function to add questions to the vector store
def add_to_vector_store(college, essay_data):
    documents = [
        Document(page_content=college+"\n"+row["question"],  metadata = {
            "Essay Type": "Supplemental essays" if college != "Personal essay" else "Personal essays",
            "College": college if college != "Personal essay" else "All"
        })
        for row in essay_data
    ]
    if college not in st.session_state:
        st.session_state.college = InMemoryVectorStore.from_documents(documents=documents,embedding=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"))
    return st.session_state.college

# Function to delete a vector store for a college
def delete_vector_store(college):
    if college in st.session_state:
        if st.session_state[college] in st.session_state.dbs:
            st.session.dbs.remove(st.session_state[college] )
        del st.session_state[college]
        
@st.cache_resource  # Use cache_resource for objects that don't serialize well
def llm_getter(llm, repo_id=""):  # Make repo_id optional
    if llm == "huggingface":
        if repo_id=="":
            repo_id = "HuggingFaceH4/zephyr-7b-beta"
        hf1= HuggingFaceEndpoint(
            repo_id="HuggingFaceH4/zephyr-7b-beta",
            task="text-generation",
            max_new_tokens=1024,
            repetition_penalty=1.03,
            callbacks=[StreamingStdOutCallbackHandler()],
            streaming=True  
        )
        hf2=HuggingFaceEndpoint(
            repo_id=repo_id
        )
        return hf2,ChatHuggingFace(llm=hf1).bind(max_tokens=4096, temperature=0.0) # Return only the ChatHuggingFace object
    elif llm == "openai":
        return OpenAI(temperature=0.0),ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
    else:
        raise ValueError(f"Invalid llm: {llm}. Must be 'huggingface', 'openai.")

