from langchain_community.document_loaders import PyPDFLoader
from opensearch_langchain_vector_store import get_vector_store
from dotenv import load_dotenv


file = "./files/history-zoroastrian.pdf"

load_dotenv()

def load():
    loader = PyPDFLoader(file)
    docs = loader.load()#loader.load_and_split()
    
    get_vector_store().add_documents(
        docs, 
        vector_field = "vector_field", 
        engine="faiss", 
        ef_construction=512,
        ef_search=512,
        m=16,
    )

    print("data loaded!")

def main():
    load()

if __name__ == "__main__":
    main()