# audio_tools/realtime_engine.py
import numpy as np

from .pitch_processor import PitchProcessor
from .time_stretcher import TimeStretcher
from .effects import Effects


class RealtimeEngine:
    """
    实时处理引擎（逻辑版）：
      - 按 block 处理音频
      - 每个 block 可以做：变调 / 时间拉伸 / 效果
    上层只需要不断喂 audio_block，就可以实时拿到处理结果。
    """

    def __init__(
        self,
        sample_rate: int = 44100,
        buffer_size: int = 1024,
    ):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size

        self.pitch_proc = PitchProcessor()
        self.time_stretcher = TimeStretcher()
        self.effects = Effects()

        # 当前参数（可在实时系统中动态修改）
        self.pitch_shift_semitones = 0.0
        self.time_stretch_rate = 1.0
        self.reverb_mix = 0.0

    def process_block(self, block: np.ndarray) -> np.ndarray:
        """
        输入一块音频（1D numpy 数组），输出处理后的音频块。
        注意：
          - 这里为了简单，时间拉伸只在 rate==1 时跳过
          - 真正实时系统里，时间拉伸通常在离线/缓冲层处理
        """
        y = block.astype(np.float32)

        # 音高校正 / 变调
        if abs(self.pitch_shift_semitones) > 1e-3:
            y = self.pitch_proc.shift_pitch(
                y, sr=self.sample_rate, semitones=self.pitch_shift_semitones
            )

        # 时间拉伸（这里只对 block 级做简单示意）
        if abs(self.time_stretch_rate - 1.0) > 1e-3:
            y = self.time_stretcher.time_stretch(y, rate=self.time_stretch_rate)

        # 混响
        if self.reverb_mix > 1e-3:
            y = self.effects.reverb(y, sr=self.sample_rate, mix=self.reverb_mix)

        # 确保输出长度不比输入短，简化调用方处理
        if len(y) < len(block):
            pad = np.zeros(len(block) - len(y), dtype=np.float32)
            y = np.concatenate([y, pad])
        else:
            y = y[: len(block)]

        return y
