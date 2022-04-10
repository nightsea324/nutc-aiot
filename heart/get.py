from os import path, mkdir, listdir, getcwd
import os
from flask import Flask, request, redirect, url_for
import json
import socket
from werkzeug.utils import secure_filename
from flask_cors import CORS
if __name__ == '__main__':
    UPLOAD_FOLDER = r'C:\Users\user\Documents\aiot\main\heart\data'
    ALLOWED_EXTENSIONS = set(['txt'])

    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
    CORS(app) # 跨域

    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


    @app.route('/', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            file = request.files['hrate']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                    filename))
                image_path = (os.path.join(app.config['UPLOAD_FOLDER'],
                                        filename))

                msg = {}
                # 判斷傳入路徑是否存在
                if os.path.isfile(image_path):
                    msg = {'status': 0}
                else:
                    msg = {'status': 1}

                msg = json.dumps(msg)
                return msg

        return 

    # start build server
    HOST = '127.0.0.1'
    PORT = 8080
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=8080)

    '''
                     <!doctype html>
                     <title>心跳</title>
                     <h1>心跳</h1>
                     <form action="" method=post enctype=multipart/form-data>
                       <p><input type=file name=hrate>
                          <input type=submit value=Upload>
                     </form>
                     '''