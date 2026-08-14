"""Display component: owns the Pygame window and renders the CHIP-8 framebuffer."""

import pygame

DISPLAY_WIDTH = 64
DISPLAY_HEIGHT = 32

COLOR_ON = (0, 255, 65)
COLOR_BG = (0, 0, 0)


class Display:
    """Wraps a Pygame window and knows how to draw a CHIP-8 64x32 framebuffer."""

    def __init__(self, scale=12, caption="CHIP-8"):
        self.scale = scale
        self.surface = pygame.display.set_mode(
            (DISPLAY_WIDTH * scale, DISPLAY_HEIGHT * scale)
        )
        pygame.display.set_caption(caption)

    def draw(self, framebuffer):
        """Render a 32x64 (row-major) 0/1 framebuffer to the window."""
        self.surface.fill(COLOR_BG)
        scale = self.scale
        for row in range(DISPLAY_HEIGHT):
            fb_row = framebuffer[row]
            for col in range(DISPLAY_WIDTH):
                if fb_row[col]:
                    rect = (col * scale, row * scale, scale, scale)
                    pygame.draw.rect(self.surface, COLOR_ON, rect)
        pygame.display.flip()
