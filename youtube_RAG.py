import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
import pickle
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from langchain_community.vectorstores import FAISS
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from langchain_core.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from transcript_handler import get_english_transcript
import google.generativeai as genai
from pathlib import Path
load_dotenv()

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# genai.configure(api_key=GEMINI_API_KEY)

def run_rag_pipeline(video_id: str, question: str) -> str:
    # === Setup Qdrant Client ===
    qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"), 
    api_key=os.getenv("QDRANT_API_KEY")
    )

    collection_name = f"yt_{video_id}"
    embedding = OpenAIEmbeddings(model="text-embedding-3-small")

    # === Create Collection if Needed ===
    if collection_name not in [col.name for col in qdrant_client.get_collections().collections]:
        # Get Transcript
        transcript = get_english_transcript(video_id)
        if not transcript:
            return "❌ Transcript not available or could not be processed."

        # Split into Chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.create_documents([transcript])

        # Create collection and upload vectors
        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
        )

        vector_store = Qdrant.from_documents(
            documents=chunks,
            embedding=embedding,
            location=qdrant_client,
            collection_name=collection_name
        )
    else:
        # Load existing vector store
        vector_store = Qdrant(
            client=qdrant_client,
            collection_name=collection_name,
            embeddings=embedding
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

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
    final_prompt = prompt.invoke({"context": context_text, "question": question})
    response = llm.invoke(final_prompt)

    return response.content
