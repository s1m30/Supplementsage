# 🧠 SupplementSage: Your AI-Powered College Essay Assistant 🎓

Supplement Sage is a web application designed to help students navigate the complexities of college applications. With AI-driven tools and personalized assistance, users can explore, organize, and refine their essays while integrating data from multiple sources.

---
![WhatsApp Image 2024-11-26 at 13 18 12](https://github.com/user-attachments/assets/e85d58af-4881-4322-b656-b6fa7e618366)

---

## 🌟 Features

- **User Authentication**: Secure login with personalized spaces for every user powered by Supabase authentication.
- **Vector Store Integration**: Advanced document handling using pgvector for fast and accurate retrieval of stored information.
- **Flexible Input Options**:
  - Upload files (TXT, PDF, DOCX, JPG).
  - Add YouTube links and website URLs for content analysis.
- **Essay Guidance**: 
  - Context-aware suggestions for crafting responses.
  - College-specific supplemental questions from a curated database.
- **Rich Visualizations**: Display insights using word clouds, bar charts, and other interactive Streamlit widgets.
- **Custom Sources**: Organize, save, and manage personal document collections with options to edit and delete.
- **Dynamic Retrieval-Augmented Generation (RAG)**:
  - Contextual question-answering from user documents.
  - Integrated embeddings with HuggingFace models.

---

## 🛠️ Technology Stack

- **Back-End**:
  - Python
  - Supabase (Postgres, pgvector, authentication)
  - LangChain (document loaders, RAG)
- **Front-End**:
  - Streamlit
- **Machine Learning**:
  - HuggingFace Embeddings
  - OCR.space for image-based text extraction
  - Keras-OCR (optional)
- **Deployment**:
  - Streamlit Community Cloud or Docker


## 🧩 Usage

1. **Login**: Authenticate using your email/password via Supabase.
2. **Upload Sources**: Upload files or enter URLs for analysis.
3. **Add Questions**: Select colleges and add supplemental essay questions to the vector store.

---

## 🎯 Future Features

- **Grammar and Style Feedback**: AI-powered suggestions to improve tone and structure.
- **Collaboration Tools**: Real-time peer review functionality.
- **Gamified Writing Challenges**: Motivate students with streaks and leaderboards.
- **Custom Analytics**: Insights into word usage, themes, and essay trends.

---

## 🌟 Acknowledgments

- [Streamlit](https://streamlit.io/) for its amazing UI capabilities.
- [LangChain](https://langchain.com/) for powering the AI workflows.
- [Supabase](https://supabase.io/) for robust database and authentication.
- The college admissions community for inspiration.

--- 