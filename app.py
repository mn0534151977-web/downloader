import os
import glob
from flask import Flask, request, jsonify, send_file
import yt_dlp

app = Flask(__name__)

@app.route('/')
def home():
    return "Downloader Server is Running!"

@app.route('/download', methods=['POST'])
def download_media():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        query = data.get('query', '')
        # כברירת מחדל מוריד אודיו, אלא אם כן נשלח במפורש false
        is_mp3 = data.get('is_mp3', True)
        
        if not query:
            return jsonify({"error": "No query provided"}), 400

        # מחיקת קבצים קודמים שנשארו
        for f in glob.glob("downloaded_file.*"):
            try:
                os.remove(f)
            except:
                pass

        # הגדרות בהתאם לסוג ההורדה (אודיו או וידאו)
        if is_mp3:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'downloaded_file.%(ext)s',
                'noplaylist': True,
                'ignoreerrors': True,
            }
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
            search_query = f"scsearch1:{query}"
        else:
            ydl_opts = {
                'format': 'bestvideo+bestaudio/best',
                'outtmpl': 'downloaded_file.%(ext)s',
                'noplaylist': True,
                'ignoreerrors': True,
                'merge_output_format': 'mp4',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web', 'mweb']
                    }
                }
            }
            search_query = f"ytsearch1:{query}"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=True)
            if not info:
                return jsonify({"error": "No results found"}), 404
                
        downloaded_files = glob.glob("downloaded_file.*")
        if not downloaded_files:
            return jsonify({"error": "Download file was not created"}), 500
            
        file_path = downloaded_files[0]
        file_name = os.path.basename(file_path)
        
        return send_file(file_path, as_attachment=True, download_name=file_name)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
