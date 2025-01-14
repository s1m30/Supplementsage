from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.retrievers import EnsembleRetriever,ContextualCompressionRetriever
import streamlit as st
from app_helper import llm_getter
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.retrievers.document_compressors import LLMChainFilter,EmbeddingsFilter
from langchain_huggingface import HuggingFaceEmbeddings

# Combine retrievers into an ensemble retriever     
@st.fragment   
def get_response(query, chat_history,db,memorydbs,llm,repo_id):
    ### Contextualize question ###
    contextualize_q_system_prompt = f"""Given a chat history and the latest user question
    which might reference context in the chat history, formulate a standalone question 
    which can be understood without the chat history. 
    Do NOT answer the question,
    just reformulate it if needed and otherwise return it as is."""
    hf,chat_model=llm_getter(llm,repo_id)
    
    # pretty_print_docs(compressed_docs)
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    try:
        ensemble_retriever = EnsembleRetriever(retrievers=[i.as_retriever() for i in memorydbs]+ [db.as_retriever()]+[st.session_state.bm25_retriever])
    except:
        ensemble_retriever = EnsembleRetriever(retrievers=[i.as_retriever() for i in memorydbs]+ [db.as_retriever()])     
    try:
        _filter = LLMChainFilter.from_llm(hf)
        compressor_retriever = ContextualCompressionRetriever(
            base_compressor=_filter, base_retriever=ensemble_retriever
        )
        history_aware_retriever = create_history_aware_retriever(
            hf, compressor_retriever, contextualize_q_prompt
        )
        print("Compressor retriever used")
    except:
        history_aware_retriever = create_history_aware_retriever(
            hf, ensemble_retriever, contextualize_q_prompt
        )
        print("Not used")

    ### Answer question ### 
    qa_system_prompt = """You are a college essay guide.
    Use the following pieces of retrieved context to respond to the user appropriately answer the question. 
    If you don't know the answer, just say that you don't know. 
    {context}"""

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm=chat_model, prompt=qa_prompt)

    rag_chain = create_retrieval_chain( history_aware_retriever,question_answer_chain).pick("answer")
    return rag_chain.stream({"input":query,"chat_history":chat_history})
