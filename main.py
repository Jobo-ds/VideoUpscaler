"""
Imports
"""
import hashlib
import math

from video import *
from segments import *
from scenes import *
from json_methods import *

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
segment_folder = input_folder + "/" + "segments"
if not path.exists(segment_folder):
    os.makedirs(segment_folder, exist_ok=False)
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
Create Segments

File is split into "segments" to allow for easier stopping and returning of processing,
as well as redoing part of the process. 
"""

# Calculate number of segments
if file_info["segments"] == 0:
    if file_info["duration"] <= 120: # 2 minutes
        updateJSON(main_json_file, "segments", 1)
        updateJSON(main_json_file, "avg segment duration", False) # If there is only one segment it's False. Allows for specific treatment.
        print("Very short file detected (< 1 min.). Only using 1 segment.")
    elif file_info["duration"] <= 600: # 10 minutes
        avg_segmentDuration = 120
        segments = math.ceil(file_info["duration"] / avg_segmentDuration)
        updateJSON(main_json_file, "segments", segments)
        updateJSON(main_json_file, "avg segment duration", 120)
        print(f"Short file detected (< 10 min.). Using {segments} segments.")
    else:
        avg_segmentDuration = 300
        segments = math.ceil(file_info["duration"] / avg_segmentDuration)
        updateJSON(main_json_file, "segments", segments)
        updateJSON(main_json_file, "avg segment duration", 300)
        print(f"Long file detected (> 10 min.). Using {segments} segments.")

file_info = loadJSON(main_json_file)

# Create Segment JSONs
if file_info["segments JSON"] == False:
    i = 0
    while i < file_info["segments"]:
        segment_number = str(i).zfill(8)
        segment_json_file = segment_folder + "/" + segment_number + ".json"
        with open(segment_json_file, 'w', encoding='utf-8') as outfile:
            json_dict = segmentJson()
            json.dump(json_dict, outfile, indent=4, ensure_ascii=False)
        i = i + 1

# Update main JSON
updateJSON(main_json_file, "segments JSON", True)

"""
Split file into parts
"""

splitVideo(main_json_file)

"""
Process Segments
"""
# Split Segments into Frames
splitSegments(main_json_file)

# Split Segments into Scenes
findScenes(main_json_file)

# # Clean frames
# cleanFrames(main_json_file)
#
# # Upscale Frames
# upscaleFrames(main_json_file)
#
# # Merge Segments
# compileVideo(main_json_file)

# Quality Testing

# Test removal
#shutil.rmtree(input_folder)