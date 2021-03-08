import collections
import contextlib
import sys
import os
import wave
import argparse
from shutil import copyfile, copytree
import webrtcvad

AGGRESSIVENESS = 3

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--inputDir',
        dest='inputdir',
        default=None)
    parser.add_argument(
        '--outputDir',
        dest='outputdir',
        default=None)
    parser.add_argument(
        '--headSilence',
        dest='headsilence',
        type=int,
        default=50)
    parser.add_argument(
        '--tailSilence',
        dest='tailsilence',
        type=int,
        default=100)
    
    args, _ = parser.parse_known_args()
    return args

def read_wave(path):
    """Reads wave file.

    Takes the path, and returns (PCM audio data, sample rate).
    """
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


def write_wave(path, audio, sample_rate, headSilBuffer, tailSilBuffer):
    """Writes a .wav file.

    Takes path, PCM audio data, and sample rate.
    """
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


class Frame(object):
    """Represents a "frame" of audio data."""
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data.

    Args:
        frame_duration_ms: The desired frame duration in milliseconds.
        audio: The PCM data.
        sample_rate: The sample rate
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n


def vad_collector(sample_rate, vad, frames):
    """Filters out non-voiced audio frames.

    Args:
        sample_rate: The audio sample rate, in Hz.
        vad: An instance of webrtcvad.Vad.
        frames: A source of audio frames (sequence or generator).

    Returns: A generator that yields PCM audio data.
    """

    voiced_frames = []
    for idx, frame in enumerate(frames):
        is_speech = vad.is_speech(frame.bytes, sample_rate)
        if is_speech:
            voiced_frames.append(frame)

    return b''.join([f.bytes for f in voiced_frames])


def voiced_frames_expand(voiced_frames, duration=2):
    total = duration * 8000 * 2
    expanded_voiced_frames = voiced_frames
    while len(expanded_voiced_frames) < total:
        expand_num = total - len(expanded_voiced_frames)
        expanded_voiced_frames += voiced_frames[:expand_num]

    return expanded_voiced_frames


def filter(wav_dir, out_dir, headSilBuffer, tailSilBuffer, expand=False):
    '''Apply vad with wave file.

    Args:
        wav_dir: The directory of input wave files.
        out_dir: The directory that contains the voiced audio.
        headSilBuffer: The head silence length of the audios.
        tailSilBuffer: The tail silence length of the audios.
        expand: Expand the frames or not, default False.
    '''
    inputfiles = os.listdir(wav_dir)
    for file in inputfiles:
        if file.find('.wav') != -1:
            wavpath = os.path.join(wav_dir, file)
            audio, sample_rate = read_wave(wavpath)
            vad = webrtcvad.Vad(AGGRESSIVENESS)
            frames = frame_generator(30, audio, sample_rate)
            frames = list(frames)
            voiced_frames = vad_collector(sample_rate, vad, frames)
            voiced_frames = voiced_frames_expand(voiced_frames, 2) if expand else voiced_frames
            import pdb
            pdb.set_trace()
            wav_name = wavpath.split('/')[-1]
            save_path = os.path.join(out_dir, wav_name)
            write_wave(save_path, voiced_frames, sample_rate, headSilBuffer, tailSilBuffer)


def main():
    in_dir = 'bn-BD_waves/denoise_waves'
    out_dir = 'bn-BD_waves/denoise_waves_rmsil'
    filter(in_dir, out_dir, expand=False)


if __name__ == '__main__':
    args = get_arguments()
    inputDir = args.inputdir
    outputDir = args.outputdir
    headSilBuffer = args.headsilence
    tailSilBuffer = args.tailsilence
    filter(inputDir, outputDir, headSilBuffer, tailSilBuffer, expand=False)
