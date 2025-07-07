# app.py
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import TranscriptsDisabled
from youtube_RAG import run_rag_pipeline  # This is the new function you'll extract from your current code
app = Flask(__name__)
CORS(app)  # Allow access from Chrome Extension

@app.route('/ask', methods=['POST'])
@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    video_id = data.get('videoId')
    question = data.get('question')

    if not video_id or not question:
        return jsonify({'error': 'Missing videoId or question'}), 400

    try:
        answer = run_rag_pipeline(video_id, question)
        return jsonify({'answer': answer})
    except TranscriptsDisabled:
        return jsonify({'error': 'No transcript available for this video'}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()  # 🐞 Show full stack trace in terminal
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)
