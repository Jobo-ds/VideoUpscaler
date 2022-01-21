"""
Imports & Setup

"""
import json
import ffmpeg
import cv2
from cv2 import dnn_superres
import os
from os import path
import time


"""
Utilities
"""

"""
Create Main file JSON
 - File Integrity Details
    - File length
    - File Size
    - Video codec
    - Frames Per Second
    - Audio codec
    - Bitrate
 - Process booleans allow for start/stopping process:
        One boolean for each Checkpoint.
"""


def mainJson(file, input_folder):
    probe = ffmpeg.probe(file)
    json_dict = {
        "duration": float(probe["streams"][0]["duration"]),
        "file size": int(probe["format"]["size"]),
        "resolution": str(probe["streams"][0]["width"]) + "x" + str(probe["streams"][0]["height"]),
        "aspect ratio": str(probe["streams"][0]["display_aspect_ratio"]),
        "checkpoints": 0,
        "checkpoints JSON": False,
        "avg checkpoint duration" : 0,
        "checkpoints completed": [],
        "vCodec": str(probe["streams"][0]["codec_name"]),
        "vBitrate": int(probe["streams"][0]["bit_rate"]),
        "FPS": str(probe["streams"][0]["r_frame_rate"]),
        "aCodec": str(probe["streams"][1]["codec_name"]),
        "sample rate": int(probe["streams"][1]["sample_rate"]),
        "Bitrate": int(probe["streams"][1]["bit_rate"]),
        "folder": str(input_folder),
        "file_id": str(input_folder[6:]),
        "file type": str(file[-4:]),
        "Super Resolution Model": "None"
    }
    return json_dict


def loadJSON(main_json_file):
    with open(main_json_file, "r") as content:
        json_object = json.load(content)
    return json_object


def updateJSON(file, variable, value):
    input_file = open(file, "r")
    json_object = json.load(input_file)
    input_file.close()
    json_object[variable] = value
    output_file = open(file, "w")
    json.dump(json_object, output_file, indent=4, ensure_ascii=False)
    output_file.close()

"""
Create Checkpoint JSON
 - Process booleans allow for start/stopping process:
            split video = False
            Does this checkpoint video file exist - eg. has the main file been split into checkpoints.
            split frames = False,
            Has this video checkpoint been split into frames?
            clean = False
            Has ALL the frames been cleaned with filters?
            upscale = False
            Has ALL the frames been upscaled in resolution?
            merge = False
            
"""


def checkpointJson():
    json_dict = {
        "split video": False,
        "split frames": False,
        "clean": False,
        "upscale": False,
        "merge": False,
        "frames": 0,
    }
    return json_dict

"""
Split video into checkpoints
Checkpoints make it easier to redo part of a restoration process.
"""

def splitVideo(main_json_file):
    file_info = loadJSON(main_json_file)
    checkpoints = file_info["checkpoints"]
    file_duration = file_info["duration"]
    checkpoint_duration = file_info["avg checkpoint duration"]
    folder = file_info["folder"]
    chk_start = 0
    chk_end = checkpoint_duration
    i = 0
    while i < checkpoints:
        checkpoint_number = str(i).zfill(3)
        checkpoint_json = loadJSON(file_info["folder"] + "/checkpoints/" + checkpoint_number + ".json")
        if not checkpoint_json["split video"]:
            video = ffmpeg.input(folder + "/" + file_info["file_id"] + file_info["file type"])
            video = ffmpeg.trim(stream=video, start=chk_start, end=chk_end)
            video = ffmpeg.setpts(stream=video, expr="PTS-STARTPTS")
            video = ffmpeg.output(video, folder + "/checkpoints/" + checkpoint_number + file_info["file type"])
            ffmpeg.run(video)
            chk_start = chk_start + checkpoint_duration
            if chk_end < file_duration:
                chk_end = chk_end + checkpoint_duration
            else:
                chk_end = file_duration
            updateJSON(folder + "/checkpoints/" + checkpoint_number + ".json", "split video", True)
        i = i + 1
    updateJSON(folder + "/checkpoints/" + checkpoint_number + ".json", "split video", True)

"""
Split a Checkpoint into frames
"""

def splitCheckpoints(main_json_file):
    file_info = loadJSON(main_json_file)
    i = 0
    while i < file_info["checkpoints"]:
        checkpoint_number = str(i).zfill(3)
        file = file_info["folder"] + "/checkpoints/" + checkpoint_number + file_info["file type"]
        checkpoint_info = loadJSON(file_info["folder"] + "/checkpoints/" + checkpoint_number + ".json")
        if not checkpoint_info["split frames"]:
            video = cv2.VideoCapture(file)
            frameNr = 0
            print(f"Writing frames from checkpoint {checkpoint_number}")
            while (True):
                success, frame = video.read()
                if success:
                    if not path.exists(file_info["folder"] + "/checkpoints/" + checkpoint_number):
                        os.makedirs(file_info["folder"] + "/checkpoints/" + checkpoint_number, exist_ok=False)
                    cv2.imwrite(file_info["folder"] + "/checkpoints/" + checkpoint_number + "/" + str(frameNr) + ".jpg", frame)
                    updateJSON(file_info["folder"] + "/checkpoints/" + checkpoint_number + ".json", frameNr, False)
                else:
                    break
                frameNr = frameNr + 1
            updateJSON(file_info["folder"] + "/checkpoints/" + checkpoint_number + ".json", "split frames", True)
            updateJSON(file_info["folder"] + "/checkpoints/" + checkpoint_number + ".json", "frames", frameNr-1)
        else:
            print(f"Checkpoint {checkpoint_number} already split into frames.")
        i = i + 1

"""
Perform Cleaning of frames
"""

# Update Checkpoint JSON

"""
Perform Upscaling of cleaned frames
"""

# Create examples of available models.
def modelExamples(main_json_file):
    models = os.listdir("models")
    file_info = loadJSON(main_json_file)
    folder = file_info["folder"] + "/" + "checkpoints"
    for model in models:
        i = 0
        checkpoint_number = str(i).zfill(3)
        frameNr = 1
        frame = cv2.imread(folder + "/" + checkpoint_number + "/" + str(frameNr) + ".jpg")
        scale = model[-4:-3]
        modelName = str(model[:-6]).lower()
        if not path.exists(folder + "/" + checkpoint_number + "/" + "Examples/"):
            os.makedirs(folder + "/" + checkpoint_number + "/" + "Examples/", exist_ok=False)
        # Create simple resizes for comparison
        if not path.exists(folder + "/" + checkpoint_number + "/" + "Examples/" + str(frameNr) + "-comparison-" + model[:-3] + ".jpg"):
            img = cv2.imread(folder + "/" + checkpoint_number + "/" + str(frameNr) + ".jpg", cv2.IMREAD_UNCHANGED)
            width = int(img.shape[1] * int(scale)*100 / 100)
            height = int(img.shape[0] * int(scale)*100 / 100)
            dim = (width, height)
            resized_img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
            cv2.imwrite(folder + "/" + checkpoint_number + "/" + "Examples/" + str(frameNr) + "-comparison-x" + str(scale) + ".jpg", resized_img)
        # Run Model
        print(f"Using model : {model} (x{scale})")
        sr = dnn_superres.DnnSuperResImpl_create()
        modelPath = "models/" + model
        sr.readModel(modelPath)
        sr.setModel(modelName, int(scale))
        if not path.exists(folder + "/" + checkpoint_number + "/" + "Examples/" + str(frameNr) + "-upscale-" + model[:-3] + ".jpg"):
            start = time.perf_counter()
            result = sr.upsample(frame)
            cv2.imwrite(folder + "/" + checkpoint_number + "/" + "Examples/" + str(frameNr) + "-upscale-" + model[:-3] + ".jpg", result)
            end = time.perf_counter()
            process_time = end - start
            print(f"Process time: {process_time} seconds")


def upscaleFrames(main_json_file):
    # Setup file variables
    file_info = loadJSON(main_json_file)
    folder = file_info["folder"] + "/" + "checkpoints"
    checkpoints_total = file_info["checkpoints"]
    # Setup Model
    model = "lapsrn"
    scale = 4
    modelPath = "models/" + model
    sr = dnn_superres.DnnSuperResImpl_create()
    sr.readModel(modelPath)
    sr.setModel(model, scale)
    print(f"Upscaling with model : {model} (x{scale})")
    i = 0
    while i < checkpoints_total:
        checkpoint_number = str(i).zfill(3)
        checkpoint_info = loadJSON(folder + "/" + checkpoint_number + ".json")
        if checkpoint_info["upscale"] == False:
            frameNr = 0
            while frameNr < checkpoint_info["frames"]:
                if frameNr % 100 == 0:
                    print(f"Upscaling... Current checkpoint: {checkpoint_number}, next frame: {frameNr}")
                # Check if frame has already been processed
                if not path.exists(folder + "/" + checkpoint_number + "/" + str(frameNr) + "-upscale.jpg"):
                    # Create folder
                    if not path.exists(folder + "/" + checkpoint_number):
                        os.makedirs(folder + "/" + checkpoint_number, exist_ok=False)
                    frame = cv2.imread(folder + "/" + checkpoint_number + "/" + str(frameNr) + ".jpg")
                    result = sr.upsample(frame)
                    cv2.imwrite(folder + "/" + checkpoint_number + "/" + str(frameNr) + "-upscale.jpg", result)
                frameNr = frameNr + 1
            updateJSON(folder + "/" + checkpoint_number + ".json", "upscale", True)
        i = i + 1
    print("Framess have been upscaled.")

"""
Merge frames into Checkpoint again
"""

# Update Checkpoint JSON

"""
Quality Control - Creat JSON of new Checkpoint file)
"""

# Compare new Checkpoint file with original JSON file

# Update Checkpoint JSON

# Update Main file JSON
