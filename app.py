@app.route('/download', methods=['POST'])
def download():
    try:
        query = request.form.get('query', '').strip()
        media_type = request.form.get('type', 'mp3')
        is_mp3 = (media_type == 'mp3')
        
        if not query:
            return "לא הוזן ערך", 400

        # מחיקת קבצים קודמים
        for f in glob.glob("downloaded_file.*"):
            try:
                os.remove(f)
            except:
                pass

        if query.startswith("http://") or query.startswith("https://"):
            search_query = query
        else:
            search_query = f"ytsearch1:{query}"

        common_opts = {
            'outtmpl': 'downloaded_file.%(ext)s',
            'noplaylist': True,
            'ignoreerrors': True,
            'no_warnings': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'ios', 'web']
                }
            }
        }

        if is_mp3:
            common_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            common_opts.update({
                'format': 'best[height<=360]/best',
            })

        with yt_dlp.YoutubeDL(common_opts) as ydl:
            info = ydl.extract_info(search_query, download=True)
            if not info:
                return "שגיאה: לא נמצאו תוצאות או שהסרטון חסום להורדה.", 404
                
        downloaded_files = glob.glob("downloaded_file.*")
        if not downloaded_files:
            return "שגיאה: קובץ המדיה לא נוצר עקב מגבלת שרת או חסימה.", 500
            
        file_path = downloaded_files[0]
        file_name = os.path.basename(file_path)
        
        return send_file(file_path, as_attachment=True, download_name=file_name)
        
    except Exception as e:
        return f"שגיאת שרת פנימית: {str(e)}", 500
