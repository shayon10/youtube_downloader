from flask import Flask, render_template, request, send_file
import os
import yt_dlp
import re

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

FORMAT_OPTIONS = {
    "1080p": "bestvideo[height<=1080]+bestaudio/best",
    "720p": "bestvideo[height<=720]+bestaudio/best",
    "480p": "bestvideo[height<=480]+bestaudio/best",
    "Audio only (MP3)": "bestaudio"
}

def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "", title)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        quality = request.form["quality"]

        try:
            title = "downloaded"
            ydl_opts = {
                'format': FORMAT_OPTIONS[quality],
                'quiet': True,
                'noplaylist': True,
            }

            # Adjust output file type and postprocessor for MP3
            if "Audio" in quality:
                ydl_opts['outtmpl'] = os.path.join(DOWNLOAD_FOLDER, '%(title).200s.%(ext)s')
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                ydl_opts['outtmpl'] = os.path.join(DOWNLOAD_FOLDER, '%(title).200s.%(ext)s')

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                title = sanitize_filename(info.get("title", "video"))

            # If MP3, update filename extension
            if "Audio" in quality:
                filename = os.path.splitext(filename)[0] + ".mp3"

            return send_file(filename, as_attachment=True)
        except Exception as e:
            return f"<h3>Error: {e}</h3><p>Check the video URL or try a different format.</p>"

    return render_template("index.html", options=FORMAT_OPTIONS.keys())

if __name__ == "__main__":
    app.run(debug=True)
