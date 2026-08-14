# CHIP-8 Emulator

A CHIP-8 interpreter with a Pygame frontend, split into small components on
top of your `Chip8CPU` core. Conventions (memory layout, font placement,
keypad mapping, timer/clock decoupling) follow Tobias V. I. Langhoff's guide:
https://tobiasvl.github.io/blog/write-a-chip-8-emulator/

## Layout

```
main.py                 Entry point: parses CLI args, starts the Emulator
chip8/
  __init__.py            Package exports
  cpu.py                  Chip8CPU: memory, registers, instruction execution
  display.py              Display: owns the Pygame window, draws the framebuffer
  keypad.py                Keypad: maps keyboard events to the 16-key hex keypad
  audio.py                Beeper: generates and loops the sound-timer beep
  emulator.py              Emulator: run loop wiring CPU + Display + Keypad + Beeper
requirements.txt
```

Each component only knows about its own job:

- **`cpu.py`** has no idea Pygame exists. It's pure emulation logic (your
  original file, with the font table extended from just `0`/`1` to the full
  `0`-`F` hex digit set, plus a `load_rom()` helper). The original test suite
  still passes unchanged against it.
- **`display.py`** takes a framebuffer (the CPU's `display` grid) and draws it
  — it doesn't know about instructions or timers.
- **`keypad.py`** turns Pygame key events into a 16-element key-state list —
  it doesn't know about the CPU's opcodes.
- **`audio.py`** just knows how to loop/stop a beep — it doesn't know *why*
  it's beeping (that's the sound timer's job to decide).
- **`emulator.py`** is the only piece that wires them all together: it steps
  the CPU, decides when to beep, tells the display to redraw, and reads input.

This means you can, e.g., swap `display.py` for an SDL2 or a headless/test
renderer without touching `cpu.py`, or reuse `cpu.py` in a totally different
frontend (web, terminal, etc.).

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py path/to/rom.ch8
```

Optional flags:

```bash
python main.py rom.ch8 --cycles 11 --scale 12
```

- `--cycles`: CPU instructions executed per 60 Hz frame (default `11`, ≈660 Hz,
  a common speed for CHIP-8 games). Bump this up for games that feel sluggish,
  lower it for games that run too fast.
- `--scale`: pixel size multiplier for the 64x32 display (default `12`, giving
  a 768x384 window).

Press `Esc` or close the window to quit.

## Keypad

CHIP-8 used a 16-key hex keypad. It's mapped onto the left side of a QWERTY
keyboard:

```
CHIP-8 keypad      Your keyboard
1 2 3 C             1 2 3 4
4 5 6 D             Q W E R
7 8 9 E             A S D F
A 0 B F             Z X C V
```

## Implementation notes

- **Timers vs. clock speed**: `cpu.cycle()` (in `cpu.py`) ties one timer tick to
  one instruction, which is only correct at exactly 60 Hz. Since real CHIP-8
  games run several hundred instructions per second, `Emulator` doesn't use
  `cycle()` directly — it fetches/executes instructions itself
  (`Emulator.step_cpu`) and decrements the delay/sound timers once per 60 Hz
  frame instead (`Emulator.update_timers`), so timing stays correct regardless
  of `--cycles`.
- **Sound**: `Beeper` generates a square-wave tone with numpy and loops it via
  `pygame.mixer` for as long as `Emulator.update_timers` reports the sound
  timer is nonzero.
- **Input**: `FX0A` (wait for key) relies on `cpu.keypad` being up to date
  *before* that instruction executes. `Emulator` shares the same list object
  between `Keypad.state` and `cpu.keypad`, and polls input once per frame
  before stepping the CPU, so this holds.
- Quirks like `SHR`/`SHL` using `VY` (original COSMAC VIP behavior) vs. `VX`
  only (CHIP-48/SUPER-CHIP behavior) aren't configurable — the CPU uses the
  `VX`-only behavior as written in `cpu.py`. Most ROMs targeting modern
  interpreters expect this.
