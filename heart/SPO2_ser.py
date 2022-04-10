
import os

folder_path = r'C:\Users\user\Documents\aiot\main\heart\data'
folder_content = os.listdir(folder_path)
print( folder_path + '資料夾內容：')
for item in folder_content:
    if os.path.isdir(folder_path + '\\' + item):
        print('資料夾：' + item)
    elif os.path.isfile(folder_path + '\\' + item):
        print('檔案：' + item)
    else:
        print('無法辨識：' + item)