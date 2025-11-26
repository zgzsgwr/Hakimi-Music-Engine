🎵 Hakimi Music Engine

Hakimi Music Engine
A complete backend engine for MIDI analysis and audio DSP processing, designed for interactive music applications and visualization systems.

This project includes:

A5 — MIDI Processing & Music Theory Analysis

A6 — Audio Signal Processing & Realtime Effects Engine

Both modules are implemented in Python.

==================================================

🚀 Features Overview

==================================================

==================================================

🎼 A5 — MIDI Processing Engine

==================================================

Robust MIDI analysis with full JSON export.

Main features:

Multi-format MIDI parsing

Note event extraction (pitch, velocity, start time, end time)

Track-to-timbre intelligent mapping (DRUMS, BASS, SYNTH, VOCAL…)

Key detection (major/minor)

Chord progression analysis

Rhythm pattern extraction (IOI histogram, beat density)

Timeline segmentation

JSON output for frontend visualization

JSON example (simplified):
{
"meta": { "tempo_bpm": 171, "ticks_per_beat": 480 },
"global": { "key": "C minor", "num_tracks": 9 },
"tracks": [...],
"timeline": {...}
}

==================================================

🎧 A6 — Audio DSP Engine

==================================================

Lightweight audio processing toolkit.

Pitch Processing:

F0 extraction (PYIN)

Voiced/unvoiced detection

Pitch shifting (phase vocoder)

Frequency → MIDI conversion

Time Processing:

Time stretching (phase vocoder)

Speed change without pitch change

Audio Effects:

Compressor

Reverb (convolution)

High-shelf EQ

Granular Synth:

Grain slicing

Hanning smoothing

Glitch / ambient effects

Realtime Engine:

Block-based DSP pipeline

Realtime pitch shift

Realtime reverb

Extendable to live microphone input

==================================================

📁 Project Structure

==================================================

Hakimi-Music-Engine
│
├── midi_processing
│ ├── midi_parser.py
│ ├── track_mapper.py
│ ├── music_analyzer.py
│ └── test_midis
│ ├── .mid
│ └── output/.json
│
├── audio_tools
│ ├── pitch_processor.py
│ ├── time_stretcher.py
│ ├── synthesizer.py
│ ├── effects.py
│ └── realtime_engine.py
│
├── run_pop_tests.py
└── run_audio_tests.py

==================================================

🔧 Installation

==================================================

Clone repository:
git clone https://github.com/YOUR_USERNAME/Hakimi-Music-Engine.git

Install dependencies:
pip install -r requirements.txt

Requirements include:
librosa
numpy
scipy
soundfile
mido

==================================================

🎹 Usage — MIDI Analysis

==================================================

Python usage:
from midi_processing.midi_parser import MidiProcessor
processor = MidiProcessor()
midi_data = processor.parse_midi("example.mid")
analysis = processor.analyze_music(midi_data)
processor.export_json(midi_data, analysis, "output.json")

Run tests:
python run_pop_tests.py

==================================================

🎧 Usage — Audio Processing

==================================================

from audio_tools import PitchProcessor, TimeStretcher
import soundfile as sf
audio, sr = sf.read("audio.wav")
shifted = PitchProcessor().shift_pitch(audio, sr, 3)
sf.write("shifted.wav", shifted, sr)
stretched = TimeStretcher().time_stretch(audio, 0.8)
sf.write("slow.wav", stretched, sr)

Run full DSP tests:
python run_audio_tests.py

Outputs include:

test_audio_shifted.wav

test_audio_stretched.wav

test_audio_granular.wav

test_audio_fx.wav

test_audio_realtime.wav

==================================================

🛠 Future Development

==================================================

A5 (MIDI):

Seven chords / add / sus / slash

Better timbre mapping

Auto Verse / Chorus detection

A6 (Audio):

PSOLA high-quality pitch shifting

AutoTune using MIDI

Realtime mic input

Neural audio effects

Web visualizer integration

==================================================

📄 License

==================================================
MIT License.

==================================================

✨ Author

==================================================
zgzsgwr
Hakimi Music Project 2025
