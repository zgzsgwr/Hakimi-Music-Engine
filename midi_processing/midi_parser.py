# midi_processing/midi_parser.py
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import mido


# --------- 数据结构 ---------
@dataclass
class NoteEvent:
    start_time: float
    end_time: float
    pitch: int
    velocity: int
    track: str
    channel: int


@dataclass
class MidiData:
    tempo: float
    ticks_per_beat: int
    tracks: Dict[str, List[NoteEvent]]
    metadata: Dict[str, Any]


@dataclass
class MusicAnalysis:
    key: str
    chord_progression: List[str]
    rhythm_patterns: Dict[str, Any]
    structure: Dict[str, Any]


@dataclass
class TrackMapping:
    mapping: Dict[str, str]


# --------- 主类：MidiProcessor ---------
class MidiProcessor:
    """主入口：解析 MIDI、乐理分析、音轨映射、导出 JSON"""

    def parse_midi(self, file_path: str) -> MidiData:
        midi = mido.MidiFile(file_path)
        ticks_per_beat = midi.ticks_per_beat

        current_tempo = 500000  # 120 BPM
        tempo_events = []

        # 取第一条 tempo 作为全局 tempo（简化）
        for track in midi.tracks:
            abs_time = 0
            for msg in track:
                abs_time += msg.time
                if msg.type == "set_tempo":
                    current_tempo = msg.tempo
                    tempo_events.append((abs_time, msg.tempo))
                    break
            if tempo_events:
                break

        def ticks_to_seconds(ticks: int, tempo: int) -> float:
            return mido.tick2second(ticks, ticks_per_beat, tempo)

        tracks: Dict[str, List[NoteEvent]] = {}

        for i, track in enumerate(midi.tracks):
            track_name = f"Track_{i}"
            for msg in track:
                if msg.type == "track_name":
                    track_name = msg.name or track_name
                    break

            abs_ticks = 0
            active_notes: Dict[tuple, NoteEvent] = {}
            note_list: List[NoteEvent] = []

            for msg in track:
                abs_ticks += msg.time
                time_sec = ticks_to_seconds(abs_ticks, current_tempo)

                if msg.type == "set_tempo":
                    continue

                if msg.type in ("note_on", "note_off"):
                    channel = getattr(msg, "channel", 0)
                    key = (channel, msg.note)

                    if msg.type == "note_on" and msg.velocity > 0:
                        active_notes[key] = NoteEvent(
                            start_time=time_sec,
                            end_time=time_sec,
                            pitch=msg.note,
                            velocity=msg.velocity,
                            track=track_name,
                            channel=channel,
                        )
                    else:
                        if key in active_notes:
                            note = active_notes.pop(key)
                            note.end_time = time_sec
                            if note.end_time > note.start_time + 0.005:
                                note_list.append(note)

            tracks[track_name] = note_list

        seconds_per_beat = mido.tick2second(
            ticks_per_beat, ticks_per_beat, current_tempo
        )
        bpm = 60.0 / seconds_per_beat if seconds_per_beat > 0 else 120.0

        metadata = {"raw_tempo_events": tempo_events, "file_path": file_path}

        return MidiData(
            tempo=bpm,
            ticks_per_beat=ticks_per_beat,
            tracks=tracks,
            metadata=metadata,
        )

    def analyze_music(self, midi_data: MidiData) -> MusicAnalysis:
        # 局部 import，避免循环引用
        from .music_analyzer import MusicAnalyzer

        analyzer = MusicAnalyzer()
        return analyzer.analyze(midi_data)

    def map_to_timbres(
        self, midi_data: MidiData, rules: Optional[dict] = None
    ) -> TrackMapping:
        from .track_mapper import TrackMapper, default_mapping_rules

        if rules is None:
            rules = default_mapping_rules()
        mapper = TrackMapper(rules)
        return mapper.map_tracks(midi_data)

    def export_to_json(self, file_path: str, rules: Optional[dict] = None) -> dict:
        midi_data = self.parse_midi(file_path)
        analysis = self.analyze_music(midi_data)
        mapping = self.map_to_timbres(midi_data, rules)

        # 计算总时长
        max_end = 0.0
        for notes in midi_data.tracks.values():
            if notes:
                local_max = max(n.end_time for n in notes)
                max_end = max(max_end, local_max)

        # 轨道
        tracks_json = []
        for track_name, notes in midi_data.tracks.items():
            timbre_group = mapping.mapping.get(track_name, "GENERIC")
            notes_json = [
                {
                    "start": round(n.start_time, 6),
                    "end": round(n.end_time, 6),
                    "pitch": n.pitch,
                    "velocity": n.velocity,
                }
                for n in notes
            ]
            tracks_json.append(
                {
                    "name": track_name,
                    "timbre_group": timbre_group,
                    "notes": notes_json,
                }
            )

        # 时间线（和弦窗口要和 music_analyzer 里一致）
        bin_size = 0.5
        chord_prog = analysis.chord_progression

        chords_timeline = []
        current = None
        start_bin = 0
        for i, ch in enumerate(chord_prog):
            if current is None:
                current = ch
                start_bin = i
            elif ch != current:
                chords_timeline.append(
                    {
                        "start": round(start_bin * bin_size, 6),
                        "end": round(i * bin_size, 6),
                        "name": current,
                    }
                )
                current = ch
                start_bin = i
        if current is not None:
            chords_timeline.append(
                {
                    "start": round(start_bin * bin_size, 6),
                    "end": round(len(chord_prog) * bin_size, 6),
                    "name": current,
                }
            )

        sections_json = []
        for idx, sec in enumerate(analysis.structure.get("sections", [])):
            sections_json.append(
                {
                    "label": f"sec_{idx}",
                    "chord": sec.get("chord", "N"),
                    "start_bin": sec.get("start_bin", 0),
                    "end_bin": sec.get("end_bin", 0),
                    "start": round(sec.get("start_bin", 0) * bin_size, 6),
                    "end": round((sec.get("end_bin", 0) + 1) * bin_size, 6),
                }
            )

        return {
            "meta": {
                "file_path": file_path,
                "tempo_bpm": midi_data.tempo,
                "ticks_per_beat": midi_data.ticks_per_beat,
                "duration_seconds": round(max_end, 6),
            },
            "global": {
                "key": analysis.key,
                "num_tracks": len(midi_data.tracks),
            },
            "tracks": tracks_json,
            "timeline": {
                "bin_size": bin_size,
                "chords": chords_timeline,
                "sections": sections_json,
                "beat_density": analysis.rhythm_patterns.get(
                    "beat_density", []
                ),
            },
        }
