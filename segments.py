from json_methods import *
import cv2
import os
from os import path
import numpy as np


"""
Split a Segment into frames
"""

def splitSegments(main_json_file):
    file_info = loadJSON(main_json_file)
    if not file_info["segments frame split"]:
        i = 0
        while i < file_info["segments"]:
            segment_number = str(i).zfill(8)
            file = file_info["folder"] + "/segments/" + segment_number + file_info["file type"]
            segment_info = loadJSON(file_info["folder"] + "/segments/" + segment_number + ".json")
            filename_length = 10
            if not segment_info["split frames"]:
                video = cv2.VideoCapture(file)
                frameNr = 0
                print(f"Writing segment {segment_number} to image frames...")
                while (True):
                    success, frame = video.read()
                    if success:
                        if not path.exists(file_info["folder"] + "/segments/" + segment_number):
                            os.makedirs(file_info["folder"] + "/segments/" + segment_number, exist_ok=False)
                        cv2.imwrite(file_info["folder"] + "/segments/" + segment_number + "/" + str(frameNr).zfill(filename_length) + ".jpg", frame)
                    else:
                        break
                    frameNr = frameNr + 1
                updateJSON(file_info["folder"] + "/segments/" + segment_number + ".json", "split frames", True)
                updateJSON(file_info["folder"] + "/segments/" + segment_number + ".json", "frames", frameNr)
            else:
                print(f"Segment {segment_number} already split into frames.")
            i = i + 1
        updateJSON(main_json_file, "segments frame split", True)
    else:
        print("All segments have already been split into frames...")

"""
Split a Segment into scenes
"""

def findScenes(main_json_file):
    # Setup file variables
    file_info = loadJSON(main_json_file)
    frame = 0
    if not file_info["segments scene split"]:
        i = 0
        while i < file_info["segments"]:
            segment_number = str(i).zfill(8)
            segment_folder = file_info["folder"] + "/segments/" + segment_number + "/"
            total_frames = len(os.listdir(segment_folder))
            j = 0
            while frame < total_frames - 1:


            #img1 = cv2.imread(frame + ".jpg")
            #img2 = cv2.imread(str(int(frame)+1))
            img1 = cv2.imread(segment_folder + "0000000109.jpg")
            img2 = cv2.imread(segment_folder + "0000000110.jpg")
            err = np.sum((img1.astype("float") - img2.astype("float")) ** 2)
            err /= float(img1.shape[0] * img1.shape[1])
            print (err)
            i = 10


