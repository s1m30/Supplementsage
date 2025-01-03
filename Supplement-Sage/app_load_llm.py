from langchain_huggingface import HuggingFaceEmbeddings,ChatHuggingFace, HuggingFaceEndpoint
from langchain_core.callbacks.streaming_stdout import StreamingStdOutCallbackHandler  
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers import EnsembleRetriever

def get_response(query, chat_history,db,memorydbs):
    ### Contextualize question ###
    contextualize_q_system_prompt = """Given a chat history and the latest user question
    which might reference context in the chat history, formulate a standalone question 
    which can be understood without the chat history. Do NOT answer the question,
    just reformulate it if needed and otherwise return it as is."""
    llm = HuggingFaceEndpoint(
        repo_id="HuggingFaceH4/zephyr-7b-beta",
        task="text-generation",
        max_new_tokens=1024,
        repetition_penalty=1.03,
        streaming=True,
        callbacks= [StreamingStdOutCallbackHandler()],     
    )   
    
    # chat_model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)
    chat_model=ChatHuggingFace(llm=llm).bind(max_tokens=8192, temperature=0.0)
    # pretty_print_docs(compressed_docs)
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
       # Combine retrievers into an ensemble retriever
    print("memories",memorydbs)
    print("dbretrieve",db.as_retriever())
    ensemble_retriever = EnsembleRetriever(retrievers=[i.as_retriever() for i in memorydbs] + [db.as_retriever()])
    

    # print(ensemble_retriever.get_relevant_documents(chat_model.invoke(contextualize_q_prompt.format_messages(input=query))))
    history_aware_retriever = create_history_aware_retriever(
        chat_model, ensemble_retriever, contextualize_q_prompt
    )
    
    ### Answer question ### 
    qa_system_prompt = """You are a college essay guide for question-answering tasks. 
    Use the following pieces of retrieved context to answer the question. 
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
