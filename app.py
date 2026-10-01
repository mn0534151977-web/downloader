import os
import glob
from flask import Flask, request, send_file, render_template_string
import yt_dlp

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <title>מוריד מדיה ישיר</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; text-align: center; padding: 50px; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); display: inline-block; width: 400px; }
        input[type="text"] { width: 90%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; font-size: 16px; text-align: right; }
        select, button { padding: 10px 20px; margin: 10px 5px; font-size: 16px; border-radius: 5px; border: none; cursor: pointer; }
        button { background-color: #007BFF; color: white; font-weight: bold; }
        button:hover { background-color: #0056b3; }
        .loading { display: none; margin-top: 15px; color: #555; font-weight: bold; }
    </style>
    <script>
        function showLoading() {
            document.getElementById('loading-msg').style.display = 'block';
        }
    </script>
</head>
<body>
    <div class="container">
        <h2>מוריד מדיה ישיר</h2>
        <form action="/download" method="POST" onsubmit="showLoading()">
            <input type="text" name="query" placeholder="הכנס שם שיר או קישור ישיר..." required><br>
            <select name="type">
                <option value="mp3">אודיו (MP3)</option>
                <option value="mp4">וידאו (MP4 - 360p)</option>
            </select><br>
            <button type="submit">הורד קובץ</button>
        </form>
        <div id="loading-msg" class="loading">מוריד את הקובץ לשרת, נא להמתין מספר שניות...</div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download', methods=['POST'])
def download():
    try:
        query = request.form.get('query', '').strip()
        media_type = request.form.get('type', 'mp3')
        is_mp3 = (media_type == 'mp3')
        
        if not query:
            return "לא הוזן ערך", 400

        # מחיקת קבצים קודמים שנשארו בתיקייה
        for f in glob.glob("downloaded_file.*"):
            try:
                os.remove(f)
            except:
                pass

        if query.startswith("http://") or query.startswith("https://"):
            search_query = query
        else:
            search_query = f"scsearch1:{query}" if is_mp3 else f"ytsearch1:{query}"

        # הגדרות חילוץ ישירות ויציבות בגרסה העדכנית של yt-dlp
        if is_mp3:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'downloaded_file.%(ext)s',
                'noplaylist': True,
                'ignoreerrors': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                }],
            }
        else:
            # פורמט 18 יורד מיידית כקובץ משולב ללא צורך בהתקנת רכיבי מיזוג חיצוניים
            ydl_opts = {
                'format': '18/best[ext=mp4]/best',
                'outtmpl': 'downloaded_file.%(ext)s',
                'noplaylist': True,
                'ignoreerrors': True,
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_query, download=True)
            if not info:
                return "לא נמצאו תוצאות", 404
                
        downloaded_files = glob.glob("downloaded_file.*")
        if not downloaded_files:
            return "הקובץ לא נוצר", 500
            
        file_path = downloaded_files[0]
        file_name = os.path.basename(file_path)
        
        return send_file(file_path, as_attachment=True, download_name=file_name)
        
    except Exception as e:
        return f"שגיאת שרת: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
