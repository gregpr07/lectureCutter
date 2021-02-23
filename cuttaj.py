
import numpy as np
from moviepy.editor import *

import os

input_file, a, out_name = sys.argv[1:]
a = float(a)

clip = VideoFileClip(input_file)  # .subclip(0,1000)

# how many intervals in one a
b = 10
fps = 44000


y = clip.audio.to_soundarray(fps=fps)[:, 0]  # only get one of the soundvawes
y = np.abs(y)


def get_non_silent_parts(a, b, silence=0.01):
    a_frames = int(a * fps)

    # whether frames from i*a_frames:(i+1)*a_frames are sounded
    # which is equal to i-seconds:i+a-seconds
    sounds = []

    current = 0

    for i in range(0, len(y), a_frames):  # len(y)
        interval = y[i: i + a_frames]

        split_intervals = np.array(np.split(interval, b))

        means = split_intervals.mean(axis=1)

        silent = means < silence

        new_silent = np.all(silent)

        if not current:
            new_silent == 0

        sounds.append(new_silent)

        current = new_silent

        """ plt.plot(interval)
        plt.plot([(x+1/2)*a_frames/b for x in range(b)], means) """

    return np.invert(sounds)


def getSecondsTuples():
    sounds_array = get_non_silent_parts(a, b)
    areas = []

    current = False
    current_start = 0

    for i in range(len(sounds_array)):

        if sounds_array[i]:
            if not current:
                current_start = i
                current = True
        else:
            if current:
                areas.append((current_start*a, (i)*a))
            current = 0

    if current:
        areas.append((current_start*a, (len(sounds_array))*a))

    return areas


def ffmpeg_text():
    tups_array = getSecondsTuples()
    text = f"select='{'+'.join([f'between(t,{tup[0]},{tup[1]})' for tup in tups_array])}'"
    return text


def run_ffmpeg_script():
    text = ffmpeg_text()
    os.system(
        f"""ffmpeg -i {input_file} \
       -vf "{text},
            setpts=N/FRAME_RATE/TB" \
       -af "a{text},
            asetpts=N/SR/TB" -y {out_name}"""
    )


run_ffmpeg_script()
