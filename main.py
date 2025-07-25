from flask import Flask, request, send_file
import subprocess
import uuid
import os

app = Flask(__name__)

# ✅ Optional: Install ffmpeg if not already available (for Render)
def ensure_ffmpeg():
    if not os.path.exists("/usr/bin/ffmpeg"):
        os.system("apt-get update && apt-get install -y ffmpeg")

ensure_ffmpeg()

@app.route('/')
def index():
    return '''
    <h2>🎬 M3U8 Video Downloader</h2>
    <form method="POST" action="/download">
        <input name="url" type="text" placeholder="Enter M3U8 URL" style="width:400px;" required>
        <button type="submit">Download</button>
    </form>
    '''

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    if not url:
        return "❌ No URL provided", 400

    filename = f"video_{uuid.uuid4().hex}.mp4"

    try:
        # ✅ Run ffmpeg to download the video
        result = subprocess.run([
            'ffmpeg', '-i', url,
            '-c', 'copy', '-bsf:a', 'aac_adtstoasc',
            filename
        ], check=True)

        # ✅ Send the file as download response
        return send_file(filename, as_attachment=True)

    except subprocess.CalledProcessError as e:
        return f"❌ Download failed: {str(e)}", 500

    finally:
        # ✅ Clean up the file after response
        if os.path.exists(filename):
            os.remove(filename)

# ✅ Run Flask (for local dev or Gunicorn)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
