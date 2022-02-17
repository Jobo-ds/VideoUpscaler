"""
Imports & Setup

"""
from json_methods import *
import ffmpeg
import os
import shutil


"""
Split video into segments
"""

def splitVideo(main_json_file):
    file_info = loadJSON(main_json_file)
    segments = file_info["segments"]
    file_duration = file_info["duration"]
    segment_duration = file_info["avg segment duration"]
    folder = file_info["folder"]
    chk_start = 0
    chk_end = segment_duration
    if not file_info["segments video split"]:
        i = 0
        if segment_duration != False:
            while i < segments:
                segment_number = str(i).zfill(8)
                segment_json = loadJSON(file_info["folder"] + "/segments/" + segment_number + ".json")
                if not segment_json["split video"]:
                    video = ffmpeg.input(folder + "/" + file_info["file_id"] + file_info["file type"])
                    video = ffmpeg.trim(stream=video, start=chk_start, end=chk_end)
                    video = ffmpeg.setpts(stream=video, expr="PTS-STARTPTS")
                    video = ffmpeg.output(video, folder + "/segments/" + segment_number + file_info["file type"])
                    ffmpeg.run(video)
                    chk_start = chk_start + segment_duration
                    if chk_end < file_duration:
                        chk_end = chk_end + segment_duration
                    else:
                        chk_end = file_duration
                    updateJSON(folder + "/segments/" + segment_number + ".json", "split video", True)
                i = i + 1
                updateJSON(folder + "/segments/" + segment_number + ".json", "split video", True)
                print("Video successfully split into segments.")
        else:
            shutil.copy(folder + "/" + file_info["file_id"] + file_info["file type"], folder + "/" + "segments/00000000" + file_info["file type"])
            updateJSON(folder + "/segments/" + "00000000" + ".json", "split video", True)
            print("Video successfully split into segments.")
        updateJSON(main_json_file, "segments video split", True)
    else:
        print("Video has already been split into video segments...")


"""
Merge Segments into video file again
"""

def compileVideo(main_json_file):
    file_info = loadJSON(main_json_file)
    if not file_info["segments video merge"]:
        segments = file_info["segments"]
        folder = file_info["folder"]
        i = 0
        while i < segments:
            segment_number = str(i).zfill(8)
            frames = os.listdir(folder + "/" + "segments/" + segment_number + "/upscaled/")
            # This sucks, but its late.
            with open(folder + "/" + "segments/" + "temp_list.txt", 'w') as f:
                file_path = segment_number + "/upscaled/"
                for item in frames:
                    f.write("file " + file_path + "%s\n" % item)
            list_path = folder + "/" + "segments/" + "/temp_list.txt"
            fps = int(file_info["FPS"][:2])
            video = ffmpeg.input(list_path, r=fps, f='concat', safe='0')
            video = ffmpeg.output(video, folder + "/" + "segments/" + segment_number + "-upscaled" + file_info["file type"])
            ffmpeg.run(video)
            updateJSON(folder + "/" + "segments/" + segment_number + ".json", "merge", True)
            i = i + 1
        updateJSON(main_json_file, "segments video merge", True)
    else:
        print("All segments have already been merged into upscaled video files...")
    #if file_info["segments video merge"]:
        #MERGE ALL FILES

"""
Quality Control - Creat JSON of new Segment file)
"""

# Compare new Segment file with original JSON file

# Update Segment JSON

# Update Main file JSON
