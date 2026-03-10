from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore

# ── 1. Load your PDF(s) ──────────────────────────────────────
PDF_PATH = "/Users/aungnandaoo/Desktop/gen-ai/rag_queue/ingest-file/nodejs.pdf"

loader = PyPDFLoader(PDF_PATH)
documents = loader.load()
print(f"Loaded {len(documents)} pages")

# ── 2. Split into chunks ─────────────────────────────────────
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(documents)
print(f"Split into {len(chunks)} chunks")

# ── 3. Embed and store in Qdrant ─────────────────────────────
embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")

QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_model,
    url="http://localhost:6333",
    collection_name="learning-rag",
)

print("Done! Collection 'learning-rag' created.")
