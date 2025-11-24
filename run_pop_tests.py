# run_pop_tests.py
import json
from pathlib import Path
from midi_processing.midi_parser import MidiProcessor


def check_and_export(midi_path: Path, output_dir: Path):
    print(f"\n========== Testing {midi_path.name} ==========")

    processor = MidiProcessor()

    midi_data = processor.parse_midi(str(midi_path))
    total_notes = sum(len(v) for v in midi_data.tracks.values())
    num_tracks = len(midi_data.tracks)

    print(f"Tempo: {midi_data.tempo:.2f} BPM")
    print(f"Tracks: {num_tracks}, Total notes: {total_notes}")

    analysis = processor.analyze_music(midi_data)
    print(f"Detected key: {analysis.key}")
    print("First 8 chords:", analysis.chord_progression[:8])

    mapping = processor.map_to_timbres(midi_data, None)
    print("Track mapping:")
    for track_name, group in mapping.mapping.items():
        print(f"  {track_name} -> {group}")

    # === 输出目录 ===
    output_dir.mkdir(parents=True, exist_ok=True)

    # === JSON 文件名 ===
    out_path = output_dir / (midi_path.stem + ".json")

    # === 导出 JSON ===
    json_dict = processor.export_to_json(str(midi_path))
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(json_dict, f, ensure_ascii=False, indent=2)

    print(f"✅ JSON saved to {out_path}")


if __name__ == "__main__":
    base_dir = Path(__file__).parent / "midi_processing" / "test_midis"
    output_dir = base_dir / "output"   # ⭐ 这里明确指定输出位置

    midi_files = [
        base_dir / "Blinding_Lights.mid",
        base_dir / "Sugar.mid",
        base_dir / "Uptown_Funk.mid",
    ]

    for mf in midi_files:
        if mf.exists():
            check_and_export(mf, output_dir)
        else:
            print(f"❌ {mf} not found")
