import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# from langchain_community.vectorstores import FAISS
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from langchain_core.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from transcript_handler import get_english_transcript
from google import genai
from pathlib import Path
load_dotenv()

# Set up gemini client
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai_client = genai.Client(api_key=GEMINI_API_KEY)

def run_rag_pipeline(video_id: str, question: str) -> str:
    
    collection_name = f"yt_{video_id}"
    embedding = OpenAIEmbeddings(model="text-embedding-3-small")

    # === Try loading the existing collection
    try:
        vector_store = QdrantVectorStore(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
            collection_name=collection_name,
            embedding=embedding,
            prefer_grpc=True
        )
        # Trigger a test query to check if it exists
        _ = vector_store.similarity_search("test", k=1)
        collection_exists = True
    except Exception as e:
        print("🟡 Collection not found, creating new one...")
        collection_exists = False
    
    if not collection_exists:
        # Get Transcript
        transcript = get_english_transcript(video_id)
        if not transcript:
            return "❌ Transcript not available or could not be processed."

        print(f"📄 Transcript length: {len(transcript)}")
        print(f"📄 Transcript preview: {transcript[:300]}")

        # Split into Chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.create_documents([transcript])

        # Create and upload to vector store
        vector_store = QdrantVectorStore.from_documents(
            documents=chunks,
            embedding=embedding,
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
            collection_name=collection_name,
            prefer_grpc=True
        )

    # 4. Retrieve Relevant Context
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})
    retrieved_docs = retriever.invoke(question)
    context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)

    # 5. Prompt + LLM Generation
    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template="""
        You're a helpful and structured AI assistant.
        Answer ONLY using the transcript provided in the context below.
        If the transcript lacks information to answer the question, say you don't know — don't hallucinate.

        If the user is asking for a **summary** of the video:
        - Provide a well-structured summary in **bullet points**
        - Each bullet should be a complete and clear idea
        - Make sure to **cover all major aspects** of the video
        - Keep technical explanations **short but accurate**
        - Use **numbered bullets** if there is a sequence or list

        If the user is asking a **specific question**, answer it precisely from the transcript.

        ---
        Context:
        {context}

        Question:
        {question}
        """
    )

    # llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
    # final_prompt = prompt.invoke({"context": context_text, "question": question})
    # response = llm.invoke(final_prompt)
    # print("Final Output:\n", response)
    # return response.content

    final_prompt = prompt.format(context=context_text, question=question)
    response = genai_client.models.generate_content(
        model='gemini-1.5-flash', 
        contents=final_prompt
    )
    print("Final Response:\n",response.text)
    return response.text