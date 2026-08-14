"""
CHIP-8 Emulator - entry point.

Usage:
    python main.py path/to/rom.ch8 [--cycles 11] [--scale 12]
"""

import argparse
import sys

from chip8 import Emulator


def main():
    parser = argparse.ArgumentParser(description="CHIP-8 emulator")
    parser.add_argument("rom", help="Path to a CHIP-8 ROM file")
    parser.add_argument(
        "--cycles", type=int, default=11,
        help="CPU instructions executed per 60Hz frame (default 11, ~660Hz)"
    )
    parser.add_argument(
        "--scale", type=int, default=12,
        help="Pixel scale factor for the 64x32 display (default 12)"
    )
    args = parser.parse_args()

    emulator = Emulator(args.rom, cycles_per_frame=args.cycles, scale=args.scale)
    emulator.run()


if __name__ == "__main__":
    sys.exit(main())
