import cgi
import sys
from os import path, mkdir, listdir, getcwd
import os
from ObjectDetection.darknet import performDetect
import json
import socket
import cv2
from http.server import HTTPServer, BaseHTTPRequestHandler
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask_cors import CORS

class detection():
    Path = "./images/"
    imagePath = ""
    thresh = 0.5
    configPath = "./ObjectDetection/cfg/yolov4.cfg"
    weightPath = "./ObjectDetection/yolov4.weights"
    metaPath = "./ObjectDetection/cfg/coco.data"
    showImage = False
    makeImageOnly = True
    initOnly = True
    fileName = ""

    # 初始化神經網路
    def __init__(self):
        # initialize lincese detection
        performDetect(self.imagePath, self.thresh, self.configPath, self.weightPath, self.metaPath, self.showImage,
                      self.makeImageOnly, self.initOnly)

    # 辨識
    def sign_detection(self, image_path):
        # get image path
        self.imagePath = image_path

        # 分割照片路徑，以此取得檔案名稱
        pathSplit = self.imagePath.split('\\')

        # example.jpg => example
        self.fileName = pathSplit[-1]
        self.initOnly = False
        signplace = list(
            performDetect(self.imagePath, self.thresh, self.configPath, self.weightPath, self.metaPath, self.showImage,
                          self.makeImageOnly, self.initOnly))

        print('len=',len(signplace))
        print("signplace = ",signplace)

        # 無法辨識類別，則回傳空值
        if len(signplace) == 0:
            return ''
        else:
            for i in range(len(signplace)):
                print('i=',signplace[i])
                if signplace[i][0] == 'traffic light':
                    image_x = signplace[i][2]
                    label = signplace[i][0]
                    x, y, w, h = image_x
                    x1 = int(x - (w / 2))
                    y1 = int(y - (h / 2))
                    box = (label, x1, y1, w, h)
                    img = get_image(self.imagePath)
                    cropimg = crop_img(img, box)
                    save_img(cropimg, self.fileName[:-4])
                    if w >= h:
                        label = 'Sign'
                    elif h >= w:
                        label = 'Psign'
                    else:
                        return 'error'
                    return label
            return ''

    def sign_recognition(self):
        create_folder_path = os.getcwd() + '\\result\\' + self.fileName[:-4]

        sign_result = create_folder_path + '.jpg'

        # 建立辨識照片資料夾
        if not os.path.isdir(create_folder_path):

            try:
                mkdir(create_folder_path)
            except:
                print("建立資料夾失敗")
                exit()
        
        return scan_img(get_image(sign_result))

def crop_img(img,box):
    (_, x, y, w, h) = box
    w = int(w)
    h = int(h)
    crop_img = img[y:y + h, x:x + w]
    return crop_img

def save_img(img, img_name):
    img_name = img_name.split(".jpg")[0]
    save_path = os.getcwd() + "/result/"

    if not os.path.isdir(save_path):
        os.makedirs(save_path)
    try:
        cv2.imwrite(save_path + "/" + str(img_name) + ".jpg", img)
    except:
        exit()

def get_image(path):
    img = cv2.imread(path)

    return img

def scan_img(img):
    nr,nc = img.shape[:2]
    # print(nr,nc)
    hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    R,G,Y = 0,0,0
    for x in range(10,nr - 10):
        for y in range (10,nc - 10):
            H = hsv[x,y,0] * 2
            S = hsv[x,y,1]/255 * 100
            V = hsv[x,y,2]/255 * 100
            if (H >= 0 and H <= 40 and 
                S >= 0 and S <= 100 and 
                V >= 0 and V <= 100):
                R = R + 1
            if (H >= 330 and  
                S >= 0 and S <= 100 and 
                V >= 0 and V <= 100):
                R = R + 1
            if (H >= 40 and H <= 60 and 
                    S >= 0 and S <= 100 and 
                    V >= 0 and V <= 100):
                Y = Y + 1 
            if (H >= 60 and H <= 180 and 
                    S >= 0 and S <= 100 and 
                    V >= 0 and V <= 100):
                G = G + 1 
    print('red=',R)
    print('yellow=',Y)
    print('green=',G)
    # red
    if (R > 20000):
        return 'red'
    # green
    elif (G > 20000):
        return 'green'
    else:
        return '無法辨識'

if __name__ == '__main__':
    # 初始化GPU
    d = detection()
    UPLOAD_FOLDER = r'C:\Users\user\Documents\aiot\main\aiot_v2\images'
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'JPG'])

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
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],
                                       filename))
                image_path = (os.path.join(app.config['UPLOAD_FOLDER'],
                                           filename))

                msg = {}
                # 判斷傳入路徑是否存在
                if os.path.isfile(image_path):

                    # 辨識
                    result = d.sign_detection(image_path) 
                    print('result=',result)
                    if result == "":
                        msg = {'status': 1, 'message': '無法辨識', 'data': 'null'}
                    else:
                        color = d.sign_recognition()
                        msg = {'status': 0, 'message': '正確', 'data': result,'data2': color}
                else:
                    msg = {'status': 2, 'message': '照片路徑錯誤，或是照片不存在', 'data': ''}

                msg = json.dumps(msg)
                return msg

        return '''
                     <!doctype html>
                     <title>Upload new File</title>
                     <h1>上傳檔案</h1>
                     <form action="" method=post enctype=multipart/form-data>
                       <p><input type=file name=file>
                          <input type=submit value=Upload>
                     </form>
                     '''

    # start build server
    HOST = '127.0.0.1'
    PORT = 8080
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=8080)