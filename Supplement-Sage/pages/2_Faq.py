import streamlit as st 
import langchain_RAG.app_component as au

st.set_page_config(
    page_title="SupplementSage - FAQ",
    page_icon="https://api.dicebear.com/5.x/bottts-neutral/svg?seed=gptLAb",
    menu_items={
        "About": "SupplementSage is a user-friendly app that empowers students to write outstanding supplemental essays by providing tailored insights and school-specific information. Our mission is to simplify the essay-writing process, making it efficient and accessible.",
        "Get help": None,
        "Report a Bug": None,
    }
)

st.markdown(
    "<style>#MainMenu{visibility:hidden;}</style>",
    unsafe_allow_html=True
)

# au.render_cta()

st.title("FAQ")

with st.expander("What is SupplementSage?", expanded=False):
    st.markdown(
        "SupplementSage is a cutting-edge tool designed for college applicants. It assists students in writing supplemental essays by extracting relevant information about schools and tailoring content to fit specific requirements. The app is intuitive and optimized to enhance your writing experience."
    )

with st.expander("Why SupplementSage?"):
    st.markdown(
        "SupplementSage was built with you, the college aspirant, in mind. We believe every student should have access to tools that help them present their best selves to admissions officers. SupplementSage optimizes essay writing and empowers you to craft compelling narratives."
    )

with st.expander("What features are available?"):
    st.markdown(
        "You have access to all of SupplementSage's features, which are designed to meet your needs during the essay-writing process. While its primary focus is on supplemental essays, the app can serve various other purposes as well. For detailed guidance, refer to the [walkthrough](#)."
    )

with st.expander("Which AI providers can I use?"):
    st.markdown(
        "SupplementSage supports multiple AI providers, including Hugging Face, OpenAI, and Vertex AI. You can obtain API keys for these providers through their respective platforms."
    )

with st.expander("What is a LangChain API Key, and why do I need it?"):
    st.markdown(
        "A LangChain API key is a unique credential that allows the app to integrate with LangChain's framework to extract insights from your documents and enhance your essay-writing experience."
    )

with st.expander("Why do I need to enter my LangChain and AI provider API keys each time I use the app?"):
    st.markdown(
        "For security reasons, we do not store your actual LangChain and AI provider API keys on our servers. During your session, the app uses these keys to interact with AI services. To maintain confidentiality, we use a secure one-way hashing algorithm to store a hashed version of your API key, which serves as your unique identifier in our backend."
    )

with st.expander("Does SupplementSage cost money?"):
    st.markdown(
        "Currently, SupplementSage is free to use. However, interacting with AI models like OpenAI GPT may incur charges depending on the API provider. Costs are typically minimal under normal usage, as you control the API calls made through your personal key. You can monitor and manage these costs on the provider's dashboard."
    )

with st.expander("Why am I seeing the error 'You exceeded your current quota, please check your plan and billing details'?"):
    st.markdown(
        "This error indicates that you have hit your API usage limit or the maximum monthly spending cap set on your account. If you're using a free trial API key, this could also be the reason. For uninterrupted usage, consider upgrading to a pay-as-you-go API plan and entering your billing information [here](https://platform.openai.com/account/billing/overview). Learn more about OpenAI API rate limits [here](https://platform.openai.com/docs/guides/rate-limits/overview)."
    )

with st.expander("Is my information kept confidential on SupplementSage?"):
    st.markdown(
        "Yes, your privacy is our priority. We do not store personally identifiable information. Uploaded documents are secured with Row Level Security to ensure only you can access them. If you wish to delete specific information, you can use the 'Remove' button in the sidebar. Additionally, session transcripts are encrypted to maintain confidentiality."
    )

au.render_cta()    