app = Flask(__name__)

@app.route('/')
def home():
    return "Downloader Server is Running! Send POST requests to /download"

@app.route('/download', methods=['POST'])
def download_media():
    # שאר הקוד שלך נשאר בדיוק אותו דבר...    data = request.json
    query = data.get('query', '')
    is_mp3 = data.get('is_mp3', False)
    
    if not query:
        return jsonify({"error": "No query provided"}), 400

    # מחיקת קבצים קודמים אם נשארו בטעות
    for f in glob.glob("downloaded_file.*"):
        try:
            os.remove(f)
        except:
            pass

    ydl_opts = {
        'format': 'bestaudio/best' if is_mp3 else 'bestvideo+bestaudio/best',
        'outtmpl': 'downloaded_file.%(ext)s',
    }
    
    if is_mp3:
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            
        downloaded_files = glob.glob("downloaded_file.*")
        if not downloaded_files:
            return jsonify({"error": "Download failed"}), 500
            
        file_path = downloaded_files[0]
        file_name = os.path.basename(file_path)
        
        # החזרת הקובץ המוכן ישירות להורדה
        return send_file(file_path, as_attachment=True, download_name=file_name)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
