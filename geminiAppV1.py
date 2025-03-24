import streamlit as st
from google import genai
from io import BytesIO

# Show title and description.
st.title("📄 Document question answering")
st.write(
    "Upload a document below and ask a question about it – Gemini will answer! "
    "To use this app, you need to provide your Gemini API key, which you can get from the Gemini platform."
)

# Ask user for their Gemini API key via `st.text_input`.
gemini_api_key = st.text_input("Gemini API Key", type="password")
if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:
    # Create a Gemini client.
    client = genai.Client(api_key=gemini_api_key)

    # Let the user upload a file via `st.file_uploader`.
    uploaded_file = st.file_uploader(
        "Upload a document (.txt, .md, .pdf, .docx)", type=("txt", "md", "pdf", "docx")
    )

    # Ask the user for a question via `st.text_area`.
    question = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )

    if uploaded_file and question:
        try:
            # Process the uploaded file and question.
            document = uploaded_file.read()

            # Handle different file types
            if uploaded_file.type == "application/pdf":
                # If the file is a PDF, extract text
                from PyPDF2 import PdfReader
                reader = PdfReader(BytesIO(document))  # Use BytesIO to wrap the bytes data
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                document = text

            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                # If the file is a DOCX (Word), extract text
                from docx import Document
                doc = Document(BytesIO(document))  # Use BytesIO to wrap the bytes data
                text = ""
                for para in doc.paragraphs:
                    text += para.text
                document = text

            # Prepare the contents to send to Gemini API.
            content = f"Here's a document: {document} \n\n---\n\n {question}"

            # Generate an answer using the Gemini API.
            response = client.models.generate_content(
                model="gemini-2.0-flash",  # Model name for Gemini
                contents=[{"parts": [{"text": content}]}]
            )

            # Access the first candidate and its text
            if response.candidates:
                answer = response.candidates[0].content.parts[0].text
                st.write(answer)
            else:
                st.error("No response from the model.")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
