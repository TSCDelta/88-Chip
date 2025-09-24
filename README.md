# CHIP-8 Emulator

A fully functional CHIP-8 emulator built with Python and Pygame. This emulator can run classic CHIP-8 games and programs with accurate timing and display rendering.

## Features

- ✅ Complete CHIP-8 instruction set implementation
- 🎮 Full keyboard input support
- 🖥️ Accurate 64x32 pixel display with scaling
- 🔊 Sound support with beep functionality
- ⚡ Configurable CPU speed/timing
- 📁 ROM loading from file
- 🧪 Robust CPU implementation with validation

## Requirements

```bash
pip install pygame
```

## Quick Start

1. **Run the emulator:**
   ```bash
   python main.py [rom_file.ch8]
   ```

2. **Without a ROM file:**
   ```bash
   python main.py
   ```
   The emulator will start with a blank screen. Use the file menu or drag-and-drop to load a ROM.

## Controls

The CHIP-8 uses a 16-key hexadecimal keypad (0-F). The keyboard mapping is:

```
CHIP-8 Keypad    Keyboard
1 2 3 C          1 2 3 4
4 5 6 D    =>    Q W E R
7 8 9 E          A S D F
A 0 B F          Z X C V
```

### Additional Controls
- `ESC` - Exit emulator
- `R` - Reset/Restart current ROM
- `P` - Pause/Resume
- `+/-` - Increase/Decrease CPU speed
- `F11` - Toggle fullscreen

## File Structure

```
chip8-emulator/
├── main.py              # Main emulator application
├── chip8_cpu.py         # CHIP-8 CPU implementation
├── cpu.py               # Standalone CPU with tests
├── roms/                # Directory for ROM files
├── fonts/               # CHIP-8 font data
└── README.md            # This file
```

## Usage Examples

### Basic Usage
```bash
# Run Pong
python main.py roms/pong.ch8

# Run Tetris
python main.py roms/tetris.ch8

# Run Space Invaders
python main.py roms/invaders.ch8
```

### Advanced Options
```bash
# Run with custom CPU speed (default: 700 Hz)
python main.py --speed 500 roms/game.ch8

# Run with different window scale (default: 10x)
python main.py --scale 15 roms/game.ch8

# Enable debug mode
python main.py --debug roms/game.ch8
```

## Configuration

You can modify the following settings in `main.py`:

- `WINDOW_SCALE`: Display scaling factor (default: 10)
- `CPU_SPEED`: Instructions per second (default: 700)
- `TIMER_SPEED`: Timer frequency in Hz (default: 60)
- `BACKGROUND_COLOR`: Background color (default: black)
- `FOREGROUND_COLOR`: Pixel color (default: white)

## ROMs

CHIP-8 ROMs typically have `.ch8` or `.c8` extensions. You can find public domain ROMs at:
- [Zophar's Domain](https://www.zophar.net/pdroms/chip8.html)
- [CHIP-8 Archive](http://www.chip8.com/)
- [Revival Studios](https://www.revival-studios.com/other.php)

Popular games include:
- Pong
- Tetris
- Space Invaders
- Pac-Man
- Breakout
- Missile Command

## Development

### CPU Implementation
The CHIP-8 CPU (`chip8_cpu.py`) implements:
- 35 instructions covering the complete CHIP-8 instruction set
- 4KB memory (0x000-0xFFF)
- 16 8-bit registers (V0-VF)
- 16-bit index register (I)
- Program counter and stack pointer
- Two timers (delay and sound)
- 64x32 monochrome display
- 16-key hexadecimal keypad

### Adding New Features
1. **Custom Instructions**: Add to the `execute()` method in `chip8_cpu.py`
2. **Enhanced Graphics**: Modify the display rendering in `main.py`
3. **Audio Effects**: Extend the sound system with different beep types
4. **Save States**: Implement CPU state serialization

## Troubleshooting

### Common Issues

**ROM won't load:**
- Ensure the ROM file exists and is readable
- Check that the file is a valid CHIP-8 ROM (usually 4KB or less)
- Try a different ROM to verify the emulator works

**Game runs too fast/slow:**
- Adjust CPU speed with `+/-` keys
- Some games are designed for specific speeds
- Try speeds between 200-1000 Hz

**No sound:**
- Check your system audio settings
- Ensure pygame audio is properly initialized
- Try running with `--debug` to see audio status

**Controls don't work:**
- Verify you're using the correct key mapping
- Make sure the emulator window has focus
- Some games use different keys - check the game's documentation

### Debug Mode
Run with `--debug` to see:
- CPU state information
- Instruction execution trace
- Memory dumps
- Timer values
- Input status

## Technical Details

### CHIP-8 Specifications
- **CPU**: Custom 8-bit processor
- **Memory**: 4KB RAM (0x000-0xFFF)
- **Display**: 64x32 pixels, monochrome
- **Timers**: 60Hz delay and sound timers
- **Input**: 16-key hexadecimal keypad
- **Fonts**: Built-in 4x5 pixel font set (0-F)

### Memory Map
```
0x000-0x1FF: Reserved (interpreter)
0x050-0x0A0: Font set storage
0x200-0xFFF: Program ROM and work RAM
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Acknowledgments

- Joseph Weisbecker - Creator of the CHIP-8 system
- The CHIP-8 community for preserving games and documentation
- Pygame developers for the excellent graphics library

---

*Happy emulating! 🎮*
