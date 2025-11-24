# midi_processing/track_mapper.py
from typing import Dict
from .midi_parser import MidiData, TrackMapping


def default_mapping_rules() -> dict:
    """
    默认音轨映射策略：
      - 根据 track 名称中的关键词判断音色组
      - 匹配不到时使用 "GENERIC"
    """
    return {
        "keywords": {
            # 打击乐
            "drum": "DRUMS",
            "percussion": "DRUMS",
            "kick": "DRUMS",
            "snare": "DRUMS",
            "hihat": "DRUMS",
            "cymbal": "DRUMS",

            # 贝斯
            "bass": "BASS",

            # 钢琴 / 键盘
            "piano": "PIANO",
            "keys": "PIANO",
            "epiano": "PIANO",

            # 吉他
            "guitar": "GUITAR",
            "acoustic": "GUITAR",
            "electric": "GUITAR",

            # 弦乐
            "violin": "STRINGS",
            "viola": "STRINGS",
            "cello": "STRINGS",
            "string": "STRINGS",

            # 合成器
            "synth": "SYNTH",
            "lead": "SYNTH",
            "pad": "SYNTH",
            "pluck": "SYNTH",

            # 人声引导 / 主旋律
            "vocal": "VOCAL",
            "voice": "VOCAL",
            "melody": "MELODY"
        },
        "default": "GENERIC"
    }


class TrackMapper:
    """
    根据 track 名称自动映射到音色类别。
    支持用户自定义 rules（例如从 JSON/配置文件读取）。
    """

    def __init__(self, rules: dict):
        self.rules = rules
        self.keyword_map: Dict[str, str] = {
            k.lower(): v for k, v in rules.get("keywords", {}).items()
        }
        self.default = rules.get("default", "GENERIC")

    def map_tracks(self, midi_data: MidiData) -> TrackMapping:
        mapping: Dict[str, str] = {}
        for track_name in midi_data.tracks.keys():
            lname = track_name.lower()
            mapped = self.default
            # 简单关键词匹配
            for kw, group in self.keyword_map.items():
                if kw in lname:
                    mapped = group
                    break
            mapping[track_name] = mapped
        return TrackMapping(mapping=mapping)
