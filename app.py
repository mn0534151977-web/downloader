import os
import glob
from flask import Flask, request, jsonify, send_file, render_template_string
import yt_dlp

app = Flask(__name__)

# דף הבית עם ממשק משתמש נקי
HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <title>מוריד מדיה מהיר</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; text-align: center; padding: 50px; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); display: inline-block; width: 400px; }
        input[type="text"] { width: 90%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; font-size: 16px; text-align: right; }
        select, button { padding: 10px 20px; margin: 10px 5px; font-size: 16px; border-radius: 5px; border: none; cursor: pointer; }
        button { background-color: #007BFF; color: white; }
        button:hover { background-color: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <h2>הורדת אודיו / וידאו</h2>
        <form action="/download-web" method="POST">
            <input type="text" name="query" placeholder="הכנס שם שיר או קישור ישיר..." required><br>
            <select name="type">
                <option value="mp3">אודיו (MP3)</option>
                <option value="mp4">וידאו (MP4)</option>
            </select><br>
            <button type="submit">הורד קובץ</button>
        </form>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download-web', methods=['POST'])
def download_web():
    try:
        query = request.form.get('query', '').strip()
        media_type = request.form.get('type', 'mp3')
        is_mp3 = (media_type == 'mp3')
        
        if not query:
            return "לא הוזן ערך לחיפוש", 400

        # ניקוי קבצים קודמים שנשארו
        for f in glob.glob("downloaded_file.*"):
            try:
                os.remove(f)
            except:
                pass

        # זיהוי חכם: האם מדובר בקישור או בטקסט חיפוש
        if query.startswith("http://") or query.startswith("https://"):
            search_query = query
        else:
            # אם זה טקסט חופשי: לאודיו מחפשים ב-SoundCloud, לוידאו מחפשים ביוטיוב
            search_query = f"scsearch1:{query}" if is_mp3 else f"ytsearch1:{query}"

        # הגדרות הורדה
        if is_mp3:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'downloaded_file.%(ext)s',
                'noplaylist': True,
                'ignoreerrors': True,
            }
        else:
            ydl_opts = {
                'format': 'best[ext=mp4]/best',
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
        return f"שגיאה: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
