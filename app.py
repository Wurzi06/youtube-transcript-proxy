from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)

@app.route('/api/transcript')
def transcript():
    video_id = request.args.get('videoId')
    lang = request.args.get('lang', 'de')

    if not video_id:
        return jsonify({'error': 'videoId required'}), 400

    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try preferred language first
        try:
            t = transcripts.find_transcript([lang])
        except:
            # Fallback to manually created DE/EN
            try:
                t = transcripts.find_transcript(['de', 'en'])
            except:
                # Fallback to generated DE/EN/EN-US
                t = transcripts.find_generated_transcript(['de', 'en', 'en-US', 'de-DE'])

        data = t.fetch()
        result = [{'text': s['text'], 'offset': s['start']*1000, 'duration': s['duration']*1000} for s in data]
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/api/transcript', methods=['OPTIONS'])
def handle_options():
    return '', 200

if __name__ == '__main__':
    app.run()
