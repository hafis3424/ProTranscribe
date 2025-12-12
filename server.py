from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# Initialize the API
ytt_api = YouTubeTranscriptApi()

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/api/transcript')
def get_transcript():
    video_id = request.args.get('videoId')
    
    if not video_id:
        return jsonify({'error': 'Video ID is required'}), 400
    
    try:
        # Fetch transcript using the new API (v1.2.3)
        fetched_transcript = ytt_api.fetch(video_id)
        
        # Get raw data
        transcript_data = fetched_transcript.to_raw_data()
        
        # Format the response
        formatted_transcript = []
        full_text = []
        
        for entry in transcript_data:
            formatted_transcript.append({
                'text': entry['text'],
                'start': entry['start'],
                'duration': entry['duration']
            })
            full_text.append(entry['text'])
        
        return jsonify({
            'success': True,
            'videoId': video_id,
            'transcript': formatted_transcript,
            'fullText': ' '.join(full_text)
        })
        
    except Exception as e:
        error_message = str(e)
        if 'disabled' in error_message.lower():
            return jsonify({'error': 'Transcripts are disabled for this video'}), 400
        elif 'not found' in error_message.lower() or 'no transcript' in error_message.lower():
            return jsonify({'error': 'No transcript found for this video'}), 404
        elif 'unavailable' in error_message.lower():
            return jsonify({'error': 'Video is unavailable'}), 404
        else:
            return jsonify({'error': f'Failed to fetch transcript: {error_message}'}), 500

if __name__ == '__main__':
    print("ProTranscribe server running at http://localhost:3000")
    app.run(port=3000, debug=True)
