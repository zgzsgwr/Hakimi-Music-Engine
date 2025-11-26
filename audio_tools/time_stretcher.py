# audio_tools/time_stretcher.py
import numpy as np
import librosa


class TimeStretcher:
    """
    时间相关处理：
      - time_stretch: 使用 phase vocoder 做时间拉伸（不变调）
    """

    def time_stretch(self, audio: np.ndarray, rate: float) -> np.ndarray:
        """
        时间拉伸：
          rate < 1.0 -> 变慢（变长）
          rate > 1.0 -> 变快（变短）
        使用 librosa.effects.time_stretch（内部就是 phase vocoder）。
        """
        if rate <= 0:
            raise ValueError("rate 必须 > 0")
        y = librosa.effects.time_stretch(audio, rate=rate)
        return y

    def stretch_with_pv(
        self,
        audio: np.ndarray,
        rate: float,
        n_fft: int = 2048,
        hop_length: int = 512,
    ) -> np.ndarray:
        """
        直接演示 phase vocoder 的版本（教学用）：
          STFT -> phase_vocoder -> iSTFT
        """
        if rate <= 0:
            raise ValueError("rate 必须 > 0")

        stft = librosa.stft(audio, n_fft=n_fft, hop_length=hop_length)
        stft_stretch = librosa.phase_vocoder(stft, rate=rate, hop_length=hop_length)
        y = librosa.istft(stft_stretch, hop_length=hop_length)
        return y
