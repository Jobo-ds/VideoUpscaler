"""
Imports & Setup

"""
import json
import ffmpeg

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
        "file_id": str(input_folder[6:])
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
            split frames = False,
            clean = false
            upscale = false
            merge = false
"""


def checkpointJson():
    json_dict = {
        "split video": False,
        "split frames": False,
        "clean": False,
        "upscale": False,
        "merge": False
    }
    return json_dict

"""
Split video into checkpoints
Checkpoints make it easier to redo part of a restoration process.
"""

def splitvideo(file, main_json_file):
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
        video = ffmpeg.input(file)
        video = ffmpeg.trim(stream=video, start=chk_start, end=chk_end)
        video = ffmpeg.setpts(stream=video, expr="PTS-STARTPTS")
        video = ffmpeg.output(video, folder + "/checkpoints/" + checkpoint_number + file[-4:])
        ffmpeg.run(video)
        chk_start = chk_start + checkpoint_duration
        if chk_end < file_duration:
            chk_end = chk_end + checkpoint_duration
        else:
            chk_end = file_duration
        i = i + 1





"""
Split a Checkpoint into frames
"""

# Update Checkpoint JSON

"""
Perform Cleaning of frames
"""

# Update Checkpoint JSON

"""
Perform Upscaling of cleaned frames
"""

# Update Checkpoint JSON

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
