# midi_processing/music_analyzer.py
from collections import Counter, defaultdict
from typing import Dict, List
import math

from .midi_parser import MidiData, MusicAnalysis, NoteEvent


class MusicAnalyzer:
    """
    轻量乐理分析：
      - 调性检测（基于 pitch class 直方图 + 模板匹配）
      - 和弦分析（时间窗内聚合音高集合）
      - 节奏模式统计（IOI、节拍上事件数量）
    """

    MAJOR_TEMPLATE = [6.35, 2.23, 3.48, 2.33,
                      4.38, 4.09, 2.52, 5.19,
                      2.39, 3.66, 2.29, 2.88]
    MINOR_TEMPLATE = [6.33, 2.68, 3.52, 5.38,
                      2.60, 3.53, 2.54, 4.75,
                      3.98, 2.69, 3.34, 3.17]

    PITCH_CLASS_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
                         'F#', 'G', 'G#', 'A', 'A#', 'B']

    def analyze(self, midi_data: MidiData) -> MusicAnalysis:
        all_notes = self._gather_all_notes(midi_data)

        key_name = self._detect_key(all_notes)
        chord_prog = self._analyze_chords(all_notes, window=0.5)  # 0.5 秒一格
        rhythm_patterns = self._analyze_rhythm(all_notes, tempo=midi_data.tempo)
        structure = self._build_timeline(chord_prog, rhythm_patterns)

        return MusicAnalysis(
            key=key_name,
            chord_progression=chord_prog,
            rhythm_patterns=rhythm_patterns,
            structure=structure
        )

    # ---------- 工具函数 ----------

    def _gather_all_notes(self, midi_data: MidiData) -> List[NoteEvent]:
        notes: List[NoteEvent] = []
        for track_notes in midi_data.tracks.values():
            notes.extend(track_notes)
        notes.sort(key=lambda n: n.start_time)
        return notes

    # ---------- 调性检测 ----------

    def _detect_key(self, notes: List[NoteEvent]) -> str:
        if not notes:
            return "C major"

        pc_hist = [0.0] * 12
        for n in notes:
            pc = n.pitch % 12
            duration = max(n.end_time - n.start_time, 0.01)
            pc_hist[pc] += duration

        total = sum(pc_hist)
        if total > 0:
            pc_hist = [x / total for x in pc_hist]

        def correlate(template):
            t_sum = sum(template)
            t = [x / t_sum for x in template]
            return sum(x * y for x, y in zip(pc_hist, t))

        best_score = -1.0
        best_key = ("C", "major")

        for i in range(12):
            rotated = self.MAJOR_TEMPLATE[-i:] + self.MAJOR_TEMPLATE[:-i]
            score = correlate(rotated)
            if score > best_score:
                best_score = score
                best_key = (self.PITCH_CLASS_NAMES[i], "major")

        for i in range(12):
            rotated = self.MINOR_TEMPLATE[-i:] + self.MINOR_TEMPLATE[:-i]
            score = correlate(rotated)
            if score > best_score:
                best_score = score
                best_key = (self.PITCH_CLASS_NAMES[i], "minor")

        tonic, mode = best_key
        return f"{tonic} {mode}"

    # ---------- 和弦分析 ----------

    def _analyze_chords(self, notes: List[NoteEvent], window: float = 0.5) -> List[str]:
        if not notes:
            return []

        end_time = max(n.end_time for n in notes)
        num_bins = int(math.ceil(end_time / window))

        bins: List[List[int]] = [[] for _ in range(num_bins)]
        for n in notes:
            start_bin = int(n.start_time // window)
            end_bin = int(n.end_time // window)
            for b in range(start_bin, min(end_bin + 1, num_bins)):
                bins[b].append(n.pitch % 12)

        chord_names: List[str] = []
        prev_chord = None

        for pc_list in bins:
            if not pc_list:
                chord_names.append("N")
                prev_chord = "N"
                continue

            c = Counter(pc_list)
            top_pcs = [pc for pc, _ in c.most_common(3)]
            name = self._name_chord_from_pcs(sorted(top_pcs))
            if name == prev_chord and chord_names:
                continue
            chord_names.append(name)
            prev_chord = name

        return chord_names

    def _name_chord_from_pcs(self, pcs: List[int]) -> str:
        if len(pcs) < 2:
            return "N"

        for root in pcs:
            intervals = sorted(((pc - root) % 12) for pc in pcs)
            if set(intervals) >= {0, 4, 7}:
                return f"{self.PITCH_CLASS_NAMES[root]}"
            if set(intervals) >= {0, 3, 7}:
                return f"{self.PITCH_CLASS_NAMES[root]}m"

        return "N"

    # ---------- 节奏分析 ----------

    def _analyze_rhythm(self, notes: List[NoteEvent], tempo: float) -> Dict[str, any]:
        if not notes:
            return {"ioi_hist": [], "beat_density": []}

        onsets = sorted(n.start_time for n in notes)

        iois = [onsets[i+1] - onsets[i] for i in range(len(onsets)-1)
                if onsets[i+1] > onsets[i] + 1e-3]

        bin_size = 0.05
        hist = defaultdict(int)
        for dt in iois:
            b = round(dt / bin_size) * bin_size
            hist[b] += 1

        ioi_hist = sorted(hist.items(), key=lambda x: x[0])

        seconds_per_beat = 60.0 / tempo if tempo > 0 else 0.5
        max_time = max(onsets)
        num_beats = int(math.ceil(max_time / seconds_per_beat))
        beat_counts = [0] * num_beats
        for t in onsets:
            idx = int(t // seconds_per_beat)
            if 0 <= idx < num_beats:
                beat_counts[idx] += 1

        return {
            "ioi_hist": ioi_hist,
            "beat_density": beat_counts,
            "seconds_per_beat": seconds_per_beat
        }

    # ---------- 结构 / 时间线 ----------

    def _build_timeline(self, chord_prog: List[str], rhythm: Dict[str, any]) -> Dict[str, any]:
        structure = {
            "sections": [],
            "chord_sequence": chord_prog,
            "rhythm_summary": {
                "avg_beat_density": float(sum(rhythm.get("beat_density", [])) /
                                         max(len(rhythm.get("beat_density", [])), 1))
            }
        }
        current = None
        start_idx = 0
        for i, ch in enumerate(chord_prog):
            if current is None:
                current = ch
                start_idx = i
            elif ch != current:
                structure["sections"].append({
                    "chord": current,
                    "start_bin": start_idx,
                    "end_bin": i - 1
                })
                current = ch
                start_idx = i
        if current is not None:
            structure["sections"].append({
                "chord": current,
                "start_bin": start_idx,
                "end_bin": len(chord_prog) - 1
            })
        return structure
