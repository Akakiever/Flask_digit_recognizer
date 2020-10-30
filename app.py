import operator
import os

import cv2
from flask import Flask, request, redirect, flash, render_template

from werkzeug.utils import secure_filename

from recognize import recognize

UPLOAD_FOLDER = 'tmp_uploads'
ALLOWED_IMAGE_EXTENSIONS = ('png', 'jpg', 'jpeg')
ALLOWED_VIDEO_EXTENSIONS = ('avi')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


def allowed_file(filename, allowed_ext):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_ext

def allowed_video_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/photo', methods=['POST', 'GET'])
def recognize_photo():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
            filename = secure_filename(file.filename)
            os_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(os_file_path)

            img = cv2.imread(os_file_path)
            string = recognize(img)

            if len(string) == 0:
                string = "NOT RECOGNIZED"
            os.remove(os_file_path)
            return render_template('result.html', result=string)
    else:
        return render_template('upload.html', file_type='Photo')

@app.route('/video', methods=['POST', 'GET'])
def video():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS):
            filename = secure_filename(file.filename)
            os_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(os_file_path)

            cap = cv2.VideoCapture(os_file_path)
            results = {}
            while cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    if frame is not None:
                        result = recognize(frame)
                        if len(result) > 0:
                            if result in results:
                                results[result] += 1
                            else:
                                results.update({result: 1})
                else:
                    break

            if len(results) > 0:
                string = max(results.items(), key=operator.itemgetter(1))[0]
            else:
                string = "NOT RECOGNIZED"
            os.remove(os_file_path)
            return render_template('result.html', result=string)
    else:
        return render_template('upload.html', file_type='Video')




if __name__ == '__main__':
    app.run(debug=True)
