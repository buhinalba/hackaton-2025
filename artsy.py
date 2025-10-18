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

def draw_flow(screen, hue_shift):
    screen.fill((0, 0, 0, 0))
    center = (WIDTH // 2, HEIGHT // 2)
    max_val = max(bands.values()) or 1

    # Normalize and smooth motion
    bass = min(bands['bass'] / max_val, 1)
    mid = min(bands['mid'] / max_val, 1)
    treb = min(bands['treble'] / max_val, 1)

    # Dynamic color palette based on time
    hue_base = (time.time() * 30 + hue_shift) % 360

    # Convert HSL -> RGB (for artistic gradients)
    def hsl_color(offset, brightness=1):
        rgb = colorsys.hsv_to_rgb(((hue_base + offset) % 360) / 360, 1, brightness)
        return tuple(int(c * 255) for c in rgb)

    # Background fade (motion trail effect)
    fade_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    fade_surface.fill((0, 0, 0, 35))  # semi-transparent black
    screen.blit(fade_surface, (0, 0))

    # Draw flowing circles
    radius_bass = int(100 + bass * 300)
    radius_mid = int(80 + mid * 250)
    radius_treb = int(60 + treb * 200)

    pygame.draw.circle(screen, hsl_color(0, bass), center, radius_bass, width=6)
    pygame.draw.circle(screen, hsl_color(120, mid), center, radius_mid, width=5)
    pygame.draw.circle(screen, hsl_color(240, treb), center, radius_treb, width=4)

    # Scatter glowing dots based on frequency energy
    for i in range(30):
        angle = np.random.uniform(0, 2 * np.pi)
        dist = np.random.uniform(50, 300)
        x = int(center[0] + dist * np.cos(angle))
        y = int(center[1] + dist * np.sin(angle))
        brightness = np.random.uniform(0.4, 1.0)
        color = hsl_color(np.random.uniform(0, 360), brightness)
        size = int(3 + treb * 15)
        pygame.draw.circle(screen, color, (x, y), size)

    pygame.display.flip()

def main():
    global running
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🎵 BeatLight Flow — Audio Reactive Art")

    thread = threading.Thread(target=audio_thread)
    thread.start()

    clock = pygame.time.Clock()
    hue_shift = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_flow(screen, hue_shift)
        hue_shift += 1
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
