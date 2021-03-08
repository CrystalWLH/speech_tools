import os
import wave
from time import sleep
import numpy as np
import sys
import argparse
from shutil import copyfile, copytree

SUCCESS = 0
FAIL = 1

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

def ZCR(curFrame):
    # Zero crossing rate
    tmp1 = curFrame[:-1]
    tmp2 = curFrame[1:]
    sings = (tmp1 * tmp2 <= 0)
    diffs = (tmp1 - tmp2) > 0.02
    zcr = np.sum(sings * diffs)
    return zcr


def STE(curFrame):
    # Short-term energy
    amp = np.sum(np.abs(curFrame))
    return amp

def dump_wave_file(wavefile, data, nchannels, sampwidth, framerate):
    fw = wave.open(wavefile, 'wb')
    fw.setnchannels(nchannels)
    fw.setsampwidth(sampwidth)
    fw.setframerate(framerate)
    fw.writeframes(data)
    fw.close()

class Vad(object):
    def __init__(self):
        # 初始短时能量高门限
        self.amp1 = 140
        # 初始短时能量低门限
        self.amp2 = 120
        # 初始短时过零率高门限
        self.zcr1 = 10
        # 初始短时过零率低门限
        self.zcr2 = 5
        # 允许最大静音长度
        self.maxsilence = 100
        # 语音的最短长度
        self.minlen = 40
        # 偏移值
        self.offsets = 40
        self.offsete = 40
        # 能量最大值
        self.max_en = 20000
        # 初始状态为静音
        self.status = 0
        self.count = 0
        self.silence = 0
        self.frame_len = 256
        self.frame_inc = 128
        self.cur_status = 0
        self.frames = []
        # 数据开始偏移
        self.frames_start = []
        self.frames_start_num = 0
        # 数据结束偏移
        self.frames_end = []
        self.frames_end_num = 0
        # 缓存数据
        self.cache_frames = []
        self.cache = ""
        # 最大缓存长度
        self.cache_frames_num = 0
        self.end_flag = False
        self.wait_flag = False
        self.on = True
        self.callback = None
        self.callback_res = []
        self.callback_kwargs = {}

    def clean(self):
        self.frames = []
        # 数据开始偏移
        self.frames_start = []
        self.frames_start_num = 0
        # 数据结束偏移
        self.frames_end = []
        self.frames_end_num = 0
        # 缓存数据
        self.cache_frames = []
        # 最大缓存长度
        self.cache_frames_num = 0
        self.end_flag = False
        self.wait_flag = False

    def speech_status(self, amp, zcr):
        status = 0
        # 0= 静音， 1= 可能开始, 2=确定进入语音段
        if self.cur_status in [0, 1]:
            # 确定进入语音段
            if amp > self.amp1:
                status = 2
                self.silence = 0
                self.count += 1
            # 可能处于语音段
            elif amp > self.amp2 or zcr > self.zcr2:
                status = 1
                self.count += 1
            # 静音状态
            else:
                status = 0
                self.count = 0
                self.count = 0
        # 2 = 语音段
        elif self.cur_status == 2:
            # 保持在语音段
            if amp > self.amp2 or zcr > self.zcr2:
                self.count += 1
                status = 2
            # 语音将结束
            else:
                # 静音还不够长，尚未结束
                self.silence += 1
                if self.silence < self.maxsilence:
                    self.count += 1
                    status = 2
                # 语音长度太短认为是噪声
                elif self.count < self.minlen:
                    status = 0
                    self.silence = 0
                    self.count = 0
                # 语音结束
                else:
                    status = 3
                    self.silence = 0
                    self.count = 0
        return status

def read_file_data(filename):
    """
    input: file name
    output: (Channel number, Digitalizing bit, Sampling, Data)
    """
    read_file = wave.open(filename, "r")
    params = read_file.getparams()
    nchannels, sampwidth, framerate, nframes = params[:4]
    data = read_file.readframes(nframes)
    return nchannels, sampwidth, framerate, data

class FileParser(Vad):
    def __init__(self):
        self.block_size = 256
        Vad.__init__(self)


    def get_sil_idx(self, filename, outfile, headSilBuffer, tailSilBuffer):
        if not os.path.isfile(filename):
            print("file %s does not exist." % filename)
            return FAIL
        nchannels, sampwidth, framerate, datas = read_file_data(filename)
        wavdata = np.frombuffer(datas, dtype=np.int16)
        oriwavdata = wavdata
        wavdata = wavdata * 1.0 / self.max_en
        #frame len 75ms
        framelen = 0.075 * framerate
        #begin sil idx
        begin_sil_idx = 0
        for i in range(0, wavdata.shape[0], int(framelen)):
            tmpdata = wavdata[i:(i+int(framelen))]
            tmpzcr = ZCR(tmpdata)
            tmpamp = STE(tmpdata) ** 2
            tmpres = self.speech_status(tmpamp, tmpzcr)
            if tmpres == 1 or tmpres == 2:
                print ("begin sil time: {}s".format(float(i)/float(framerate)))
                begin_sil_idx = max(0, int(i - framelen))
                break
        #end sil idx
        end_sil_idx = wavdata.shape[0]
        for i in range(wavdata.shape[0], 0, -1 * int(framelen)):
            tmpdata = wavdata[(i-int(framelen)):i]
            tmpzcr = ZCR(tmpdata)
            tmpamp = STE(tmpdata) ** 2
            tmpres = self.speech_status(tmpamp, tmpzcr)
            if tmpres == 1 or tmpres == 2:
                print ("end sil time: {}s".format(float(i)/float(framerate)))
                end_sil_idx = min(wavdata.shape[0], int(i+framelen))
                break

        #begin pading 100ms sil, end padding 50ms sil
        headSil = float(headSilBuffer) / 1000.0
        tailSil = float(tailSilBuffer) / 1000.0
        pad_begin_sil_idx = max(0, begin_sil_idx-int(headSil*framelen))
        pad_end_sil_idx = min(wavdata.shape[0], end_sil_idx+int(tailSil*framelen))
        dump_wave_file(outfile, oriwavdata[pad_begin_sil_idx:pad_end_sil_idx].tostring(), nchannels, sampwidth, framerate)


def rm_waves_slience(inputdir, outputdir, headSilBuffer, tailSilBuffer):
    inputfiles = os.listdir(inputdir)
    stream_test = FileParser()
    for file in inputfiles:
        if file.find('.wav') != -1:
            wave_path = os.path.join(inputdir, file)
            save_path = os.path.join(outputdir, file)
            stream_test.get_sil_idx(wave_path, save_path, headSilBuffer, tailSilBuffer)

if __name__ == "__main__":
    args = get_arguments()
    inputDir = args.inputdir
    outputDir = args.outputdir
    headSilBuffer = args.headsilence
    tailSilBuffer = args.tailsilence

    rm_waves_slience(inputDir, outputDir, headSilBuffer, tailSilBuffer)
