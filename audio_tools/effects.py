# audio_tools/effects.py
import numpy as np
import scipy.signal as sps
import librosa


class Effects:
    """
    常用效果处理：
      - compressor: 动态范围控制（简单压缩器）
      - reverb: 简单混响（基于指数衰减的脉冲响应）
      - high_shelf: 简易高频提升/削减
    """

    def compressor(
        self,
        audio: np.ndarray,
        threshold_db: float = -20.0,
        ratio: float = 4.0,
    ) -> np.ndarray:
        """
        简单静态压缩器（无 attack/release）:
          - 超过阈值部分按 ratio 压缩
        """
        # 避免 0
        eps = 1e-9
        x = audio.astype(np.float32)
        mag = np.abs(x) + eps
        db = 20 * np.log10(mag)

        over = db - threshold_db
        gain_db = np.where(over > 0, -over * (1 - 1 / ratio), 0.0)
        gain = 10 ** (gain_db / 20.0)

        y = x * gain
        return y

    def reverb(
        self,
        audio: np.ndarray,
        sr: int,
        decay_time: float = 0.8,
        mix: float = 0.3,
    ) -> np.ndarray:
        """
        非常简单的混响：用指数衰减的脉冲响应做卷积。
        decay_time: 混响长度（秒）
        mix: dry/wet 比例（0~1）
        """
        ir_len = int(sr * decay_time)
        t = np.linspace(0, decay_time, ir_len)
        ir = np.exp(-3 * t / decay_time)  # 指数衰减
        ir /= np.max(np.abs(ir)) + 1e-9

        wet = sps.fftconvolve(audio, ir, mode="full")[: len(audio)]
        wet = wet.astype(np.float32)

        out = (1 - mix) * audio + mix * wet
        # 防止爆音，做个简单归一化
        max_abs = np.max(np.abs(out)) + 1e-9
        out = out / max_abs * 0.99
        return out

    def high_shelf(
        self,
        audio: np.ndarray,
        sr: int,
        cutoff: float = 4000.0,
        gain_db: float = 3.0,
    ) -> np.ndarray:
        """
        简易高频搁架滤波（shelf EQ）
        """
        # 使用 librosa 自带的 preemphasis 模拟一点高频提升
        # gain_db > 0 -> 高频提升；gain_db < 0 -> 高频削减（反向预加重）
        coef = 0.97
        if gain_db >= 0:
            y = librosa.effects.preemphasis(audio, coef=coef)
        else:
            # 反向操作，粗略实现高频削减
            y = librosa.effects.deemphasis(audio, coef=coef)
        return y.astype(np.float32)
