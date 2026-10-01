import os
import requests
from flask import Flask, request, render_template_string, redirect
import yt_dlp

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <title>מוריד מדיה חכם</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; text-align: center; padding: 50px; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0px 0px 10px rgba(0,0,0,0.1); display: inline-block; width: 400px; }
        input[type="text"] { width: 90%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 5px; font-size: 16px; text-align: right; }
        select, button { padding: 10px 20px; margin: 10px 5px; font-size: 16px; border-radius: 5px; border: none; cursor: pointer; }
        button { background-color: #28a745; color: white; font-weight: bold; }
        button:hover { background-color: #218838; }
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
        <h2>מוריד מדיה חכם</h2>
        <form action="/download" method="POST" onsubmit="showLoading()">
            <input type="text" name="query" placeholder="הכנס שם שיר או קישור ישיר..." required><br>
            <select name="type">
                <option value="audio">אודיו (MP3)</option>
                <option value="video">וידאו (MP4)</option>
            </select><br>
            <button type="submit">הורד קובץ עכשיו</button>
        </form>
        <div id="loading-msg" class="loading">מחפש ומכין את הקובץ להורדה, נא להמתין...</div>
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
        media_type = request.form.get('type', 'audio')
        
        if not query:
            return "לא הוזן ערך", 400

        # זיהוי האם מדובר בקישור או בטקסט חיפוש
        if query.startswith("http://") or query.startswith("https://"):
            target_url = query
        else:
            # אם זה טקסט, נשתמש ב-yt-dlp לשליפת הקישור בלבד
            search_query = f"scsearch1:{query}" if media_type == "audio" else f"ytsearch1:{query}"
            ydl_opts = {
                'noplaylist': True,
                'ignoreerrors': True,
                'extract_flat': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_query, download=False)
                if not info:
                    return "לא נמצאו תוצאות בחיפוש", 404
                
                if 'entries' in info and len(info['entries']) > 0:
                    entry = info['entries'][0]
                    target_url = entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id')}"
                else:
                    return "לא נמצא קישור תקין לתוצאה", 404

        # שליחת הקישור לשרת החיצוני להורדה חלקה
        api_url = "https://api.cobalt.tools/api/json"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "url": target_url,
            "downloadMode": "audio" if media_type == "audio" else "auto"
        }

        response = requests.post(api_url, json=payload, headers=headers)
        res_data = response.json()

        if "url" in res_data:
            return redirect(res_data["url"])
        elif "picker" in res_data and len(res_data["picker"]) > 0:
            return redirect(res_data["picker"][0]["url"])
        else:
            return f"שגיאה בהפקת ההורדה: {res_data.get('text', 'לא ידוע')}", 500

    except Exception as e:
        return f"שגיאת שרת: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
