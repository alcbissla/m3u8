import os
import subprocess
from flask import Flask, request, render_template, send_file, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = "supersecretkey"
COOKIE_FILE = "cookies.txt"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "cookies" in request.files:
            cookies = request.files["cookies"]
            if cookies.filename == "":
                flash("No cookies file selected")
            else:
                cookies.save(COOKIE_FILE)
                flash("Cookies uploaded successfully!")
                return redirect(url_for("index"))

        elif "url" in request.form:
            url = request.form.get("url").strip()
            filename = "video.mp4"
            if os.path.exists(filename):
                os.remove(filename)

            if url.endswith(".m3u8") or ".m3u8" in url:
                # Download M3U8 using ffmpeg
                cmd = [
                    "ffmpeg",
                    "-y",  # overwrite output
                    "-i", url,
                    "-c", "copy",
                    filename
                ]
            else:
                # YouTube/TikTok with yt-dlp
                if not os.path.exists(COOKIE_FILE):
                    flash("Please upload cookies.txt first!")
                    return redirect(url_for("index"))

                cmd = [
                    "yt-dlp",
                    "--cookies", COOKIE_FILE,
                    "-f", "mp4",
                    "-o", filename,
                    url
                ]

            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                if result.returncode != 0:
                    flash(f"Download failed: {result.stderr}")
                    return redirect(url_for("index"))
                else:
                    return send_file(filename, as_attachment=True)
            except subprocess.TimeoutExpired:
                flash("Download timed out!")
                return redirect(url_for("index"))
            except Exception as e:
                flash(f"Error: {str(e)}")
                return redirect(url_for("index"))

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
