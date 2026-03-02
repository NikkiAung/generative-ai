from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from openai import OpenAI

load_dotenv()

openai_client = OpenAI()
# Vector Embeddings
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="learning-rag",
    embedding=embedding_model,
)

user_query = input("Ask Something ... ")

# Relevant Chunks from the vector DB
search_results = vector_db.similarity_search(query=user_query)

context = "\n\n\n".join([
    f"Page Content: {result.page_content}\nPage Number: {result.metadata.get('page', result.metadata.get('page_label', 'N/A'))}\nFile Location: {result.metadata['source']}"
    for result in search_results
])

# Define the prompt template
SYSTEM_PROMPT_TEMPLATE = """
    You are a helpful AI Assistant who answers user Query based on the available context.
    retrieved from a pdf file along with page_contents and page number.

    You should only answer the user based on the following context and navigate the user
    to open the right page number to know more.

    context:{context}
"""

# **FIX 1: Use an f-string to format the prompt with the context**
final_system_prompt = SYSTEM_PROMPT_TEMPLATE.format(context=context)

response = openai_client.chat.completions.create(
    # **FIX 2: Use a valid model name**
    model="gpt-4o",  # Or "gpt-3.5-turbo"
    messages=[
        {"role": "system", "content": final_system_prompt},
        {"role": "user", "content": user_query}
    ]
)

print(f"Bot: {response.choices[0].message.content}")