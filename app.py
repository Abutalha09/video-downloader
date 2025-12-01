from flask import Flask, request, send_file, jsonify, render_template
import yt_dlp
import os

app = Flask(__name__)

# Persistent download folder
download_folder = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(download_folder, exist_ok=True)

# --- URL Cleaner
def clean_url(url: str) -> str:
    if "youtube.com/shorts/" in url and "?" in url:
        url = url.split("?")[0]
    return url

# --- Serve frontend
@app.route('/')
def home():
    return render_template('download.html')

# --- API for downloading
@app.route('/download', methods=['POST'])
def download_video():
    data = request.get_json()
    url = data.get('url')
    mode = data.get('mode', 'video')   # "video" or "audio"
    quality = data.get('quality', 'best')  # video quality

    if not url:
        return jsonify({'success': False, 'error': 'No URL provided'}), 400

    url = clean_url(url)

    # Default options
    ydl_opts = {
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        'quiet': True,
    }

    # Audio mode
    if mode == 'audio':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        # Video mode with quality selection
        if quality == '360p':
            ydl_opts.update({'format': 'bestvideo[height<=360]+bestaudio/best'})
        elif quality == '720p':
            ydl_opts.update({'format': 'bestvideo[height<=720]+bestaudio/best'})
        elif quality == '1080p':
            ydl_opts.update({'format': 'bestvideo[height<=1080]+bestaudio/best'})
        else:  # best available
            ydl_opts.update({'format': 'best'})

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = info['filepath']

        if not os.path.exists(filename):
            return jsonify({'success': False, 'error': 'Download failed, file not found'}), 500

        return send_file(filename, as_attachment=True)
    except Exception as e:
        print("Download error:", str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

# --- API for Instagram downloading
@app.route('/instagram-download', methods=['POST'])
def instagram_download():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'success': False, 'error': 'No URL provided'}), 400

    ydl_opts = {
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        'quiet': True,
        'format': 'best',
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        if not os.path.exists(filename):
            return jsonify({'success': False, 'error': 'Download failed, file not found'}), 500
        return send_file(filename, as_attachment=True)
    except Exception as e:
        print("Instagram download error:", str(e))
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1000)
