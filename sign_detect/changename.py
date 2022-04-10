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
import random

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
        # 無法辨識類別，則回傳空值
        if len(signplace) == 0:
            return ''
        else:
            for i in range(len(signplace)):
                if signplace[i][0] == 'traffic light':
                    image_x = signplace[i][2]
                    label = signplace[i][0]
                    x, y, w, h = image_x
                    x1 = int(x) - int(w / 2)
                    y1 = int(y) - int(h / 2)
                    if x1 <= 0:
                        x1 = 0
                    if y1 <= 0:
                        y1 = 0
                    box = (label, x1, y1, w, h)
                    img = get_image(self.imagePath)
                    cropimg = crop_img(img, box)
                    save_img(cropimg, self.fileName[:-4])
                    if w >= h:
                        label = 'Sign'
                    elif h >= w:
                        label = 'Psign'
                    else:
                        label = 'error'
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
    if (R > 1000000):
        return 'red'
    # green
    else:
        return 'green'

def changename():
    path=r'C:\Users\user\Pictures\aiot\people_sign\Red' 
    files=os.listdir(path)
    print(files) 

    n=0
    for i in files:
        m = n + 787
        if ((m / 1000) >= 1):
            newname = os.path.join(path,str(m) + '-PSign-Red' + '.JPG')
        elif ((m / 1000) < 1 and (m / 100) >= 1):
            newname = os.path.join(path,'0' + str(m) + '-PSign-Red' + '.JPG')
        elif ((m / 100) < 1 and (m / 10) >= 1):
            newname = os.path.join(path,'00' + str(m) + '-PSign-Red' + '.JPG')
        elif ((m / 10) < 1):
            newname = os.path.join(path,'000' + str(m) + '-PSign-Red' + '.JPG')

        oldname=os.path.join(path,files[n])
        os.rename(oldname,newname)
        print(oldname+'>>>'+newname)
        n=n+1

if __name__ == '__main__':

    changename()

    # # 初始化GPU
    # d = detection()
    # UPLOAD_FOLDER = r'C:\Users\user\Pictures\aiot\people_sign'
    # ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'JPG'])

    # app = Flask(__name__)
    # app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    # app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
    # CORS(app) # 跨域

    # def allowed_file(filename):
    #     return '.' in filename and \
    #            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

    # filepath = [] 
    # for filenames in os.listdir(UPLOAD_FOLDER):
    #     if not os.path.isdir(filenames):
    #         filepath.append(os.path.join(UPLOAD_FOLDER,filenames))

    # resultpath = r'C:\Users\user\Documents\aiot\main\aiot_v2\result3.txt'
    # files=os.listdir(UPLOAD_FOLDER)
    # print('count = ',len(files))
    # n=375
    # for i in files:
    #     m = n + 1
    #     result = d.sign_detection(os.path.join(UPLOAD_FOLDER,files[n]))
    #     if result == "":
    #         print("無法辨識")
    #     else:
    #         color = d.sign_recognition()
    #         print("color = ",color)
    #         if ((m / 1000) >= 1):
    #             newname = os.path.join(UPLOAD_FOLDER,str(m) + '-PSign-' + color + '.JPG')
    #         elif ((m / 1000) < 1 and (m / 100) >= 1):
    #             newname = os.path.join(UPLOAD_FOLDER,'0' + str(m) + '-PSign-' + color + '.JPG')
    #         elif ((m / 100) < 1 and (m / 10) >= 1):
    #             newname = os.path.join(UPLOAD_FOLDER,'00' + str(m) + '-PSign-' + color + '.JPG')
    #         elif ((m / 10) < 1):
    #             newname = os.path.join(UPLOAD_FOLDER,'000' + str(m) + '-PSign-' + color + '.JPG')

    #         oldname=os.path.join(UPLOAD_FOLDER,files[n])
    #         os.rename(oldname,newname)
    #         print(oldname+'>>>'+newname)
    #     n=n+1