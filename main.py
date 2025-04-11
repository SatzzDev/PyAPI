import math
from flask import Flask, request, send_file, jsonify
import os, uuid, subprocess, random
from rembg import remove
from PIL import Image
import threading, time

def auto_delete(file, delay=180):
 def hapus(): time.sleep(delay); os.remove(file) if os.path.exists(file) else None
 threading.Thread(target=hapus).start()

app = Flask(__name__)

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
 return jsonify({"creator": "SatzzDev", "message": quotes[math.floor(random.random()*len(quotes))]})

@app.route('/yt', methods=['GET'])
def yt():
 url = request.args.get('url')
 tipe = request.args.get('type','mp3')
 if not url: return jsonify({"error":"url kosong"})
 id = str(uuid.uuid4())
 out = f"{id}.%(ext)s"
 cmd = ['yt-dlp', url, '-o', out]
 if tipe == 'mp3': cmd += ['-x','--audio-format','mp3','--audio-quality','0','--ffmpeg-location','/usr/bin/ffmpeg','--prefer-ffmpeg']
 elif tipe == 'mp4': cmd += ['-f','bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]','--ffmpeg-location','/usr/bin/ffmpeg','--prefer-ffmpeg']
 else: return jsonify({"error":"tipe harus mp3 atau mp4"})
 subprocess.run(cmd)
 for f in os.listdir():
  if f.startswith(id) and ((tipe=='mp3' and f.endswith('.mp3')) or (tipe=='mp4' and f.endswith('.mp4'))):
   auto_delete(f)
   return send_file(f, as_attachment=True)
 return jsonify({"error":"gagal download"})


@app.route('/removebg', methods=['POST'])
def removebg():
 if 'image' not in request.files: return jsonify({"error":"image kosong"})
 img = request.files['image'].read()
 hasil = remove(img)
 id = f"{uuid.uuid4()}.png"
 with open(id,'wb') as f: f.write(hasil)
 auto_delete(id)
 return send_file(id, mimetype='image/png')

@app.route('/upscale', methods=['POST'])
def upscale():
 if 'image' not in request.files: return jsonify({"error":"image kosong"})
 img = Image.open(request.files['image'])
 besar = img.resize((img.width*2, img.height*2), Image.LANCZOS)
 id = f"{uuid.uuid4()}.png"
 besar.save(id)
 auto_delete(id)
 return send_file(id, mimetype='image/png')

if __name__ == '__main__':
 app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))
