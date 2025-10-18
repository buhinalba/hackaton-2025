import numpy as np
import sounddevice as sd
import pygame
import threading

# === CONFIG ===
SAMPLERATE = 44100
CHUNK = 1024  # frames per buffer
WIDTH, HEIGHT = 800, 400

# === GLOBAL STATE ===
bands = {'bass': 0, 'mid': 0, 'treble': 0}
running = True


def audio_callback(indata, frames, time, status):
    global bands
    if status:
        print(status)
    audio_data = np.mean(indata, axis=1)  # mono

    # FFT
    fft = np.fft.rfft(audio_data)
    freq = np.fft.rfftfreq(len(audio_data), 1/SAMPLERATE)
    magnitude = np.abs(fft)

    # Frequency bands
    def band_energy(low, high):
        idx = np.where((freq >= low) & (freq < high))
        return np.mean(magnitude[idx]) if len(idx[0]) > 0 else 0

    bands = {
        'bass': band_energy(20, 250),
        'mid': band_energy(250, 2000),
        'treble': band_energy(2000, 8000)
    }


def audio_thread():
    with sd.InputStream(channels=1, callback=audio_callback, samplerate=SAMPLERATE, blocksize=CHUNK):
        while running:
            sd.sleep(100)


def draw_visuals(screen):
    screen.fill((0, 0, 0))

    # Normalize band strengths
    max_val = max(bands.values()) or 1
    bass_h = int((bands['bass'] / max_val) * HEIGHT)
    mid_h = int((bands['mid'] / max_val) * HEIGHT)
    treb_h = int((bands['treble'] / max_val) * HEIGHT)

    # Colors: red=bass, green=mid, blue=treble
    pygame.draw.rect(screen, (255, 50, 50), (100, HEIGHT - bass_h, 150, bass_h))
    pygame.draw.rect(screen, (50, 255, 50), (325, HEIGHT - mid_h, 150, mid_h))
    pygame.draw.rect(screen, (50, 50, 255), (550, HEIGHT - treb_h, 150, treb_h))

    pygame.display.flip()


def main():
    global running
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("BeatLight — Minimal Music Visualizer")

    # Start audio capture in a separate thread
    thread = threading.Thread(target=audio_thread)
    thread.start()

    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        draw_visuals(screen)
        clock.tick(30)  # 30 FPS

    pygame.quit()


if __name__ == "__main__":
    main()
