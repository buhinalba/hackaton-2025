from itertools import product, count
from math import sin, cos, pi
import threading
import pygame

import numpy as np
import sounddevice as sd
import pygame
import threading
import colorsys
import time

# === CONFIG ===
SAMPLERATE = 44100
CHUNK = 1024
WIDTH, HEIGHT = 1000, 600

bands = {'bass': 0, 'mid': 0, 'treble': 0}
running = True

def audio_callback(indata, frames, time_, status):
    global bands
    if status:
        print(status)
    audio_data = np.mean(indata, axis=1)

    # FFT
    fft = np.fft.rfft(audio_data)
    freq = np.fft.rfftfreq(len(audio_data), 1/SAMPLERATE)
    magnitude = np.abs(fft)

    # Band energies
    def energy(low, high):
        idx = np.where((freq >= low) & (freq < high))
        return np.mean(magnitude[idx]) if len(idx[0]) > 0 else 0

    bands = {
        'bass': energy(20, 250),
        'mid': energy(250, 2000),
        'treble': energy(2000, 8000)
    }

def audio_thread():
    with sd.InputStream(channels=1, callback=audio_callback,
                        samplerate=SAMPLERATE, blocksize=CHUNK):
        while running:
            sd.sleep(100)

# === CONFIG ===
SAMPLERATE = 44100
CHUNK = 1024
WIDTH, HEIGHT = 1000, 600
VARIABLE = 42
running = True

SIDE = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((SIDE, SIDE))
screen.fill(WHITE)


def draw_pixel(screen, x, y, colour):
    x, y = round(x), round(y)
    for dx, dy in product(range(-1, 2), repeat=2):
        screen.set_at((x + dx, y + dy), colour)

def spiral(percentage):
    return (
        SIDE // 2 * percentage * cos(10 * pi * percentage),
        SIDE // 2 * percentage * sin(10 * pi * percentage),
    )

def rotating_spiral(percentage, time, variant):
    max_val = max(bands.values()) or 1
    # Normalize and smooth motion
    variant = (min(bands['mid'] / max_val, 1)+1 ) * 50 # smooth range

    return (
        SIDE // 2
        + (1 + sin(time) / variant)
        * percentage * (SIDE // 3) * cos(variant * pi * percentage + time),
        SIDE // 2
        + (1 + sin(time) / VARIABLE)
        * percentage * (SIDE // 3) * sin(variant * pi * percentage + time),
    )


def background(time):
    variant = 40 # smooth range
    print(variant)
    some_meaningful_number=30*variant
    rgb_code = (
        (int(abs(30 * sin(0.05 * time))))%255,
        (int(abs(30 * sin(0.05 * time))))%255,
        (int(abs(30 * sin(0.05 * time))))%255
    )
    return rgb_code

def fg(time):
    variant = 40 + min(bands['mid'] * 30, 100)  # smooth range
    return (
        255 - int(abs(15 * variant * sin(0.1 * time)))%255,
        85 + int(abs(160 * variant * sin(0.1 * time)))%170,
        85 + int(abs(60 * variant * sin(0.1 * time)))%170,
    )

def animate():
    global running
    pygame.init()

    thread = threading.Thread(target=audio_thread)
    thread.start()

    clock = pygame.time.Clock()
    hue_shift = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        STEPS = 3000
        step_count = 0.001
        tick = 1
        while tick < STEPS:
            screen.fill(background(tick))
            clr = fg(tick)
            for step in range(STEPS + 1):
                percentage = step / STEPS
                x, y = rotating_spiral(percentage, tick, VARIABLE*step+1)
                draw_pixel(screen, x, y, clr)
            pygame.display.flip()
            tick += step_count



if __name__ == "__main__":
    animate()