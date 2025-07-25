from flask import Flask, request, send_file
import subprocess
import uuid
import os

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <form method="POST" action="/download">
        <input name="url" type="text" placeholder="Enter M3U8 URL" required>
        <button type="submit">Download</button>
    </form>
    '''

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    filename = f"video_{uuid.uuid4().hex}.mp4"

    try:
        # Use ffmpeg to download and convert
        subprocess.run([
            'ffmpeg', '-i', url,
            '-c', 'copy', '-bsf:a', 'aac_adtstoasc',
            filename
        ], check=True)

        # Immediately return file in the POST response
        return send_file(filename, as_attachment=True)

    except subprocess.CalledProcessError:
        return "❌ Error: Download failed. Check the link."

    finally:
        # Clean up after response
        if os.path.exists(filename):
            os.remove(filename)

# Run Flask app
app.run(host='0.0.0.0', port=8080)
