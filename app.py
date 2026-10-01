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
        is_mp3 = data.get('is_mp3', True)
        
        if not query:
            return jsonify({"error": "No query provided"}), 400

        # מחיקת קבצים קודמים
        for f in glob.glob("downloaded_file.*"):
            try:
                os.remove(f)
            except:
                pass

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'downloaded_file.%(ext)s',
            'noplaylist': True,
            'ignoreerrors': True,
        }
        
        if is_mp3:
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # מנסה לחפש בסאונדקלאוד
            info = ydl.extract_info(f"scsearch1:{query}", download=True)
            if not info:
                return jsonify({"error": "No results found on SoundCloud"}), 404
                
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
