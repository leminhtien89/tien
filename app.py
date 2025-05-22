from flask import Flask, render_template, request, send_file, redirect
from pytube import YouTube
import os

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    video_info = None
    formats = []
    if request.method == 'POST':
        url = request.form['url']
        try:
            yt = YouTube(url)
            streams = yt.streams
            video_info = {
                'title': yt.title,
                'thumbnail': yt.thumbnail_url,
                'length': yt.length,
                'url': url
            }
            # Lọc định dạng video & audio
            for s in streams.filter(progressive=True).order_by('resolution').desc():
                filesize_mb = round(s.filesize / (1024 * 1024), 2) if s.filesize else None
                formats.append({
                    'itag': s.itag,
                    'res': s.resolution or 'Audio',
                    'mime': s.mime_type,
                    'size': f"{filesize_mb} MB" if filesize_mb else "?"
                })
            # Thêm định dạng MP3
            audio = streams.filter(only_audio=True).first()
            if audio:
                filesize_mb = round(audio.filesize / (1024 * 1024), 2) if audio.filesize else None
                formats.append({
                    'itag': audio.itag,
                    'res': 'MP3',
                    'mime': 'audio/mp4',
                    'size': f"{filesize_mb} MB" if filesize_mb else "?"
                })
        except Exception as e:
            return f"Lỗi: {str(e)}"
    return render_template('index.html', video=video_info, formats=formats)

@app.route('/download')
def download_video():
    url = request.args.get('url')
    itag = request.args.get('itag')
    if not url or not itag:
        return redirect('/')
    yt = YouTube(url)
    stream = yt.streams.get_by_itag(itag)
    filepath = stream.download(output_path=DOWNLOAD_FOLDER)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
