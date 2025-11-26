# audio_tools/synthesizer.py
import numpy as np


class GranularSynth:
    """
    简单的颗粒合成引擎：
      - 从原音频中取粒度（grain），按一定 hop 重叠相加
      - 可用来做特殊效果 / 时长控制
    """

    def __init__(self, grain_size: int = 2048, hop_size: int = 512):
        self.grain_size = grain_size
        self.hop_size = hop_size

    def synthesize(self, audio: np.ndarray, rate: float = 1.0) -> np.ndarray:
        """
        简化版颗粒合成：
          rate 控制粒子前进速度（rate < 1 更慢，> 1 更快）
        """
        if rate <= 0:
            raise ValueError("rate 必须 > 0")

        grains = []
        pos = 0.0
        length = len(audio)

        while int(pos) + self.grain_size < length:
            grain = audio[int(pos): int(pos) + self.grain_size].copy()
            # 加一个汉宁窗，减小拼接处的突变
            grain *= np.hanning(len(grain))
            grains.append(grain)
            pos += self.hop_size * rate

        if not grains:
            return audio

        out_len = self.hop_size * (len(grains) - 1) + self.grain_size
        output = np.zeros(out_len, dtype=np.float32)

        for i, g in enumerate(grains):
            start = i * self.hop_size
            output[start: start + len(g)] += g.astype(np.float32)

        # 简单归一化，避免叠加后过载
        max_abs = np.max(np.abs(output)) + 1e-9
        output = output / max_abs * 0.95
        return output

    @staticmethod
    def crossfade(a: np.ndarray, b: np.ndarray, fade_len: int = 2048) -> np.ndarray:
        """
        高质量交叉渐变：连接两个音频 a, b。
        """
        fade_len = min(fade_len, len(a), len(b))
        if fade_len <= 0:
            return np.concatenate([a, b])

        # 前面是 a，后面是 b，中间 overlap 区做 crossfade
        left = a[:-fade_len]
        right = b[fade_len:]

        fade_out = a[-fade_len:]
        fade_in = b[:fade_len]

        t = np.linspace(0, 1, fade_len)
        cross = fade_out * (1 - t) + fade_in * t

        return np.concatenate([left, cross, right]).astype(np.float32)
