# Colab Notebook for Building a RAG System with LLAMAIndex and OpenAI

# Install Required Libraries
# !pip install llama-index
# !pip install openai
# !pip install faiss-cpu
# !pip install requests
# !pip install PyMuPDF

# Import Libraries
import os
import openai
import faiss
import numpy as np
import fitz  # PyMuPDF for PDF handling
from llama_index.core import VectorStoreIndex, ServiceContext, PromptTemplate, Document
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.vector_stores.faiss import FaissVectorStore

# Load OpenAI API key from file
with open("OPEN_AI_KEY.txt", "r") as key_file:
    openai.api_key = key_file.read().strip()

# Load text files and convert PDFs from the "data" folder
text_folder = "data"
texts = []

for filename in os.listdir(text_folder):
    file_path = os.path.join(text_folder, filename)
    if filename.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as file:
            texts.append(file.read())
    elif filename.endswith(".pdf"):
        with fitz.open(file_path) as pdf:
            pdf_text = ""
            for page_num in range(pdf.page_count):
                page = pdf.load_page(page_num)
                pdf_text += page.get_text()
            texts.append(pdf_text)

# Configure the chunking
chunk_size = 1024  # Size of each text chunk
chunks = []
for text in texts:
    chunks.extend([text[i:i+chunk_size] for i in range(0, len(text), chunk_size)])

# Create the vector store
def embed_texts(texts):
    """Embeds text using OpenAI and returns the numpy array of embeddings."""
    response = openai.Embedding.create(input=texts, model="text-embedding-ada-002")
    embeddings = [item['embedding'] for item in response['data']]
    return np.array(embeddings)

# Initialize FAISS index
dimension = 1536  # Dimension of the OpenAI embeddings (ensure this matches your model's output)
faiss_index = faiss.IndexFlatL2(dimension)

# Create the vector store
vector_store = FaissVectorStore(faiss_index=faiss_index)

# Manually add texts to the vector store
for chunk in chunks:
    embedding = embed_texts([chunk])[0]
    vector_store.add_vector(embedding, metadata={"chapter": "Introduction"})

# Simple search method
def search(query, top_k=3):
    query_embedding = embed_texts([query])[0]
    ids, distances = vector_store.search(query_embedding, top_k=top_k)
    return [(chunks[id], distances[i]) for i, id in enumerate(ids)]

# Query the index
query = "What happened on November 1st, 1907?"
response = search(query, top_k=3)
print(response)
