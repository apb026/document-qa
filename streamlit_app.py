import streamlit as st
from openai import OpenAI
import pandas as pd
import fitz  # PyMuPDF for PDF handling
from io import StringIO

# Show title and description
st.title("📄 Document Question Answering")
st.write(
    "Upload multiple documents (TXT, MD, PDF, or Excel) below and ask a question about them. GPT will answer!"
    " To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys)."
)

# Ask user for their OpenAI API key via `st.text_input`.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Let the user upload multiple files via `st.file_uploader`.
    uploaded_files = st.file_uploader(
        "Upload documents (.txt, .md, .pdf, .xlsx)", type=("txt", "md", "pdf", "xlsx"), accept_multiple_files=True
    )

    # Ask the user for a question via `st.text_area`.
    question = st.text_area(
        "Now ask a question about the documents!", 
        placeholder="Can you give me a short summary?", 
        disabled=not uploaded_files
    )

    def extract_text_from_pdf(file):
        """Extract text from PDF files."""
        doc = fitz.open(file)
        text = ""
        for page in doc:
            text += page.get_text()
        return text

    def extract_text_from_excel(file):
        """Extract text from Excel files."""
        df = pd.read_excel(file)
        return df.to_string()

    def extract_text_from_txt_md(file):
        """Extract text from .txt or .md files."""
        return file.read().decode()

    if uploaded_files and question:
        document_text = ""

        for uploaded_file in uploaded_files:
            if uploaded_file.type == "application/pdf":
                # Process PDF file
                document_text += extract_text_from_pdf(uploaded_file)
            elif uploaded_file.type in ["text/plain", "text/markdown"]:
                # Process TXT or MD file
                document_text += extract_text_from_txt_md(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                # Process Excel file
                document_text += extract_text_from_excel(uploaded_file)

        # Prepare messages for the OpenAI API
        messages = [
            {
                "role": "user",
                "content": f"Here's the content from the documents: {document_text} \n\n---\n\n {question}",
            }
        ]

        # Generate an answer using the OpenAI API
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            stream=True,
        )

        # Stream the response to the app using `st.write_stream`
        st.write_stream(stream)
