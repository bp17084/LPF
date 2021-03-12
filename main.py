# -*- coding: utf-8 -*-
import wave
import numpy as np
import matplotlib.pyplot as plt
import struct
import math



#sinc関数
def sinc(x):
    if x == 0.0: return 1.0
    else: return np.sin(x) / x

def printWaveInfo(wf):
    """WAVEファイルの情報を取得"""
    print( "チャンネル数:", wf.getnchannels())
    print ("サンプル幅:", wf.getsampwidth())
    print ("サンプリング周波数:", wf.getframerate())
    print ("フレーム数:", wf.getnframes())
    print ("パラメータ:", wf.getparams())
    print ("長さ（秒）:", float(wf.getnframes()) / wf.getframerate())

# waveファイルの読み込み
def load_wave(filename):
    wr = wave.open(filename, "rb")
    print("元ファイル")
    printWaveInfo(wr)
    print("")
    
    channel = wr.getnchannels()
    width = wr.getsampwidth()
    fs = wr.getframerate()
    rdata = wr.readframes(wr.getnframes())
    data = np.frombuffer(rdata, dtype="int16")/32768.0
    return data, channel, width, fs, 
 
# waveファイルへ保存
def save_wave(data, bit, fs, channel, filename):
    maxvalue = np.max(np.abs(data))
    g = [int(v/maxvalue * 32767.0) for v in data]
    g = struct.pack("h" * len(g), *g)
    wf = wave.open(filename, "w")
    wf.setnchannels(channel)
    wf.setsampwidth(bit)
    wf.setframerate(fs)
    wf.writeframes(g)
    wf.close()

    wf = wave.open(filename, "rb")
    print("low-pass")
    printWaveInfo(wf)
    
 
# ローパスフィルタ

def LPF(fe, delta):
    """ローパスフィルタを設計、fe:エッジ周波数、delta:遷移帯域幅"""
    # 遷移帯域幅を満たすフィルタ係数の数を計算
    # N+1が奇数になるように調整が必要
    N = round(3.1 / delta) - 1
    if (N + 1) % 2 == 0:
        N += 1
    
    N = int(N)

    # フィルタ係数を求める
    b = []
    
    for i in range(-N//2, N//2 + 1):
        b.append(2.0 * fe * sinc(2.0 * math.pi * fe * i))

    

    # ハニング窓関数をかける（窓関数法）
    hanningWindow = np.hanning(N + 1)
    for i in range(len(b)):
        b[i] *= hanningWindow[i]
    
    return b
 
# FIRフィルタ(元信号, フィルタ係数)
def fir(g, b):
    gf = [0.0] * len(g)     # フィルタの出力信号
    N = len(b) - 1          # フィルタ係数の数
    for n in range(len(g)):
        for i in range(N+1):
            if n - i >= 0:
                gf[n] += b[i] * g[n-i]
    return gf
 
if __name__ == '__main__':

    filepath = "sample.wav"  #waveファイルのパス
    
    print(filepath)
    print("")

    data, channel, width, fs,  = load_wave(filepath)    # waveファイルの読み込み

    # LPFを設計
    fe = 2000.0 / fs        # 正規化したエッジ周波数
    delta = 100.0 / fs      # 正規化した遷移帯域幅
    b = LPF(fe, delta)
  
    firdata = fir(data, b)              # FIRフィルタ処理
    save_wave(firdata, width, fs, channel, "low-pass.wav")# waveファイルを保存