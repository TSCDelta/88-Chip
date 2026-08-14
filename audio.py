"""Audio component: generates a beep and plays it while the sound timer is active."""

import numpy as np
import pygame


def _make_beep(frequency=440, duration=0.1, sample_rate=44100, volume=0.3):
    """Generate a simple square-wave beep as a pygame Sound."""
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, endpoint=False)
    wave = np.sign(np.sin(2 * np.pi * frequency * t))
    audio = (wave * volume * 32767).astype(np.int16)
    stereo = np.column_stack([audio, audio])
    return pygame.sndarray.make_sound(np.ascontiguousarray(stereo))


class Beeper:
    """Plays a looping beep while active, and silences it when told to stop."""

    def __init__(self, frequency=440):
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()
        self._sound = _make_beep(frequency=frequency)
        self._channel = None

    def set_active(self, active):
        """Start looping the beep if active and not already playing; stop it otherwise."""
        if active:
            if self._channel is None or not self._channel.get_busy():
                self._channel = self._sound.play(loops=-1)
        else:
            if self._channel is not None:
                self._channel.stop()
                self._channel = None
