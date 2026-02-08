---
name: project-synth-context
description: Architecture, purpose, and context for the Synth (DAW Lite) project. Use this to understand the codebase structure and design decisions.
---
# Synth Project Context

## Purpose
A Python-based Digital Audio Workstation (DAW) Lite with a Cyberpunk/Sci-Fi aesthetic.
The application provides real-time audio synthesis, looping capabilities, and visual feedback.

## Technology Stack
- **GUI Framework:** PySide6 (Qt)
- **Audio Engine:** `sounddevice` (PortAudio wrapper), `numpy` (DSP), `scipy`
- **Visualization:** `pyqtgraph` (integrated into PySide6 layouts)
- **Styling:** QSS (Qt Style Sheets)

## Architecture Overview

### 1. Audio Engine (`src/audio/`)
The heart of the application, running in a dedicated audio thread via `sounddevice`.
- **`engine.py`**: The central coordinator (Singleton logic).
    - Manages the audio stream `_callback`.
    - **Signal Flow**: Voices -> VoiceManager -> Looper -> Output.
    - Provides thread-safe buffer access for visualization.
- **`voice_manager.py`**: Manages polyphonic synthesis.
    - Allocates `Voice` instances (`voice.py`) to MIDI notes/frequencies.
    - Routes parameters (Attack, Decay, etc.) to active voices.
- **`looper.py`**: Handles multi-track audio recording and playback.
    - Synchronized with the audio callback.
    - Manages track states (Arm, Mute, Solo).

### 2. User Interface (`src/ui/`)
Built with PySide6, orchestrating user interaction and visual feedback.
- **`main_window.py`**: The main application window.
    - Composes `SynthPanel`, `LooperPanel`, `Visualizer`, and `VirtualKeyboard`.
    - Handles global key events and routes them to the keyboard.
- **`keyboard.py`**: `VirtualKeyboard` widget.
    - Visualizes key states using manual "piano" layout (overlapping keys).
    - Supports **Multi-Touch** for polyphonic chords on touch screens.
    - Emits signals (`note_on`, `note_off`) connected to the `AudioEngine`.
- **`visualizer.py`**: High-performance plotting.
    - Pulls data from `AudioEngine.get_buffer()` on a UI timer/interval.
    - Displays Oscilloscope, Spectrum Analyzer (FFT), and ADSR Envelope Graph side-by-side.
- **`synth_panel.py`** & **`looper_panel.py`**: Control surfaces for their respective audio components.

### 3. Styling
- **Theme:** Cyberpunk / Sci-Fi / Dark Mode.
- **Definition:** `src/assets/styles/theme.qss`.
- **Key Characteristics:**
    - Dark backgrounds (approx `#1e1e1e`, `#2b2b2b`).
    - Neon accents (Cyan, Magenta) for active states and highlights.
    - Rounded corners and modern flatness.

## Key Interaction Flows

### Note Triggering
1. **Input:** User presses a key (Physical or Mouse click on Virtual Keyboard).
2. **UI Layer:** `VirtualKeyboard` emits `note_on_signal(freq)`.
3. **Connection:** `MainApplication` routes signal to `AudioEngine.note_on(freq)`.
4. **Audio Layer:** `AudioEngine` delegates to `VoiceManager.note_on(freq)`.
5. **DSP:** A free `Voice` starts generating samples in the next audio callback block.

### Visualization
1. **Audio Thread:** `AudioEngine` updates `self.current_buffer` with the mixed output.
2. **UI Thread:** `Visualizer` wrapper calls `update_plot()` via `QTimer`.
3. **Fetch:** Calls `AudioEngine.get_buffer()` (uses `threading.Lock`).
4. **Render:** `pyqtgraph` updates the curve.

## Directory Structure
```
c:/projects/Synth/
├── src/
│   ├── audio/          # DSP and Audio Logic
│   ├── ui/             # PySide6 Widgets and Windows
│   ├── utils/          # Helpers (Logger, Playback utils)
│   ├── assets/         # Styles (QSS), Images
│   └── main.py         # Entry Point
├── tests/              # Unit and Integration Tests
└── requirements.txt    # Project Dependencies
```
