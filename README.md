# 🎥 YouTube Video Chatbot – Chrome Extension

A smart Chrome Extension that enables users to **chat with YouTube videos** and get **AI-generated answers**, summaries, and insights — without watching the full video.

> 🔍 Built using **LangChain**, **Gemini/OpenAI**, **Qdrant**, and **Whisper**, this tool brings real-time Retrieval-Augmented Generation (RAG) to any YouTube video.

---

## 🚀 Features

- 🔎 Extracts and translates YouTube video transcripts (if available).
- 🎧 If no transcript is found, uses **Whisper ASR** to transcribe audio.
- 🌐 Translates non-English transcripts using **Gemini API**.
- 🤖 Generates AI-based responses and video summaries using a **RAG pipeline**.
- 💬 Smooth chat UI integrated directly inside a YouTube video page.
- 📦 One-time embedding of video chunks using **Qdrant Vector DB**.

---

## 🧠 Tech Stack

| Layer         | Tools/Tech                                |
|---------------|--------------------------------------------|
| Frontend      | HTML, CSS, JavaScript (Chrome Extension)   |
| Backend       | Python, Flask                              |
| AI & RAG      | LangChain, Gemini API / OpenAI API         |
| Transcription | Whisper (fallback for unavailable captions)|
| Vector Store  | Qdrant DB                                  |
| NLP Utilities | LangGraph, Prompt Engineering              |

---

## 🛠️ How It Works

1. 🔗 User opens a YouTube video with the extension enabled.
2. 📜 The extension checks for an English transcript.
   - ✅ If found: cleaned & chunked → embedded → stored in Qdrant.
   - ❌ If not found: audio is transcribed using **Whisper**.
3. 🌍 If the transcript is in another language, it's translated to English using **Gemini API**.
4. 💡 RAG pipeline (via LangChain) is triggered to answer user queries about the video content.
5. 💬 User interacts via a chatbot embedded directly on the YouTube page.

---

## 📸 Screenshots

> _You can add images or gifs here to demo the extension_

- Chat interface on a YouTube video
- Transcription fallback using Whisper
- AI-generated answers

---

## 📦 Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/SaurabhYadav45/Yt-video-RAG-chrome-extension
   cd Yt-video-RAG-chrome-extension
   
2. Install dependencies:
  pip install -r requirements.txt

3. Add your API keys in .env file:
  GEMINI_API_KEY=your_key_here
  OPENAI_API_KEY=optional_if_using

4. Run the Flask backend:
  python app.py

5. Load the Chrome extension:
  Go to chrome://extensions/
  Enable Developer Mode
  Click Load Unpacked and select the extension/ folder

Status:
Fully working MVP
Open to future enhancements like:
  Support for multilingual conversations
  Improved Whisper integration
  UI animations with React or Tailwind

Author:
Saurabh Singh Yadav

License:
This project is open-source and available under the MIT License.
