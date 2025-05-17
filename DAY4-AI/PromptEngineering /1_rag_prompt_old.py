import streamlit as st
import os
from dotenv import load_dotenv
from io import StringIO
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ibm import WatsonxLLM, WatsonxEmbeddings
from chromadb import Client
from langchain_community.vectorstores import Chroma
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import DecodingMethods

# Load environment variables
load_dotenv()

# Setup Watsonx credentials
project_id = "a15722af-476f-4ad2-ad25-090750dd14e2"
credentials = {
    "url": "https://us-south.ml.cloud.ibm.com",
    "apikey": "Nt8BVcy9pRD8bDngmalyAujN02hPV7PsuJu6bpUr6zxN"
}

# Watsonx generation params
generation_params = {
    GenParams.DECODING_METHOD: DecodingMethods.GREEDY,
    GenParams.MIN_NEW_TOKENS: 1,
    GenParams.MAX_NEW_TOKENS: 100,
    GenParams.STOP_SEQUENCES: ["<|endoftext|>"]
}

# Load LLM model once
llm_model = WatsonxLLM(
    model_id="ibm/granite-13b-instruct-v2",
    url=credentials["url"],
    apikey=credentials["apikey"],
    project_id=project_id,
    params=generation_params
)

# Create Chroma client
client = Client()

# Set up the collection where we will store the document chunks
def create_chroma_collection(collection_name):
    if collection_name in client.list_collections():
        collection = client.get_collection(collection_name)
        # Clear existing documents before inserting new ones
        collection.delete(where={"$exists": True})  # Delete all documents
        return collection
    else:
        collection = client.create_collection(collection_name)
        return collection


# Function to upsert the chunks into the Chroma collection
def upsert_to_chroma(collection, split_docs):
    documents = []
    metadatas = []
    ids = []
    
    for i, doc in enumerate(split_docs):
        documents.append(doc.page_content)
        metadatas.append({"source": doc.metadata.get("source", "unknown")})
        ids.append(f"chunk_{i}")
    
    # Upsert documents into the collection
    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    return collection

# Modular functions for document loading, splitting, and vector store setup
def load_and_split_document(file_path):
    loader = TextLoader(file_path)
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(documents)

 # Create the embeddings object for the collection
embeddings = WatsonxEmbeddings(
        model_id="ibm/slate-30m-english-rtrvr",
        url=credentials["url"],
        apikey=credentials["apikey"],
        project_id=project_id
    )
def setup_vectorstore_with_chroma(split_docs, collection_name="document_collection"):
    # Create Chroma collection or get existing one
    collection = create_chroma_collection(collection_name)

    # Upsert the split document chunks to the collection
    collection = upsert_to_chroma(collection, split_docs)
    
    # Create a Chroma vector store from the collection
    vectorstore = Chroma(client=client, collection_name=collection_name, embedding_function=embeddings)

    return vectorstore

def retrieve_relevant_chunks(question, retriever):
    
    # Embed the question to get its vector representation
    
    #question_embedding = embeddings.embed_documents([question])[0]
    #question_embedding = embeddings.embed_query(question)
    #print(question_embedding)
    
    # Retrieve relevant documents based on the question embedding
    relevant_chunks = retriever.get_relevant_documents(query=question)
    
    
    return relevant_chunks


def build_prompt(chunks, question):
    context = "\n\n".join([chunk.page_content for chunk in chunks])
    return f"""You are a helpful assistant. Use the following context to answer the question.

        Context:
        {context}

        Question:
        {question}

        Answer:"""

def generate_with_watsonx(prompt):
    return llm_model.invoke(prompt)

# Streamlit UI
st.title("RAG - Watsonx + Chroma + LangChain")
st.write("Upload a `.txt` file and ask questions based on its content.")

uploaded_file = st.file_uploader("Upload a text file", type=["txt"])

if uploaded_file:
    upload_dir = "./uploaded_files"
    os.makedirs(upload_dir, exist_ok=True)

    # Delete previous files
    for filename in os.listdir(upload_dir):
        file_path = os.path.join(upload_dir, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Save new uploaded file
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
    file_content = stringio.read()

    temp_path = os.path.join(upload_dir, uploaded_file.name)
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(file_content)

    st.success(f"File '{uploaded_file.name}' uploaded and processed!")

    # Load and split the document, then create vector store
    with st.spinner("Processing file and creating vector store..."):
        split_docs = load_and_split_document(temp_path)
        vectorstore = setup_vectorstore_with_chroma(split_docs)
        retriever = vectorstore.as_retriever()

    # Question input
    user_question = st.text_input("Enter your question:")

    if st.button("Get Answer"):
        if user_question.strip() != "":
            with st.spinner("Fetching answer..."):
                relevant_chunks = retrieve_relevant_chunks(user_question, retriever)
                rag_prompt = build_prompt(relevant_chunks, user_question)
                st.write(rag_prompt)
                final_answer = generate_with_watsonx(rag_prompt)

            st.success("Answer:")
            st.write(final_answer)
        else:
            st.warning("Please enter a question.")
