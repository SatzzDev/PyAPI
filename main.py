import math
from flask import Flask, request, send_file, jsonify
import os, uuid, subprocess, random, threading, time
from rembg import new_session, remove as rembg_remove
from PIL import Image

# ==== CONFIGURATION & PRELOAD MODEL ====
app = Flask(__name__)
# Auto-load U2NET model for removebg
session_u2net = new_session(model_name="u2net")

# Utility: Auto-delete file after delay (in seconds)
def auto_delete(path, delay=180):
    def _del():
        time.sleep(delay)
        if os.path.exists(path):
            os.remove(path)
    threading.Thread(target=_del, daemon=True).start()

# Root endpoint: random quote
quotes = [
    "percaya boleh, tapi jangan buta. orang bisa berubah kapan aja",
    "gak semua yang deket itu tulus, kadang cuma numpang jalan doang",
    "gak semua senyum itu jujur",
    "trust less, log everything",
    "jangan gampang cerita, gak semua orang peduli, sebagian cuma pengin tahu aja",
    "kalau lo terlalu baik, siap-siap dimanfaatin",
    "gak semua yang deket itu temen, kadang cuma musuh yang lagi nyamar",
    "pada akhirnya, cuma diri lo sendiri yang selalu ada",
    "kadang yang paling nyakitin bukan orang jauh, tapi yang lo percaya",
    "gak semua kehilangan itu buruk, kadang Tuhan cuma bersihin circle lo",
    "sendiri gak selalu sepi, kadang lebih tenang daripada bareng orang yang salah",
    "belajar ngelepas orang yang bikin lo mikir dua kali buat percaya lagi",
    "orang bisa bilang sayang hari ini, lalu ninggalin tanpa alasan besok",
    "lo gak butuh banyak temen, lo cuma butuh satu yang bener-bener ada",
    "jangan terlalu berharap dari orang lain, ekspektasi itu sumber kecewa",
    "semakin banyak lo percaya orang, semakin besar kemungkinan lo dikecewain",
    "gak usah maksa dimengerti, gak semua orang pantas tahu isi hati lo",
    "diam bukan berarti kalah, kadang itu cara paling damai buat jaga diri",
    "kalau akhirnya lo sendiri, itu bukan kutukan — itu proses jadi kuat",
    "percaya itu mahal, jangan sembarang bagi"
]

@app.route('/')
def index():
    msg = random.choice(quotes)
    return jsonify({"creator": "SatzzDev", "message": msg})

# YouTube download endpoint
@app.route('/yt', methods=['GET'])
def yt():
    url = request.args.get('url')
    tipe = request.args.get('type', 'mp3')
    if not url:
        return jsonify(error="url kosong"), 400

    # Validate basic YouTube URL
    if not url.startswith(('http://', 'https://')):
        return jsonify(error="url tidak valid"), 400

    # Generate unique output pattern
    uid = str(uuid.uuid4())
    out_pattern = f"{uid}.%(ext)s"

    # Build yt-dlp command
    cmd = ['yt-dlp', url, '-o', out_pattern]
    if tipe == 'mp3':
        cmd += ['-x', '--audio-format', 'mp3', '--audio-quality', '0',
                '--ffmpeg-location', '/usr/bin/ffmpeg', '--prefer-ffmpeg']
    elif tipe == 'mp4':
        cmd += ['-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]',
                '--ffmpeg-location', '/usr/bin/ffmpeg', '--prefer-ffmpeg']
    else:
        return jsonify(error="tipe harus mp3 atau mp4"), 400

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        app.logger.exception("yt-dlp gagal")
        return jsonify(error="gagal download dari YouTube"), 500

    # Find generated file
    for fname in os.listdir('.'):
        if fname.startswith(uid) and ((tipe=='mp3' and fname.endswith('.mp3')) or (tipe=='mp4' and fname.endswith('.mp4'))):
            auto_delete(fname)
            return send_file(fname, as_attachment=True)

    return jsonify(error="file output tidak ditemukan"), 500

# Background removal endpoint
@app.route('/removebg', methods=['POST'])
def removebg():
    if 'image' not in request.files:
        return jsonify(error="image kosong"), 400
    try:
        img = Image.open(request.files['image'].stream).convert('RGBA')
        out_img = rembg_remove(img, session=session_u2net)

        out_path = f"{uuid.uuid4()}.png"
        out_img.save(out_path, format="PNG")
        auto_delete(out_path)
        return send_file(out_path, mimetype='image/png')

    except Exception as e:
        app.logger.exception("Error di /removebg")
        return jsonify(error=str(e)), 500

# Upscale endpoint
@app.route('/upscale', methods=['POST'])
def upscale():
    if 'image' not in request.files:
        return jsonify(error="image kosong"), 400
    try:
        img = Image.open(request.files['image'].stream)
        new_size = (img.width * 2, img.height * 2)
        up_img = img.resize(new_size, Image.LANCZOS)

        out_path = f"{uuid.uuid4()}.png"
        up_img.save(out_path, format="PNG")
        auto_delete(out_path)
        return send_file(out_path, mimetype='image/png')

    except Exception as e:
        app.logger.exception("Error di /upscale")
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)), debug=True)
