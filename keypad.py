"""Keypad component: maps host keyboard events onto CHIP-8's 16-key hex keypad."""

import pygame

# Standard CHIP-8 keypad -> modern keyboard layout
#   COSMAC VIP keypad         Mapped to
#   1 2 3 C                   1 2 3 4
#   4 5 6 D                   Q W E R
#   7 8 9 E                   A S D F
#   A 0 B F                   Z X C V
KEY_MAP = {
    pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
    pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
    pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
    pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF,
}


class Keypad:
    """Tracks the 16-key CHIP-8 keypad state and processes Pygame key events."""

    def __init__(self):
        self.state = [0] * 16

    def handle_event(self, event):
        """Update key state from a single Pygame event.

        Returns "quit" if the event means the app should exit (Esc or window
        close), otherwise None.
        """
        if event.type == pygame.QUIT:
            return "quit"
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "quit"
            if event.key in KEY_MAP:
                self.state[KEY_MAP[event.key]] = 1
        elif event.type == pygame.KEYUP:
            if event.key in KEY_MAP:
                self.state[KEY_MAP[event.key]] = 0
        return None
