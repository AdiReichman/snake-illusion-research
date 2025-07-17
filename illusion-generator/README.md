# Snake Illusion Generator

A Python application for creating optical illusions based on Akiyoshi Kitaoka's "Snake Illusion" with precise parameter control for research and experimentation.

<div align="center">
  <img src="../assets/snake-illusion-generator/Example of a generated Snake Illusion.png" width="650" alt="Example of a generated Snake Illusion">
  <br>
  <i>Example of a generated Snake Illusion</i>
</div>

## Features

- **Real-time Preview**: Live preview of pattern changes
- **Pattern Types**: Complete Reversal (default) or Classic mirroring
- **Color Control**: 3 or 4 colors with individual saturation adjustment (0-100%)
- **Precision Settings**: Width control (1.0-10.0), shift angles, pattern repetitions
- **Export Options**: High-quality PNG with parameter-embedded filenames
- **Project Management**: Save/load configurations as JSON files

<div align="center">
  <img src="../assets/snake-illusion-generator/Main application interface.png" width="650" alt="Main application interface">
  <br>
  <i>Main application interface</i>
</div>

## Installation

### Requirements
- Python 3.7+
- PyQt5, Matplotlib, NumPy

### Setup
```bash
conda create -n snake_illusion python=3.10
conda activate snake_illusion
conda install pyqt matplotlib numpy
```

**Alternative with pip:**
```bash
pip install -r requirements.txt
```

### Run
```bash
python "Snake Illusion Generator.py"
```

## Quick Start

1. **Choose Pattern Type**: Complete Reversal (works with 3-4 colors) or Classic (4 colors only)
2. **Select Colors**: Click "Choose" buttons or use preset palettes
3. **Adjust Parameters**: Use sliders for saturation, width, and other settings
4. **Preview**: Watch live preview update automatically
5. **Generate**: Click "Generate Illusion" for full dual-circle pattern
6. **Save**: Export as PNG or save project as JSON for sharing

<div align="center">
  <img src="../assets/snake-illusion-generator/Pattern types.png" width="500" alt="Complete Reversal vs Classic pattern types">
  <br>
  <i>Complete Reversal vs Classic pattern types</i>
</div>

## Project Sharing

Save your configurations as JSON files to:

- **Share setups** with colleagues and collaborators
- **Reproduce experiments** with identical parameters
- **Build libraries** of interesting pattern combinations

Use "Save Project" to export all settings, then "Load Project" to restore them exactly.

## Key Controls

- **Colors**: Individual picker + saturation control for each stripe
- **Pattern Count**: 1-50 repetitions around each circle
- **Shift Angle**: -30° to +30° rotation between layers
- **Background**: Custom color or transparent
- **Width**: Relative stripe thickness

<div align="center">
  <img src="../assets/snake-illusion-generator/Live preview example.png" width="300" alt="Live preview example">
  <br>
  <i>Live preview example</i>
</div>

## File Naming

Exported files include all parameters:
```
snake_illusion_p24_c000000-B0B0B0-FFFFFF_s0-50-100_w1.0-2.0-1.5_a-12.5_bg-808080_reversed.png
```
