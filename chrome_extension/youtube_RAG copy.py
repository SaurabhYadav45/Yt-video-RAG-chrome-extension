from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain.text_splitter import RecursiveCharacterTextSplitter


# 1. Document Ingestion
try:
    video_id = "Gfr50f6ZBvo"
    transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=["en"])
    # trnscript list look like this
    # [
    #   {"text": "Hello world", "start": 0.0, "duration": 1.5},
    #   {"text": "This is a demo", "start": 1.5, "duration": 2.0},
    #   ...
    # ]


    # flatten it to plain text
    transcript = " ".join(chunk["text"] for chunk in transcript_list)
    # print(transcript)
except TranscriptsDisabled:
    print("No caption available for this video.")


# 2. Text Splitting 
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.create_documents([transcript])
# print(len(chunks))
# print(chunks[100])

# Embedding and vector store
embedding = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = FAISS.from_documents(
    embedding=embedding,
    documents=chunks
)

# res = vector_store.index_to_docstore_id
# print(res)

# vector_store.get_by_ids(['5ba19578-9c0d-41e2-950c-24ae249d6c38'])


# ************** Retrieval **************

retriever = vector_store.as_retriever(search_type="similarity", kwargs={"k": 3})
# usery_query = "What is deepmind"
# retriever_res = retriever.invoke(usery_query)
# print("Retriever_response: ", retriever_res)



#  Augmented Genration (Prompt + Context)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)

prompt = PromptTemplate(
    template="""
    You're an helpful AI assistant
    Answer ONLY from the provided transcript context.
    If the context is insufficient, just say you don't know.

    {context}
    Question:{question}
    """,
    input_variables=['context', 'question']
)

question = "is the topic of nuclear fusion discussed in this video? if yes then what was discussed"
retrieved_docs= retriever.invoke(question)
print("retriever_res",retrieved_docs)

context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)

final_prompt = prompt.invoke({"context":context_text, "question":question})
print("final prompt:", final_prompt)


# ********** Generation *************

response = llm.invoke(final_prompt)
print("Final response:\n")
print(response.content)



