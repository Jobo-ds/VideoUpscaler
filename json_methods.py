import json
import ffmpeg

"""
JSON Methods
"""

def mainJson(file, input_folder):
    probe = ffmpeg.probe(file)
    json_dict = {
        "duration": float(probe["streams"][0]["duration"]),
        "file size": int(probe["format"]["size"]),
        "resolution": str(probe["streams"][0]["width"]) + "x" + str(probe["streams"][0]["height"]),
        "aspect ratio": str(probe["streams"][0]["display_aspect_ratio"]),
        "segments": 0,
        "segments JSON": False,
        "segments video split": False,
        "segments scene split": False,
        "segments frame split": False,
        "segments frame clean": False,
        "segments frame upscale": False,
        "segments video merge": False,
        "avg segment duration" : 0,
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

def segmentJson():
    json_dict = {
        "split video": False,
        "split frames": False,
        "scenes sorted": False,
        "scenes upscaled": False,
        "scenes": 0,
    }
    return json_dict

def sceneJson():
    json_dict = {
        "stablized": False,
        "cleaned": False,
        "upscaled": False,
        "frames": 0,
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