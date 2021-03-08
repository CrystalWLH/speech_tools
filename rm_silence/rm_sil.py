from pydub import AudioSegment
import os
import sys


def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):
    trim_ms = 0
    assert chunk_size > 0
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size
    return trim_ms



if __name__ == '__main__':
    wavdir = sys.argv[1]
    outdir = sys.argv[2]
    for root, dirs, files in os.walk(wavdir):
        for f in files:
            if f.find('wav') != -1:
                try:
                    sound = AudioSegment.from_file(os.path.join(root, f), format="wav")
                    start_trim = detect_leading_silence(sound)
                    end_trim = detect_leading_silence(sound.reverse())
                    silbuffer = 300 #ms
                    start_trim = max(start_trim - 50, 0)
                    end_trim = max(end_trim - 100, 0)
                    duration = len(sound)
                    # import pdb
                    # pdb.set_trace()
                    rmsil_sound = sound[start_trim:duration-end_trim]
                    rmsil_sound.export(os.path.join(outdir, f), format="wav")
                except:
                    print (f)


