from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import sys

# Pre-import to fail early if missing (though Vercel should have it from requirements.txt)
try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        video_id = params.get('videoId', [None])[0]
        lang = params.get('lang', ['de'])[0]
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.end_headers()
        
        if not video_id:
            self.wfile.write(json.dumps({'error': 'videoId required'}).encode())
            return
            
        if not YouTubeTranscriptApi:
            self.wfile.write(json.dumps({'error': 'youtube-transcript-api library not installed'}).encode())
            return
        
        try:
            # 1. Get available transcripts
            transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # 2. Try preferred language
            try:
                t = transcripts.find_transcript([lang])
            except:
                # 3. Fallback to DE/EN manually created
                try:
                    t = transcripts.find_transcript(['de', 'en'])
                except:
                    # 4. Fallback to generated DE/EN/EN-US
                    t = transcripts.find_generated_transcript(['de', 'en', 'en-US', 'de-DE'])
            
            data = t.fetch()
            result = [{'text': s['text'], 'offset': s['start']*1000, 'duration': s['duration']*1000} for s in data]
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            # Always return a clean JSON error
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
