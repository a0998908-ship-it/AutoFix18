import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path


# Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Create ChromaDB client
client = chromadb.PersistentClient(path="data/chroma_db")

# Create a collection
collection = client.get_or_create_collection(
    name="codebase"
)


def index_code(folder="codebase"):

    files = Path(folder).glob("*.py")

    for file in files:
        code = file.read_text()

        embedding = model.encode(code).tolist()

        collection.upsert(
            ids=[file.name],
            documents=[code],
            embeddings=[embedding]
        )

    print("Code indexing completed!")


def search_code(query):

    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    return results["documents"]