import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import mv_generator_pro as mv_engine[span_6](start_span)[span_6](end_span)

app = Flask(__name__)
CORS(app)  # Memungkinkan Netlify berkomunikasi dengan Render

UPLOAD_FOLDER = '/tmp/uploads'
OUTPUT_FOLDER = '/tmp/outputs'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return jsonify({"status": "Server AI MV Generator Aktif!"})

@app.route('/api/generate-mv', methods=['POST'])
def generate_mv():
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'message': 'File audio (.mp3) wajib ada!'}), 400
        
        audio_file = request.files['audio']
        audio_filename = secure_filename(audio_file.filename)
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
        audio_file.save(audio_path)

        clips_files = request.files.getlist('clips')
        if not clips_files or clips_files[0].filename == '':
            return jsonify({'success': False, 'message': 'Minimal unggah 1 klip video!'}), 400

        clips_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'clips_temp')
        os.makedirs(clips_dir, exist_ok=True)
        
        for f in os.listdir(clips_dir):
            os.remove(os.path.join(clips_dir, f))

        for clip in clips_files:
            clip_name = secure_filename(clip.filename)
            clip.save(os.path.join(clips_dir, clip_name))

        aspect_ratio = request.form.get('aspect_ratio', '16:9')[span_7](start_span)[span_7](end_span)
        lyrics_raw = request.form.get('lyrics', '')
        
        lyrics_data = []
        if lyrics_raw.strip():
            lines = lyrics_raw.strip().split('\n')
            for line in lines:
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        lyrics_data.append({
                            'start': float(parts[0].strip()),
                            'end': float(parts[1].strip()),
                            'text': parts[2].strip()
                        })

        output_filename = "Hasil_MV_AI.mp4"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

        mv_engine.build_advanced_mv(
            audio_path=audio_path,
            clips_dir=clips_dir,
            output_path=output_path,
            lyrics_file_or_list=lyrics_data if lyrics_data else None,
            config={'aspect_ratio': aspect_ratio}
        )

        return jsonify({
            'success': True,
            'message': 'MV berhasil dibuat!',
            'download_url': f'/download/{output_filename}'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
