"""
Imports
"""
import os
from os import path
import random
import shutil
import hashlib
import cv2
import math


from video import *

"""
Setup Process of file
"""

print("Put the input file into the input folder.")

GUI_cmd = False

file = "test_files/test_veryshort_file.mp4"
if GUI_cmd: file = input("Enter Filename: ")
file_type = file[-4:]

# Assign ID to file (md5 Hash, for now)
file_id = str(hashlib.md5(file.encode()).hexdigest())

# Create folders
input_folder = "input/" + file_id
if not path.exists(input_folder):
    os.makedirs(input_folder, exist_ok=False)
checkpoint_folder = input_folder + "/" + "checkpoints"
if not path.exists(checkpoint_folder):
    os.makedirs(checkpoint_folder, exist_ok=False)
output_folder = "output/" + file_id
if not path.exists(output_folder):
    os.makedirs(output_folder, exist_ok=False)

# Prepare Files
shutil.copy("input/" + file, input_folder + "/" + file_id + file_type)
file = input_folder + "/" + file_id + file_type
main_json_file = input_folder + "/" + file_id + ".json"

# Create Main File JSON
if not path.exists(main_json_file):
    with open(main_json_file, 'w', encoding='utf-8') as outfile:
        json_dict = mainJson(file, input_folder)
        json.dump(json_dict, outfile, indent=4, ensure_ascii=False)

file_info = loadJSON(main_json_file)

"""
Create Checkpoints
"""

# Calculate number of checkpoints
if file_info["checkpoints"] == 0:
    if file_info["duration"] <= 120: # 2 minutes
        updateJSON(main_json_file, "checkpoints", 1)
        updateJSON(main_json_file, "avg checkpoint duration", False) # If there is only one checkpoint it's False. Allows for specific treatment.
        print("Very short file detected (< 1 min.). Only using 1 checkpoint.")
    elif file_info["duration"] <= 600: # 10 minutes
        avg_checkpointDuration = 120
        checkpoints = math.ceil(file_info["duration"] / avg_checkpointDuration)
        updateJSON(main_json_file, "checkpoints", checkpoints)
        updateJSON(main_json_file, "avg checkpoint duration", 120)
        print(f"Short file detected (< 10 min.). Using {checkpoints} checkpoints.")
    else:
        avg_checkpointDuration = 300
        checkpoints = math.ceil(file_info["duration"] / avg_checkpointDuration)
        updateJSON(main_json_file, "checkpoints", checkpoints)
        updateJSON(main_json_file, "avg checkpoint duration", 300)
        print(f"Long file detected (> 10 min.). Using {checkpoints} checkpoints.")

file_info = loadJSON(main_json_file)

# Create Checkpoint JSONs
if file_info["checkpoints JSON"] == False:
    i = 0
    while i < file_info["checkpoints"]:
        checkpoint_number = str(i).zfill(3)
        checkpoint_json_file = checkpoint_folder + "/" + checkpoint_number + ".json"
        with open(checkpoint_json_file, 'w', encoding='utf-8') as outfile:
            json_dict = checkpointJson()
            json.dump(json_dict, outfile, indent=4, ensure_ascii=False)
        i = i + 1

# Update main JSON
updateJSON(main_json_file, "checkpoints JSON", True)

"""
Split file into parts
"""

splitVideo(main_json_file)

"""
Process Checkpoints
"""

# Split Checkpoints into Frames

splitCheckpoints(main_json_file)

# Create examples from first frame
#modelExamples(main_json_file)

# Upscale Frames
upscaleFrames(main_json_file)

# Merge Checkpoints

# Quality Testing

# Test removal
#shutil.rmtree(input_folder)