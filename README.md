# Video Upscaler

Video upscaling using OpenCV, FFMPEG and RIFE.

"Segments" allow for easy stopping and returning processing.
JSONs keep track of the process.

### Step 1: Split video into smaller segments

Depending on the length of the video file it is split into smaller segments.

### Step 2: Split segments into scenes

Each frame of the segment is compared to the next frame to find "scenes".

"Scenes" are changes in camera view, or other big perspective changes. Having scenes allow for individual modifications to each scene, and during RIFE it avoids odd morphings between schene changes.

### Step 3: Clean frames

Each frame is "cleaned", eg. edited for whitebalance, sharpening, etc.

### Step 4: Upscale

Each frame is upscaled.

### Step 5: RIFE

Double the FPS for the video.

### Step 6: Merge segments into new video

