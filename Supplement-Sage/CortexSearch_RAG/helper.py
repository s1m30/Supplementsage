import streamlit as st
import json
from snowflake.snowpark import Session
from snowflake.core import Root # requires snowflake>=0.8.0
from snowflake.cortex import Complete
from langchain_community.document_loaders import WebBaseLoader
from snowflake.connector import connect
from langchain.text_splitter import RecursiveCharacterTextSplitter
### Default Values
NUM_CHUNKS = 3 # Num-chunks provided as context. Play with this to check how it affects your accuracy
slide_window = 7 # how many last conversations to remember. This is the slide window.

# service parameters
CORTEX_SEARCH_DATABASE = "CC_QUICKSTART_CORTEX_SEARCH_DOCS"
CORTEX_SEARCH_SCHEMA = "DATA"
CORTEX_SEARCH_SERVICE1 = "ESSAY_SEARCH"
CORTEX_SEARCH_SERVICE2= "SAGE_CHECKER"
######
######

# columns to query in the service
COLUMNS1 = [
    "question",
    "college_name"
] 
COLUMNS2=[
    "title",
    "content",
    "url"
]
def get_parameters(account, user, password,role="ACCOUNTADMIN",database="CC_QUICKSTART_CORTEX_SEARCH_DOCS"
                   ,warehouse="COMPUTE_WH",schema="DATA"):
    CONNECTION_PARAMETERS = {
        "account": account,
        "user": user,
        "password": password,
        "role": role,
        "database":database,
        "warehouse": warehouse,
        "schema": schema,
    }
    return CONNECTION_PARAMETERS
essay_prompts_session = Session.builder.configs(get_parameters(st.secrets["ACCOUNT"],st.secrets["USER"],st.secrets["PASSWORD"])).create()
# Ensure credentials are stored in st.session_state
    # Initialize chat history
if "account" not in st.session_state:
    st.session_state.account = ""
if "user" not in st.session_state:
    st.session_state.user = ""
if "password" not in st.session_state:
    st.session_state.password = ""
def upload_source():
    uploaded_file, website_url,save_sources = file_and_url_upload()
    if save_sources:
        if uploaded_file is not None:
            # Process uploaded file here (e.g., read content, upload to Snowflake)
            st.write("Uploaded File:", uploaded_file.name)
            st.sidebar.success("Sources saved and questions added to the vector store!")

        if website_url:
            try:
                # Process website URL here (e.g., load content using LangChain, extract data)
                st.write("Website URL:", website_url)
                process_url(website_url)
            except:
                st.warning("Input a valid url")
            st.sidebar.success("Sources saved and questions added to the vector store!")
    
def init_users_sources():
    with st.expander(label="Snowflake Account Credentials"):
        st.text_input("ACCOUNT",type="password",key="account")
        st.text_input("USER",type="password",key="user") 
        st.text_input("PASSWORD",type="password",key="password")
        st.text_input("ROLE",type="default",key="role",value="ACCOUNTADMIN")
        st.text_input("DATABASE",type="default",key="database",value="CC_QUICKSTART_CORTEX_SEARCH_DOCS") 
        st.text_input("WAREHOUSE",type="default",key="warehouse",value="COMPUTE_WH")
        st.text_input("SCHEMA",type="default",key="schema",value="DATA")
        
        params=[st.session_state.account, st.session_state.user, st.session_state.password,st.session_state.role,st.session_state.database,st.session_state.warehouse,st.session_state.schema]
        try:
            st.session_state.personal_sources_session = Session.builder.configs(
                get_parameters(*params)
            ).create()
            titles = st.session_state.personal_sources_session.table('website_data').select('title').distinct().collect()
            title_list = ["ALL"] + [title.TITLE for title in titles if title]
            title_list = list(filter(None, title_list))# Remove empty values
            st.sidebar.multiselect('Select the sources you would like to include', title_list, key="title_value",default="ALL")
            upload_source()
            st.success("Credentials Verified!!")
        except:
            st.warning("Please enter valid credentials.")


def cortex_config():
    essay_prompts = essay_prompts_session.table('Essay_Prompts').select('college_name').distinct().collect()
    col_name = [cat.COLLEGE_NAME for cat in essay_prompts if cat]
    col_name = list(filter(None, col_name))  # Remove empty values
    st.sidebar.selectbox('Select the essay prompts you wish to include', col_name, key="college_value")
    st.sidebar.selectbox("Do you want to include your personal sources",options=["No","Yes"],key="choice")
    if st.session_state.choice=="Yes":
        init_users_sources()
    else:
        pass
        
    
def make_search_service(session,search_service):
    root = Root(session)
    svc = root.databases[CORTEX_SEARCH_DATABASE].schemas[CORTEX_SEARCH_SCHEMA]
    return svc.cortex_search_services[search_service]
    
def get_similar_chunks_search_service(query):
    essay_prompts_service = make_search_service(essay_prompts_session, CORTEX_SEARCH_SERVICE1)
    filter_obj1 = {"@eq": {"college_name": st.session_state.college_value}}
    response1 = essay_prompts_service.search(query, COLUMNS1, filter=filter_obj1, limit=NUM_CHUNKS)
    response2 = []  # Default value

    if st.session_state.personal_sources_session: 
        personal_sources_service = make_search_service(st.session_state.personal_sources_session, CORTEX_SEARCH_SERVICE2)
        if st.session_state.title_value == "ALL":
            response2 = personal_sources_service.search(query, COLUMNS2, limit=NUM_CHUNKS)
        elif st.session_state.title_value:
            filter_obj2 = [{"@eq": {"title": source}} for source in st.session_state.title_value]
        response2 = personal_sources_service.search(query, COLUMNS2, filter={"@or": filter_obj2}, limit=NUM_CHUNKS)
    response = str(response1.results + (response2.results if response2 else []))
    print(response)
    return response


def get_chat_history():
#Get the history from the st.session_stage.messages according to the slide window parameter
    
    chat_history = []
    
    start_index = max(0, len(st.session_state.messages) - slide_window)
    for i in range (start_index , len(st.session_state.messages) -1):
         chat_history.append(st.session_state.messages[i])

    return chat_history

def summarize_question_with_history(chat_history, question):
# To get the right context, use the LLM to first summarize the previous conversation
# This will be used to get embeddings and find similar chunks in the docs for context

    prompt = f"""
        Based on the chat history below and the question, generate a query that extend the question
        with the chat history provided. The query should be in natual language. 
        Answer with only the query. Do not add any explanation.
        
        <chat_history>
        {str(chat_history)}
        </chat_history>
        <question>
        {question}
        </question>
        """
    print("This is the prompt",prompt)
    sumary = Complete('mistral-large', prompt)   

    # if st.session_state.debug:
    #     st.sidebar.text("Summary to be used to find similar chunks in the docs:")
    #     st.sidebar.caption(sumary)

    sumary = sumary.replace("'", "")

    return sumary

def create_prompt (myquestion):
    chat_history = get_chat_history()

    if chat_history != []: #There is chat_history, so not first question
        question_summary = summarize_question_with_history(chat_history, myquestion)
        prompt_context =  get_similar_chunks_search_service(question_summary)
    else:
        prompt_context = get_similar_chunks_search_service(myquestion) #First question when using history

  
    prompt = f"""
           You are an expert chat assistance that extracts information from the CONTEXT provided
           between <context> and </context> tags.
           You offer a chat experience considering the information included in the CHAT HISTORY
           provided between <chat_history> and </chat_history> tags..
           When ansering the question contained between <question> and </question> tags
           be concise and do not hallucinate. 
           If you don´t have the information just say so.
           
           Do not mention the CONTEXT used in your answer.
           Do not mention the CHAT HISTORY used in your asnwer.

           Only anwer the question if you can extract it from the CONTEXT provideed.
           
           <chat_history>
           {chat_history}
           </chat_history>
           <context>          
           {prompt_context}
           </context>
           <question>  
           {myquestion}
           </question>
           Answer: 
           """
    
    # json_data = json.loads(prompt_context)

    return prompt

def file_and_url_upload():
    """
    Creates a Streamlit sidebar with options to upload files and enter a website URL.

    Returns:
        tuple: A tuple containing the uploaded file and the entered URL.
    """

    st.sidebar.title("Upload Files and Enter URL")

    uploaded_file = st.sidebar.file_uploader("Upload File", type=["pdf"]) 
    website_url = st.sidebar.text_input("Enter Website URL")
    save_sources=st.sidebar.button("Save Sources")
    return uploaded_file, website_url,save_sources
def answer_question(myquestion):

    prompt =create_prompt (myquestion)
    try:
        response = Complete('mistral-large', prompt)
    except:
        response="Sorry Could not generate a response!!"   

    return response

def process_url(url):
    if url:
        try:
            params=[st.session_state.account, st.session_state.user, st.session_state.password,st.session_state.role,st.session_state.database,st.session_state.warehouse,st.session_state.schema]
            conn = connect(**get_parameters(*params))
            loader = WebBaseLoader(url)
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=100,
                separators=["\n\n\n", "\n\n", "\n", " "]
            )
            documents = text_splitter.split_text(loader.load())
            
            for docs in documents:
                metadata = {
                    "url": url,
                    "title": docs.metadata.get("title", "") if hasattr(docs, "metadata") else "",
                    "description": docs.metadata.get("description", "") if hasattr(docs, "metadata") else ""
                }

                data = [(metadata["url"], metadata["title"], metadata["description"], getattr(docs, "page_content", ""))]
                
                insert_query = """
                    INSERT INTO WEBSITE_DATA (url, title, description, content)
                    VALUES (%s, %s, %s, %s)
                """
                with conn.cursor() as cursor:
                    cursor.executemany(insert_query, data)
                conn.commit()

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter a valid URL.")
