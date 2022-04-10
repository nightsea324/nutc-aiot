import numpy as numpy 
import cv2
import os
from os import path, mkdir, listdir, getcwd

def crop_img(f):
    g = f.copy()
    crop_img = g[150:200,105:215]
    return crop_img

def scan_img(f):
    g = f.copy()
    nr,nc = f.shape[:2]
    # print(nr,nc)
    hsv = cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    R,G,Y,W,B = 0,0,0,0,0
    for x in range(nr):
        for y in range (nc):
            H = hsv[x,y,0] * 2
            S = hsv[x,y,1]/255 * 100
            V = hsv[x,y,2]/255 * 100
            if (H >= 0 and H <= 20 and 
                S >= 0 and S <= 100 and 
                V >= 0 and V <= 100):
                R = R + 1
            if (H >= 330 and  
                S >= 0 and S <= 100 and 
                V >= 0 and V <= 100):
                R = R + 1
            if (H >= 20 and H <= 80 and 
                    S >= 0 and S <= 100 and 
                    V >= 0 and V <= 100):
                Y = Y + 1 
            if (H >= 80 and H <= 160 and 
                    S >= 0 and S <= 100 and 
                    V >= 0 and V <= 100):
                G = G + 1 
            if (H >= 0 and H <= 360 and 
                    S >= 0 and S <= 20 and 
                    V >= 50 and V <= 100):
                W = W + 1 
            if (H >= 0 and H <= 360 and 
                    S >= 0 and S <= 100 and 
                    V >= 0 and V <= 50):
                B = B + 1 
    # print(R,Y,G,W,B)
    # red
    if (R > Y and R > G and R > W):
        return 1
    # yellow
    elif (Y > R and Y > G and Y > W):
        return 2
    # green
    elif (G > R and G > Y and G > W):
        return 3
    # white
    elif (W > R and W > Y and W > G):
        return 0
    else:
        return 0
    
def red_segmentation(f):
    g = f.copy()
    nr,nc = f.shape[:2]
    hsv = cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    for x in range(nr):
        for y in range (nc):
            H = hsv[x,y,0] * 2
            S = hsv[x,y,1]/255 * 100
            V = hsv[x,y,2]/255 * 100
            #if (V >= V1 and V <= V2):
            #    g[x,y,0]= g[x,y,1] = g[x,y,2] = 0
            if (H >= 0 and H <= 360 and 
                S >= 0 and S <= 100 and 
                V >= 85 and V <= 100):
               g[x,y,0] = 0
               g[x,y,1] = 0
               g[x,y,2] = 0
            elif (H >= 0 and H <= 40 and 
                S >= 0 and S <= 100 and 
                V >= 50 and V <= 100):
               g[x,y,0] = 255
               g[x,y,1] = 255
               g[x,y,2] = 255
            elif (H >= 320 and 
                S >= 0 and S <= 100 and 
                V >= 50 and V <= 100):
               g[x,y,0] = 255
               g[x,y,1] = 255
               g[x,y,2] = 255     
            #if not(H >= H1 and H <= H2 and S >= S1 and S <= S2 and V >= V1 and V <= V2):
            #   g[x,y,0]= g[x,y,1] = g[x,y,2] = 0
    return g

def green_segmentation(f):
    g = f.copy()
    nr,nc = f.shape[:2]
    hsv = cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    for x in range(nr):
        for y in range (nc):
            H = hsv[x,y,0] * 2
            S = hsv[x,y,1]/255 * 100
            V = hsv[x,y,2]/255 * 100
            if (H >= 0 and H <= 360 and 
                S >= 0 and S <= 100 and 
                V >= 85 and V <= 100):
               g[x,y,0] = 0
               g[x,y,1] = 0
               g[x,y,2] = 0
            elif (H >= 60 and H <= 180 and 
                S >= 0 and S <= 100 and 
                V >= 50 and V <= 100):
               g[x,y,0] = 255
               g[x,y,1] = 255
               g[x,y,2] = 255   
    return g

def yellow_segmentation(f):
    g = f.copy()
    nr,nc = f.shape[:2]
    hsv = cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    for x in range(nr):
        for y in range (nc):
            H = hsv[x,y,0] * 2
            S = hsv[x,y,1]/255 * 100
            V = hsv[x,y,2]/255 * 100
            if (H >= 0 and H <= 360 and 
                S >= 0 and S <= 100 and 
                V >= 0 and V <= 50):
               g[x,y,0] = 0
               g[x,y,1] = 0
               g[x,y,2] = 0
            elif (H >= 20 and H <= 80 and 
                S >= 0 and S <= 100 and 
                V >= 50 and V <= 100):
               g[x,y,0] = 255
               g[x,y,1] = 255
               g[x,y,2] = 255 
    return g

def save_img(tran_img, img_name):
    img_name = img_name.split(".jpg")[0]
    save_path = os.getcwd() + "/result/"

    if not os.path.isdir(save_path):
        os.makedirs(save_path)
    try:
        cv2.imwrite(save_path + "/" + str(img_name) + ".jpg", tran_img)
    except:
        exit()

def Transform(imagePath):
    fileName = ""
    pathSplit = imagePath.split('/')
    fileName = pathSplit[-1]
    img1 = cv2.imread(imagePath,-1)
    img2 = crop_img(img1)
    img3 = scan_img(img2)
    if(img3 == 1):
        img4 = red_segmentation(img1)
    if(img3 == 2):
        img4 = yellow_segmentation(img1)
    if(img3 == 3):
        img4 = green_segmentation(img1)
    if(img3 == 0):
        img4 = img1
    save_img(img4,fileName[:-4])
    cv2.waitKey(0)

if __name__ == "__main__":
    print()