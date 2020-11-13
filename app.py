import operator
import os

import cv2
from flask import Flask, request, redirect, flash, render_template, url_for, send_from_directory

from werkzeug.utils import secure_filename

from recognize import recognize

UPLOAD_FOLDER = 'uploads'
ALLOWED_IMAGE_EXTENSIONS = ('png', 'jpg', 'jpeg')
ALLOWED_VIDEO_EXTENSIONS = ('avi', 'mp4')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


def allowed_file(filename, allowed_ext):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_ext


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/photo', methods=['POST', 'GET'])
def upload_photo():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
            filename = secure_filename(file.filename)
            os_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(os_file_path)
            return redirect(url_for('recognize_photo', file=filename))
        else:
            flash('No selected file')
            return redirect(request.url)
    else:
        return render_template('upload.html', file_type='Photo')

@app.route('/video', methods=['POST', 'GET'])
def upload_video():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS):
            filename = secure_filename(file.filename)
            os_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(os_file_path)
            return redirect(url_for('recognize_video', file=filename))
        else:
            flash('No selected file')
            return redirect(request.url)
    else:
        return render_template('upload.html', file_type='Video')


@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/recognize/photo/<file>', methods=['POST', 'GET'])
def recognize_photo(file):
    if request.method == 'POST':
        os_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)

        img = cv2.imread(os_file_path)
        x = int(float(request.form['x']))
        width = int(float(request.form['width']))
        y = int(float(request.form['y']))
        height = int(float(request.form['height']))
        img = img[y:y+height, x:x+width]
        string = recognize(img)
        if len(string) == 0:
            string = "NOT RECOGNIZED"
        return render_template('result_photo.html', result=string)
    else:
        return render_template('crop.html', image_source=file)


@app.route('/recognize/video/<file>', methods=['POST', 'GET'])
def recognize_video(file):
    if request.method == 'POST':
        os_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)

        cap = cv2.VideoCapture(os_file_path)
        results = []
        count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                if count % 10 == 0:
                    if frame is not None:
                        x = int(float(request.form['x']))
                        width = int(float(request.form['width']))
                        y = int(float(request.form['y']))
                        height = int(float(request.form['height']))
                        frame = frame[y:y + height, x:x + width]
                        result = recognize(frame)
                        if len(result) == 0:
                            result = "NOT RECOGNIZED"
                        results.append([len(results) + 1, result])
                        if len(results) >= 10:
                            break
                count += 1
            else:
                break
        return render_template('result_video.html', results=results)
    else:
        os_file_path = os_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
        cap = cv2.VideoCapture(os_file_path)
        ret, frame = cap.read()
        os_frame_path = os.path.join(app.config['UPLOAD_FOLDER'], 'frames', file+'.png')
        cv2.imwrite(os_frame_path, frame)
        # TODO replace with os.path.join
        return render_template('crop.html', image_source=f'frames/{file}.png')




if __name__ == '__main__':
    if not os.path.isdir(app.config['UPLOAD_FOLDER']):
        os.mkdir(app.config['UPLOAD_FOLDER'])
    if not os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], 'frames')):
        os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], 'frames'))
    app.run(host='0.0.0.0')
