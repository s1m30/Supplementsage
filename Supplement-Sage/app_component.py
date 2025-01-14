import streamlit as st
import streamlit.components.v1 as c 
import os
from app_loader import group_sources, load_sources
from app_helper import add_to_vector_store, delete_vector_store
from app_helper import add_web_input, add_youtube_input, get_college_data, remove_source, get_college_name

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
    llms=st.multiselect("Choose your AI provider", options=["openai","huggingface"],max_selections=1,default="huggingface")
    for options in llms:
        if options=="huggingface":
            # col1,col2=st.columns(2)
            os.environ["HUGGINGFACEHUB_API_TOKEN"]=st.text_input('Enter HuggingFace API key:', type='password')
            st.session_state.repo_id=st.text_input("Enter a repo_id(Opt)")
        elif options=="openai":
            os.environ["OPENAI_API_KEY"]=st.text_input('Enter Openai API key:', type='password')
        # elif options=="vertexai":
        #     os.environ["GOOGLE_API_KEY"]=st.text_input('Enter VertexAI API key:', type='password')
        #     continue
    # os.environ["UNSTRUCTURED_API_KEY"]= st.text_input('Enter Unstructured API key(optional):', type='password',help="Useful for websites or PDF files containing images or illustrations")
    if not (os.environ.get('LANGCHAIN_API_KEY') and (os.environ.get("HUGGINGFACEHUB_API_TOKEN") or os.environ.get("OPENAI_API_KEY"))):
        st.warning('Please enter your credentials!', icon='⚠️')
    else:
        st.success('Credentials verified. Proceed!', icon='👉')
        return llms[0]

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

  # Buttons to add more inputs
  if st.button("Add another Web Loader URL"):
      add_web_input()

  if st.button("Add another YouTube Loader URL"):
      add_youtube_input()

  # Display additional inputs for Web Loader
  for i, value in enumerate(st.session_state.web_inputs):
      st.session_state.web_inputs[i] = st.text_input(f"Additional Web Loader URL {i+1}", value=value)

  # Display additional inputs for YouTube Loader
  for i, value in enumerate(st.session_state.youtube_inputs):
      st.session_state.youtube_inputs[i] = st.text_input(f"Additional YouTube Loader URL {i+1}", value=value)
  all_web_urls = [web_url] + st.session_state.web_inputs
  all_ytb_urls = [ytb_url] + st.session_state.youtube_inputs
  return files, all_ytb_urls, all_web_urls
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