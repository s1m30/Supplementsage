import streamlit as st 
import os
import base64
from streamlit_option_menu import option_menu
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# st.set_page_config(
#     page_title="Hello",
#     page_icon="👋",
# )

st.write("# Welcome to SupplementSage! 👋")

def get_img_as_base64(file):
  with open(file, "rb") as f:
      data = f.read()
  return base64.b64encode(data).decode()

# Get the current working directory
current_directory = os.getcwd()
img = get_img_as_base64(os.path.join(current_directory+"Supplement-Sage","background.jpg"))

def add_bg_from_url():
    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"]>div:first-child{{
            background-image: url("data:image/png;base64,{img}");
            background-position: center;
            background-repeat: no-repeat;
            background-color: rgba(0, 0, 0, 0.9);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

add_bg_from_url()

# About page content
st.markdown(
    f"""
     <style>
        [data-testid="stAppViewContainer"]>div:first-child{{
            background-image: url("data:image/png;base64,{img}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
        }}
    </style>
    # SupplementSage 📝✨
    
    Welcome to **SupplementSage**, your AI-powered ally in simplifying the college application process!  
    Whether you're brainstorming ideas, researching schools, or refining your supplemental essays, SupplementSage is here to make the process smarter, faster, and easier.  
    
    ## Why Choose SupplementSage? 🌟
    - **Streamlined School Research**  
      Automatically fetch and analyze school-specific essay prompts and requirements to save you hours of manual work.
    - **Personalized Feedback**  
      Upload essay prompts, links, or documents to receive tailored suggestions and insights based on your unique needs.
    - **RAG Technology**  
      Leverage Retrieval-Augmented Generation to integrate data from videos, files, websites, and a supplemental essay database into your writing process.
    - **Export Features**  
      Easily export recommendations and insights as professional PDFs for offline use.

    ## Features at a Glance 🔍
    - **Comprehensive Support:** From researching schools to refining essays.  
    - **User-Friendly Design:** Accessible to anyone, regardless of technical expertise.  
    - **Versatile Data Input:** Supports links, documents, and multimedia for flexible usage.

    ## Ready to Start? 🚀
    - Upload your materials to begin your journey toward creating standout essays.  
    - Let SupplementSage handle the heavy lifting while you focus on telling your story.

    ---
    
    **Need Help or Have Feedback?** Reach out to us anytime for support and suggestions!  
    """, 
    unsafe_allow_html=True
)

# # Contact form functionality
# st.markdown("---")
# st.markdown("## Contact Us 📩")

# with st.form(key="contact_form"):
#     name = st.text_input("Your Name", placeholder="Enter your name")
#     email = st.text_input("Your Email", placeholder="Enter your email")
#     message = st.text_area("Message", placeholder="Write your message here...")
#     submit_button = st.form_submit_button("Send Message")

#     if submit_button:
#         if name and email and message:
#             # Email configuration
#             sender_email = "your_email@example.com"  # Replace with your email
#             receiver_email = "your_email@example.com"  # Replace with your email
#             subject = f"New Message from {name} via SupplementSage"

#             # Create the email message
#             msg = MIMEMultipart()
#             msg["From"] = sender_email
#             msg["To"] = receiver_email
#             msg["Subject"] = subject
#             msg.attach(MIMEText(f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}", "plain"))

#             try:
#                 # Set up the server (example with Gmail's SMTP server)
#                 with smtplib.SMTP("smtp.gmail.com", 587) as server:
#                     server.starttls()
#                     server.login(sender_email, "your_email_password")  # Replace with your email password
#                     server.send_message(msg)

#                 st.success("Your message has been sent successfully!")
#             except Exception as e:
#                 st.error(f"Failed to send your message. Error: {e}")
#         else:
#             st.error("Please fill in all the fields before submitting.")
