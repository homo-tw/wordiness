from flask import Flask, request, jsonify, send_file
from transcriber import transcribe
import os

app = Flask(__name__)

@app.route("/transcribe", methods=["POST"])
def handle_transcribe():
    if "file" not in request.files:
        return jsonify({"error": "Missing audio file"}), 400

    audio_file = request.files["file"]
    audio_path = "/tmp/audio.mp3"
    audio_file.save(audio_path)

    srt_path = "/tmp/output.srt"
    transcribe(audio_path, srt_path)

    return send_file(srt_path, mimetype="text/plain", as_attachment=True, download_name="subtitle.srt")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
