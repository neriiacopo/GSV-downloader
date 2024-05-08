# Next STEP: https://www.pyimagesearch.com/2016/01/11/opencv-panorama-stitching/.en

# Import google_streetview for the api module
import google_streetview.api
import shutil
import pandas as pd
import os 
from omnicv import fisheyeImgConv
import cv2
import numpy as np
import time

# Import locations
locations_df = pd.read_csv('data\dummy:data.csv')

# Select main folder for outputs
dir_out = "outputs/"

# Prepare folders
dir_temp = dir_out+"temp"
dir_imgs = dir_out+"imgs"
dir_panos = dir_out+"panos"

try:
    os.mkdir(dir_out)
    os.mkdir(dir_temp)
    os.mkdir(dir_imgs)
    os.mkdir(dir_panos)
except:
    pass


# Main loop through locations
for w in range(0,len(locations_df)) :
    location_w = str(locations_df.iloc[w][1]) + ',' + str(locations_df.iloc[w][0])
    location_id = format(w,"04d")

    try:
        # Nested loop for 360 view
        for i in range(0,6):
            # fitfh image to be top img
            if i == 4:
                pitch = 90
                heading = 0
            elif i == 5:
                pitch = -90
                heading = 0
            else:
                pitch = 0
                heading = 90*i

            # Define parameters for street view api
            params = [{
                'size': '640x640', # max 640x640 pixels
                'location': str(location_w),
                'heading': heading,
                'pitch': pitch,
                'fov': '90',
                'key': '' #>>>>>>>>>>>>>>>>>>>>>>>>>> place here your Google Street View api key <<<<<<<<<<<<<<<<<<<<<<<<<<<<<
            }]

            # Create a results object
            results = google_streetview.api.results(params)

            # Download images to directory 'downloads'
            dummypath = os.path.join(dir_temp, "gsv_0.jpg")
            results.download_links(os.path.join(dir_temp))

            # Rename temp
            filepath_temp = os.path.join(dir_temp, ("img_"+ str(i)+ ".jpg"))
            os.rename(dummypath, filepath_temp)
            # Store shots
            filepath_img = os.path.join(dir_imgs, ("img_"+ location_id + "_"+ str(i)+".jpg"))
            shutil.copyfile(filepath_temp, filepath_img)

        # Make panos for location
        imgs_paths = []

        for file in os.listdir(dir_temp):
            if file.endswith(".jpg"):
                path = os.path.join(dir_temp, file)
                imgs_paths.append(path)

        imgs = [] # initialized a list of images
        mask = cv2.imread('utils/mask.jpg', 0) # Load the mask

        for i in range(len(imgs_paths)):
            img = cv2.imread(imgs_paths[i])
            img_m = cv2.inpaint(img, mask, 1, cv2.INPAINT_NS)
            imgs.append(img_m)
            os.remove(imgs_paths[i])

        # Create Equirectangular
        cubemap = np.concatenate((
            np.flip(imgs[2],1), 
            imgs[1],
            imgs[0],
            np.flip(imgs[3],1),
            imgs[4],
            np.flip(imgs[5],0)), axis=1)

        outShape = [512, 1024]
        inShape = cubemap.shape[:2]
        mapper = fisheyeImgConv()

        equirect = mapper.cubemap2equirect(cubemap, outShape)
        filepath_pano = os.path.join(dir_panos, ("pano_"+ location_id + ".png"))
        cv2.imwrite(filepath_pano, equirect)

        print(w)
        
    except:
        print("missing image")
