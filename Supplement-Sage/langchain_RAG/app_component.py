import streamlit as st
import streamlit.components.v1 as c 
import os
from .app_loader import group_sources, load_sources
from .app_helper import *
from supabase import create_client, Client
 
#@st.cache(show_spinner=False, suppress_st_warning=True,ttl=600)
def robo_avatar_component():

    robo_html = "<div style='display: flex; flex-wrap: wrap; justify-content: left;'>"
    robo_avatar_seed = [0, 'aRoN', 'gptLAb', 180, 'nORa', 'dAVe', 'Julia', 'WEldO', 60]

    for i in range(1, 10):
        avatar_url = "https://api.dicebear.com/5.x/bottts-neutral/svg?seed={0}".format(robo_avatar_seed[i-1])#format((i)*r.randint(0,888))
        robo_html += "<img src='{0}' style='width: {1}px; height: {1}px; margin: 10px;'>".format(avatar_url, 50)
    robo_html += "</div>"

    robo_html = """<style>
          @media (max-width: 800px) {
            img {
              max-width: calc((100% - 60px) / 6);
              height: auto;
              margin: 0 10px 10px 0;
            }
          }
        </style>""" + robo_html
    
    c.html(robo_html, height=70)


def st_button(url, label, font_awesome_icon):
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">', unsafe_allow_html=True)
    button_code = f'''<a href="{url}" target=_blank><i class="fa {font_awesome_icon}"></i>   {label}</a>'''
    return st.markdown(button_code, unsafe_allow_html=True)

#Authentication Setup
supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

#Session States Initialization
def init_states():
    # Initialize session state for saved sources
    if "saved_sources" not in st.session_state:
        st.session_state.saved_sources = []
    if "dbs" not in st.session_state:
        st.session_state.dbs=[]
    if "documents" not in st.session_state:
        st.session_state.documents ={}  # Initialize document dictionary
        st.session_state.bm25_retriever = None


def langchain_config():
    llm=choose_llm()
    init_states()
    upload_view_delete(supabase)
    st.session_state.embedding= OpenAIEmbeddings() if llm=="openai" else HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    #Initialize db session_state
    if "db" not in st.session_state:
        st.session_state.db=InMemoryVectorStore(embedding=st.session_state.embedding)

def render_cta():
  with st.sidebar:
      st.write("Let's connect!")
      st_button(url="https://www.linkedin.com/in/simeon-adebola-050079263/", label="Twitter", font_awesome_icon="fa-twitter")
      st_button(url="https://www.linkedin.com/in/simeon-adebola-050079263/", label="LinkedIn", font_awesome_icon="fa-linkedin")


#Sidebar Component for choosing LLM based on A.I. provider
@st.fragment
def choose_llm():
    #Save Langchain key in session_State and Os environment
    os.environ['LANGCHAIN_API_KEY'] = st.text_input('Enter Langchain API key:', type='password')
    #Save A.I. Provider key in session_State and Os environment
    llm=st.selectbox("Choose your AI provider", options=["huggingface","openai"],key="llm")
    if llm=="huggingface":
        os.environ["HUGGINGFACEHUB_API_TOKEN"]=st.text_input('Enter HuggingFace API key:', type='password')
        st.session_state.repo_id=st.text_input("Enter a repo_id(Opt)")
    else:
        os.environ["OPENAI_API_KEY"]=st.text_input('Enter Openai API key:', type='password')
    if not (os.environ.get('LANGCHAIN_API_KEY') and (os.environ.get("HUGGINGFACEHUB_API_TOKEN") or os.environ.get("OPENAI_API_KEY"))):
        st.warning('Please enter your credentials!', icon='⚠️')
    else:
        st.success('Credentials verified. Proceed!', icon='👉')
        return llm

#Sidebar Component to upload documents, view sources and delete them
def upload_view_delete(supabase):
  st.title("Sources")
  files,ytb,web=handle_file_uploads()
  st.divider()
  handle_essay_prompts(supabase)
  st.divider()
  view_and_delete_sources(files,ytb,web)


#For User's Documents
def handle_file_uploads():
  files = st.file_uploader("Upload files", accept_multiple_files=True, type=["txt", "pdf", "docx"])
  # Prepare inputs for grouping
  # Base web and YouTube inputs
  web_url = st.text_input("Web Loader URL (default)")
  ytb_url = st.text_input("YouTube Loader URL (default)")
  
  return files, ytb_url, web_url
  #For College essay prompts

#For handling essay prompts
@st.fragment
def handle_essay_prompts(supabase):
  # Fetch data for Colleges
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
  
  with st.expander(label="College Essay Prompts",expanded=False):
    for college in selected_colleges:
        st.subheader(college)
        st.session_state.essay_data=get_college_data(college,supabase)
        
        # Display questions and add to vector store
        st.session_state.dbs.append(add_to_vector_store(college, st.session_state.essay_data))
        for row in st.session_state.essay_data:
            st.write(row["question"])
        st.divider()

#For viewing and deleting documents sources
@st.fragment
def view_and_delete_sources(files, all_ytb_urls,all_web_urls):
  if st.button("Save Sources"):
      grouped_sources = group_sources(files, all_ytb_urls, all_web_urls)
      if grouped_sources:
          with st.spinner("File Upload underway..."):
            load_sources(grouped_sources,st.session_state.db,st.session_state.documents)
      st.success("Sources saved and questions added to the vector store!")
 
  # Display saved sources in an expander
  with st.expander("Saved Sources", expanded=True):
      for source in st.session_state.saved_sources:
          col1, col2 = st.columns([3, 2])  # Create columns for source name and cancel button
          with col1:
              st.text(f"{source['name']}")  # Display source name and type
          with col2:
              if st.button(f"Remove", key=source["id"]):
                  remove_source(source["id"])  # Remove source when cancel button is clicked