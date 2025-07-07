from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

import os
import pickle

load_dotenv()  # Load your .env containing OPENAI_API_KEY

def run_rag_pipeline(video_id: str, question: str) -> str:
    print(f"📥 Received video ID: {video_id}")
    print(f"❓ User question: {question}")

    # ---------- 1. Transcript Caching ----------
    transcript_path = f"cache/{video_id}_transcript.pkl"
    if os.path.exists(transcript_path):
        print("📄 Loading transcript from cache...")
        with open(transcript_path, "rb") as f:
            transcript = pickle.load(f)
    else:
        try:
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
        except NoTranscriptFound:
            print("⚠️ No 'en' transcript found. Trying fallback to 'en-US'...")
            transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
            try:
                transcript_obj = transcripts.find_transcript(["en-US", "en"])
                transcript_list = transcript_obj.fetch()
            except Exception:
                print("❌ No transcript available in 'en' or 'en-US'")
                raise NoTranscriptFound(video_id, ['en', 'en-US'], transcripts)

        transcript = " ".join(chunk.text for chunk in transcript_list)
        os.makedirs("cache", exist_ok=True)
        with open(transcript_path, "wb") as f:
            pickle.dump(transcript, f)
        print(f"📦 Transcript cached at {transcript_path}")

    # ---------- 2. Text Splitting ----------
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.create_documents([transcript])
    print(f"✂️ Total chunks created: {len(chunks)}")

    # ---------- 3. Vector Store Caching (FAISS) ----------
    faiss_path = f"cache/{video_id}_faiss"
    embedding = OpenAIEmbeddings(model="text-embedding-3-small")

    if os.path.exists(faiss_path):
        print("📥 Loading FAISS index from cache...")
        vector_store = FAISS.load_local(faiss_path, embedding, allow_dangerous_deserialization=True)
    else:
        print("⚙️ Creating new FAISS index...")
        vector_store = FAISS.from_documents(documents=chunks, embedding=embedding)
        vector_store.save_local(faiss_path)
        print(f"📦 FAISS index cached at {faiss_path}")


    # ---------- 4. Retrieval ----------
    retriever = vector_store.as_retriever(search_type="similarity", kwargs={"k": 3})
    retrieved_docs = retriever.invoke(question)
    print(f"🔍 Retrieved {len(retrieved_docs)} relevant chunks")

    context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
    if not context_text.strip():
        print("⚠️ No context found for the question.")
        return "Sorry, I couldn't find any relevant information in the video."

    # ---------- 5. Prompt + LLM ----------
    prompt = PromptTemplate(
        template="""
You're a helpful AI assistant.
Answer ONLY from the provided transcript context.
If the context is insufficient, just say you don't know.

{context}
Question: {question}
""",
        input_variables=['context', 'question']
    )

    final_prompt = prompt.invoke({"context": context_text, "question": question})
    print(f"🧠 Final prompt sent to LLM:\n{final_prompt}")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    response = llm.invoke(final_prompt)

    print(f"✅ LLM response:\n{response.content}")
    return response.content or "Sorry, I couldn't generate an answer."