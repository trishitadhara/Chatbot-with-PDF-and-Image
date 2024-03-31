from openai import OpenAI
import streamlit as st
from PIL import Image
import pytesseract
import PyPDF2


st.title("The New GPT!!")

if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How can I help?"}]
# Display the existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def extract_text_from_pdf(uploaded_pdf):
    with st.spinner("Extracting text from PDF..."):
        pdf_reader = PyPDF2.PdfReader(uploaded_pdf)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
    return text

def extract_text_from_image(uploaded_image):
    with st.spinner("Extracting text from image..."):
        image = Image.open(uploaded_image)
        text = pytesseract.image_to_string(image)
    return text



# User input for chat
if prompt := st.text_input("You:", key="chat_input"):
    st.session_state.messages.append({"role": "user", "content": prompt})

# User uploads a document
uploaded_document = st.file_uploader("Upload a document:", type=["pdf"])




# If the last message is not from the assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant" and (prompt or uploaded_document or uploaded_image):
    # Process document if uploaded
    document_text = ""
    if uploaded_document:
        try:
            document_text = extract_text_from_pdf(uploaded_document)
        except Exception as e:
            st.error(f"Error extracting text from document: {e}")
    image_text = ""
    if uploaded_image:
        try:
            image_text = extract_text_from_image(uploaded_image)
        except Exception as e:
            st.error(f"Error extracting text from image: {e}")


    # Combine document and image text
    extracted_text = f"{document_text}\n{image_text}" if document_text or image_text else ""
    if st.session_state.messages[-1]["role"] != "assistant":
    # Call LLM
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                r = OpenAI().chat.completions.create(
                    messages=[{"role": m["role"], "content": m["content"]+extracted_text} for m in st.session_state.messages],
                    model="gpt-3.5-turbo",
                )
                response = r.choices[0].message.content
                st.write(response)

        # Update session state with the assistant's message
        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message)
