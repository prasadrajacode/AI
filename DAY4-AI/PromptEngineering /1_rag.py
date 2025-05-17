import streamlit as st
import os, getpass
from dotenv import load_dotenv
from io import StringIO
#from langchain.document_loaders import TextLoader
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ibm import WatsonxLLM, WatsonxEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods

# Ensure directory exists for uploaded files
UPLOAD_DIR = "./uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Load environment variables from .env file
load_dotenv()

# Retrieve credentials
project_id = "a15722af-476f-4ad2-ad25-090750dd14e2"
credentials = {
    "url": "https://us-south.ml.cloud.ibm.com",
    "apikey": "Nt8BVcy9pRD8bDngmalyAujN02hPV7PsuJu6bpUr6zxN"
}


#filename = 'india_2.txt'

uploaded_file = st.file_uploader("Upload a text file", type=["txt"])

if uploaded_file:
    # Read file content from memory (no need to save it)
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    file_content = stringio.read()

    st.success(f"File '{uploaded_file.name}' uploaded successfully!")

    # Save file content to a temporary file (needed for TextLoader)
    temp_path = f"./uploaded_files/{uploaded_file.name}"
    os.makedirs("./uploaded_files", exist_ok=True)  # Ensure directory exists

    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(file_content)

    loader = TextLoader(temp_path)
    documents = loader.load()

    #text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(documents)

    # Load Watsonx Embeddings
    embeddings = WatsonxEmbeddings(
        model_id="ibm/slate-30m-english-rtrvr",
        url=credentials["url"],
        apikey=credentials["apikey"],
        project_id=project_id
    )

    # Load ChromaDB
    vectorstore = Chroma.from_documents(split_docs, embeddings)

    # Create Retriever
    retriever=vectorstore.as_retriever()

    model_id = "ibm/granite-13b-instruct-v2"

    parameters = {
        GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
        GenParams.MIN_NEW_TOKENS: 1,
        GenParams.MAX_NEW_TOKENS: 100,
        GenParams.STOP_SEQUENCES: ["<|endoftext|>"]
    }

    # Load Watsonx Granite LLM
    watsonx_granite = WatsonxLLM(
        model_id=model_id,
        url=credentials.get("url"),
        apikey=credentials.get("apikey"),
        project_id=project_id,
        params=parameters
    )

    # Set Up RetrievalQA Chain
    qa_chain = RetrievalQA.from_chain_type(llm=watsonx_granite, chain_type="stuff", retriever=retriever)

    # Streamlit UI
    st.title("RAG - Chroma and Langchain")
    st.write("Ask any question based on the documents stored in ChromaDB.")

    # User Input
    user_question = st.text_input("Enter your question:")

    if st.button("Get Answer"):
        if user_question:
            with st.spinner("Fetching answer..."):
                response = qa_chain.invoke(user_question)
            st.success("Answer:")
            st.write(response)
        else:
            st.warning("Please enter a question!")

