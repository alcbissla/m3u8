from flask import Flask, request, send_file
import subprocess
import os
import uuid

app = Flask(__name__)

def is_m3u8(url):
    return url.endswith(".m3u8") or ".m3u8?" in url

def generate_filename():
    return f"{uuid.uuid4().hex}.mp4"

@app.route("/")
def home():
    return '''
    <h2>📥 Multi Video Downloader</h2>
    <form method="post" action="/download">
        <input name="url" type="text" placeholder="Paste YouTube / TikTok / M3U8 URL" style="width:400px;" required>
        <button type="submit">Download</button>
    </form>
    '''

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    filename = generate_filename()

    try:
        if is_m3u8(url):
            # Use ffmpeg
            headers = (
                "User-Agent: Mozilla/5.0\r\n"
                "Referer: https://example.com\r\n"
            )

            cmd = [
                "ffmpeg",
                "-headers", headers,
                "-i", url,
                "-c", "copy",
                "-bsf:a", "aac_adtstoasc",
                filename
            ]
        else:
            # Use yt-dlp
            cmd = [
                "yt-dlp",
                "-o", filename,
                "-f", "mp4",
                url
            ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return f"<h3>❌ Error</h3><pre>{result.stderr}</pre>", 500

        return send_file(filename, as_attachment=True)

    finally:
        if os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.environ.get("PORT", 10000))
