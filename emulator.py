"""Emulator: ties the CPU, Display, Keypad and Beeper together into a run loop."""

import pygame

from .cpu import Chip8CPU
from .display import Display
from .keypad import Keypad
from .audio import Beeper


class Emulator:
    """Drives the fetch/execute cycle and keeps CPU speed decoupled from timers.

    cpu.cycle() (in cpu.py) decrements the delay/sound timers on every call,
    which is only correct if it's called at exactly 60 Hz. Real CHIP-8 games
    expect several hundred instructions per second, so this class fetches and
    executes instructions itself (step_cpu) and decrements the timers once per
    60 Hz frame instead (update_timers), regardless of how many instructions
    ran that frame.
    """

    def __init__(self, rom_path, cycles_per_frame=11, scale=12, fps=60):
        pygame.init()

        self.cpu = Chip8CPU()
        self.cpu.load_rom(rom_path)

        self.display = Display(scale=scale, caption=f"CHIP-8 - {rom_path}")
        self.keypad = Keypad()
        self.beeper = Beeper()

        self.cpu.keypad = self.keypad.state  # CPU reads/writes this list directly

        self.cycles_per_frame = cycles_per_frame
        self.fps = fps
        self.clock = pygame.time.Clock()
        self.running = True

    def handle_input(self):
        for event in pygame.event.get():
            if self.keypad.handle_event(event) == "quit":
                self.running = False

    def step_cpu(self):
        """Fetch + execute one instruction without touching the timers."""
        cpu = self.cpu
        inst = (cpu.memory[cpu.pc] << 8) | cpu.memory[cpu.pc + 1]
        cpu.pc += 2
        cpu.execute(inst)

    def update_timers(self):
        cpu = self.cpu
        if cpu.delay_timer > 0:
            cpu.delay_timer -= 1
        if cpu.sound_timer > 0:
            cpu.sound_timer -= 1
        self.beeper.set_active(cpu.sound_timer > 0)

    def run(self):
        while self.running:
            self.handle_input()

            for _ in range(self.cycles_per_frame):
                self.step_cpu()

            self.update_timers()
            self.display.draw(self.cpu.display)
            self.clock.tick(self.fps)

        pygame.quit()
