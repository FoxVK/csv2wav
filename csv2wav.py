#!/bin/python3
__author__ = 'Pavel Kovar fox@vsetin.org'

import wave
import struct
from sys import argv, exit

if len(argv) != 3:
    print("Usage:", argv[0], "input.csv output.wav")
    exit(-1)

csv_name = argv[1]
wav_name = argv[2]

try:
    csv = open(csv_name)
except IOError as e:
    print("Can not open input file \"" + csv_name + "\" - " + e.strerror)
    exit(-1)

try:
    wav = wave.open(wav_name, 'wb')
except IOError as e:
    print("Can not open output file \"" + wav_name + "\" - " + e.strerror)
    exit(-1)

'''
Time [s], Analyzer Name, Decoded Protocol Result
0.000011500000000,I2S / PCM,Ch 2: '0' (0x0000)
0.000021750000000,I2S / PCM,Ch 1: '0' (0x0000)
0.000032250000000,I2S / PCM,Ch 2: '0' (0x0000)
0.000042500000000,I2S / PCM,Ch 1: '0' (0x0000)
0.000053000000000,I2S / PCM,Ch 2: '0' (0x0000)
'''

sample = struct.Struct('H')
data = b''

chans = 1
wffch = True   #waiting for first chan

time_of_first = None
time_of_last = None
smpl_cnt = 0

for line in csv:
    cs = line.split(',')
    if len(cs) != 3:
        continue
    if cs[1].startswith('I2S'):
        ch, val = cs[2].split('(0x')
        chn = int(ch[3])

        if chans < chn:
            chans = chn

        if wffch and chn != 1:
            continue
        wffch = False

        if chn == 1:
            time_of_last = float(cs[0])
            if time_of_first is None:
                time_of_first = time_of_last
            smpl_cnt += 1

        data += sample.pack(int(val[:-2], 16))


csv.close()

rates = [8000, 11025, 16000, 22050, 32000, 44100, 48000, 88200, 96000, 176400, 192000]
measured_rate = smpl_cnt / (time_of_last - time_of_first)
rate = min(rates, key=lambda x: abs(x-measured_rate))
print('Length:', int(time_of_last-time_of_first), "Rate:", rate, "Channels:", chans)

wav.setframerate(rate)
wav.setnchannels(chans)
wav.setsampwidth(2)
wav.writeframes(data)
wav.close()