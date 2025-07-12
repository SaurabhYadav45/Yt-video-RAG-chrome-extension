import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import TranscriptsDisabled
from youtube_RAG import run_rag_pipeline 

app = Flask(__name__)
CORS(app)  

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
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)