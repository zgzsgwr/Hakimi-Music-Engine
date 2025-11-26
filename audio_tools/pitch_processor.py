# audio_tools/pitch_processor.py
import numpy as np
import librosa


class PitchProcessor:
    """
    音高相关处理：
      - extract_pitch: 提取 F0 曲线（默认用 librosa.pyin）
      - shift_pitch: 变调（目前用 phase-vocoder, 后续可换 PSOLA）
    """

    def extract_pitch(
        self,
        audio: np.ndarray,
        sr: int,
        fmin: str = "C2",
        fmax: str = "C7",
        frame_length: int = 2048,
        hop_length: int = 256,
    ):
        """
        提取音高曲线（F0）和有声/无声标记。

        返回:
          f0: shape (T,) 的频率数组（Hz），无声帧为 np.nan
          voiced_flag: shape (T,) 的 bool 数组
          voiced_probs: shape (T,) 的置信度
        """
        f0, voiced_flag, voiced_probs = librosa.pyin(
            audio,
            fmin=librosa.note_to_hz(fmin),
            fmax=librosa.note_to_hz(fmax),
            sr=sr,
            frame_length=frame_length,
            hop_length=hop_length,
        )
        return f0, voiced_flag, voiced_probs

    def shift_pitch(
        self,
        audio: np.ndarray,
        sr: int,
        semitones: float,
    ) -> np.ndarray:
        """
        变调（不变速）。
        目前用 librosa.effects.pitch_shift (phase-vocoder)，
        后续可以替换为 PSOLA 实现。
        """
        y_shifted = librosa.effects.pitch_shift(audio, sr=sr, n_steps=semitones)
        return y_shifted

    @staticmethod
    def hz_to_midi_safe(f0: np.ndarray) -> np.ndarray:
        """
        把频率曲线（Hz）转换为 MIDI 编号（带 nan 处理）。
        """
        f0 = np.asarray(f0)
        midi = np.full_like(f0, np.nan, dtype=float)
        valid = ~np.isnan(f0) & (f0 > 0)
        midi[valid] = librosa.hz_to_midi(f0[valid])
        return midi
