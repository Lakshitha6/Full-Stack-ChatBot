import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import  RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

def generate_response(question):


# initialize llm model (huggingface)

    llm = ChatGroq(
        api_key=SecretStr(groq_api_key if groq_api_key is not None else "GROQ_API_KEY environment variable is not set."),
        model="qwen/qwen3-32b",
        temperature=0.6
    )
    # initialize embedding model huggingface

    embedding_model = HuggingFaceEmbeddings(
        model_name = "sentence-transformers/all-mpnet-base-v2"
    )

    #convert output gets from llm to String
    output_parser = StrOutputParser()

    # create a vector store from splitted text using chroma vector database
    app_dir = os.path.dirname(os.path.abspath(__file__))
    datastore_path = os.path.join(app_dir, "datastore")
    pdf_path = os.path.join(app_dir, "data.pdf")
    
    if os.path.exists(datastore_path):
        vectorstore = Chroma(persist_directory=datastore_path, embedding_function=embedding_model)
    else:
        load_pdf = PyPDFLoader(pdf_path)
        docs = load_pdf.load()

        # Split document into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=80)
        splits = text_splitter.split_documents(docs)

        # Create and persist vector store
        vectorstore = Chroma.from_documents(documents=splits, embedding=embedding_model, persist_directory=datastore_path)

    #create retriver from vectorstore
    retriever = vectorstore.as_retriever()

    #define prompt template
    template = """
    You are a helpful tutor for beginner IT students.

    Answer the question below using only the information from the provided context. 
    Explain things clearly and simply. If the answer is not in the context, say "I have no knowledge to answer your question."

    Question:
    {question}

    Context:
    {context}

    Answer (simple and clear explanation):
    """

    prompt = ChatPromptTemplate.from_template(template)

    chain = (
        {"context": retriever,  "question": RunnablePassthrough()}
        | prompt
        | llm
        | output_parser
    )

    try:
        response = chain.invoke(question)
        return response
    except Exception as e:
        print(f"Error invoking chain: {e}")
        return "Sorry, the service is currently unavailable. Please try again later."
    
#print(generate_response("What is firewall"))