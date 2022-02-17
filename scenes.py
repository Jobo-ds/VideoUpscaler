from json_methods import *
import cv2
import os
from os import path
import time
from datetime import datetime, timedelta


"""
Perform Cleaning of frames
"""

def cleanFrames(main_json_file):
    # Setup file variables
    file_info = loadJSON(main_json_file)
    if not file_info["segments frame clean"]:
        folder = file_info["folder"] + "/" + "segments"
        segments_total = file_info["segments"]
        # Setup Cleaning
        # White Balance
        wb = cv2.xphoto.createSimpleWB()
        wb.setP(1)
        wb.setOutputMax(190)
        i = 0
        while i < segments_total:
            segment_number = str(i).zfill(8)
            segment_info = loadJSON(folder + "/" + segment_number + ".json")
            filename_length = 10
            if segment_info["clean"] == False:
                frameNr = 0
                update_gui = True
                avg_process_time_list = []
                while frameNr < segment_info["frames"]:
                    # Check if frame has already been processed
                    if not path.exists(folder + "/" + segment_number + "/" + "clean/" + str(frameNr).zfill(filename_length) + ".jpg"):
                        if update_gui:
                            now = datetime.now()
                            current_time = now.strftime("%H:%M:%S")
                            try:
                                avg_process_time = round(sum(avg_process_time_list) / len(avg_process_time_list), 3)
                                time_left = int((segment_info["frames"] - int(frameNr)) * avg_process_time)
                                time_left = str(timedelta(seconds=time_left))
                            except:
                                avg_process_time = "?"
                                time_left = "?"
                            print(
                                f"{current_time}: Cleaning... Current segment: {segment_number}, next frame to process: {frameNr}. Average process time: {avg_process_time} second(s). Time left (H:MM:SS): {time_left}.")
                            avg_process_time_list = []
                            update_gui = False
                        # Create folder
                        if not path.exists(folder + "/" + segment_number):
                            os.makedirs(folder + "/" + segment_number, exist_ok=False)
                        if not path.exists(folder + "/" + segment_number + "/clean"):
                            os.makedirs(folder + "/" + segment_number + "/clean", exist_ok=False)
                        frame = cv2.imread(folder + "/" + segment_number + "/" + str(frameNr).zfill(filename_length) + ".jpg")
                        if frameNr % 10 == 0: start = time.perf_counter()
                        result = wb.balanceWhite(frame)
                        cv2.imwrite(folder + "/" + segment_number + "/clean/" + str(frameNr).zfill(filename_length) + ".jpg", result)
                        if frameNr % 10 == 0: end = time.perf_counter()
                        if frameNr % 10 == 0: avg_process_time_list.append(float(end)-float(start))
                        if frameNr % 49 == 0: update_gui = True
                    frameNr = frameNr + 1
                updateJSON(folder + "/" + segment_number + ".json", "clean", True)
            i = i + 1
        updateJSON(main_json_file, "segments frame clean", True)
    else:
        print("All frames have already been cleaned...")


"""
Perform Upscaling of cleaned frames
"""

def upscaleFrames(main_json_file):
    # Setup file variables
    file_info = loadJSON(main_json_file)
    if not file_info["segments frame upscale"]:
        folder = file_info["folder"] + "/" + "segments"
        segments_total = file_info["segments"]
        # Setup Model
        model = "lapsrn"
        scale = 4
        modelPath = "models/" + model + "_x4.pb"
        sr = dnn_superres.DnnSuperResImpl_create()
        sr.readModel(modelPath)
        sr.setModel(model, scale)
        # Set CUDA backend and target to enable GPU inference
        sr.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        sr.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        print(f"Upscaling with model : {model} (x{scale})")
        i = 0
        while i < segments_total:
            segment_number = str(i).zfill(8)
            segment_info = loadJSON(folder + "/" + segment_number + ".json")
            filename_length = 10
            if segment_info["upscale"] == False:
                frameNr = 0
                update_gui = True
                avg_process_time_list = []
                while frameNr < segment_info["frames"]:
                    # Check if frame has already been processed
                    if not path.exists(folder + "/" + segment_number + "/" + "upscaled/" + str(frameNr).zfill(filename_length) + ".jpg"):
                        if update_gui:
                            now = datetime.now()
                            current_time = now.strftime("%H:%M:%S")
                            try:
                                avg_process_time = round(sum(avg_process_time_list) / len(avg_process_time_list), 3)
                                time_left = int((segment_info["frames"] - int(frameNr)) * avg_process_time)
                                time_left = str(timedelta(seconds=time_left))
                            except:
                                avg_process_time = "?"
                                time_left = "?"
                            print(
                                f"{current_time}: Upscaling... Current segment: {segment_number}, next frame to process: {frameNr}. Average process time: {avg_process_time} second(s). Time left (H:MM:SS): {time_left}.")
                            avg_process_time_list = []
                            update_gui = False
                        # Create folder
                        if not path.exists(folder + "/" + segment_number):
                            os.makedirs(folder + "/" + segment_number, exist_ok=False)
                        if not path.exists(folder + "/" + segment_number + "/upscaled"):
                            os.makedirs(folder + "/" + segment_number + "/upscaled", exist_ok=False)
                        frame = cv2.imread(folder + "/" + segment_number + "/clean/" + str(frameNr).zfill(filename_length) + ".jpg")
                        if frameNr % 10 == 0: start = time.perf_counter()
                        result = sr.upsample(frame)
                        cv2.imwrite(folder + "/" + segment_number + "/upscaled/" + str(frameNr).zfill(filename_length) + ".jpg", result)
                        if frameNr % 10 == 0: end = time.perf_counter()
                        if frameNr % 10 == 0: avg_process_time_list.append(float(end)-float(start))
                        if frameNr % 49 == 0: update_gui = True
                    frameNr = frameNr + 1
                updateJSON(folder + "/" + segment_number + ".json", "upscale", True)
            i = i + 1
        updateJSON(main_json_file, "segments frame upscale", True)
    else:
        print("All frames have already been upscaled...")