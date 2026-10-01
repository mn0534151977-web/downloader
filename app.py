import os
import requests
from flask import Flask, request, send_file, render_template_string, redirect

app = Flask(__name__)

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
        <h2>מוריד מדיה סופי</h2>
        <form action="/download" method="POST" onsubmit="showLoading()">
            <input type="text" name="url" placeholder="הדבק קישור מיוטיוב או סאונדקלאוד..." required><br>
            <select name="type">
                <option value="audio">אודיו (MP3)</option>
                <option value="video">וידאו (MP4)</option>
            </select><br>
            <button type="submit">הורד קובץ עכשיו</button>
        </form>
        <div id="loading-msg" class="loading">מכין את הקובץ להורדה, אנתן להמתין מספר שניות...</div>
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
        url = request.form.get('url', '').strip()
        media_type = request.form.get('type', 'audio')
        
        if not url:
            return "לא הוזן קישור", 400

        # שימוש ב-API חיצונים חזקים שעוקפים את החסימות של יוטיוב לשרתים
        api_url = "https://api.cobalt.tools/api/json"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "url": url,
            "downloadMode": "audio" if media_type == "audio" else "auto"
        }

        response = requests.post(api_url, json=payload, headers=headers)
        res_data = response.json()

        if "url" in res_data:
            download_link = res_data["url"]
            return redirect(download_link)
        elif "picker" in res_data and len(res_data["picker"]) > 0:
            download_link = res_data["picker"][0]["url"]
            return redirect(download_link)
        else:
            return f"שגיאה בהפקת ההורדה מהשרת החיצוני: {res_data.get('text', 'לא ידוע')}", 500

    except Exception as e:
        return f"שגיאת שרת: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
