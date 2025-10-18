import numpy as np
import sounddevice as sd
import pygame
import threading, requests, time
from io import BytesIO
from PIL import Image

# === CONFIG ===
SAMPLERATE = 44100
CHUNK = 1024
WIDTH, HEIGHT = 900, 700
PIXEL_SIZE = 20  # smaller = more detailed
running = True
bands = {'bass': 0, 'mid': 0, 'treble': 0}

# === 1. Download & prepare album art ===
def get_album_surface(url, size=(400, 400)):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content)).convert("RGB")
    img = img.resize(size)
    mode = img.mode
    data = img.tobytes()
    return img, pygame.image.fromstring(data, size, mode)

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import os

sp = Spotify(auth_manager=SpotifyOAuth(
    scope="user-read-currently-playing",
    # If you set env vars (recommended), you don't need to pass client_id/client_secret here.
    # client_id="...", client_secret="...",
    redirect_uri="http://127.0.0.1:8888/callback",
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
))

# This will open a browser the first run so you can authorize the app
now = sp.current_user_playing_track()
if now and now['item']:
    print("Track:", now['item']['name'], "by", now['item']['artists'][0]['name'])
    album_url = now['item']['album']['images'][0]['url']
    print("Album cover URL:", album_url)


# Example Spotify album URL
ALBUM_URL = album_url #"https://i.scdn.co/image/ab67616d0000b273d7e2f4c7353edc42b4ad479f"
album_img, album_surface = get_album_surface(ALBUM_URL)

# === 2. Audio processing ===
def audio_callback(indata, frames, time_, status):
    global bands
    audio_data = np.mean(indata, axis=1)
    fft = np.fft.rfft(audio_data)
    freq = np.fft.rfftfreq(len(audio_data), 1/SAMPLERATE)
    magnitude = np.abs(fft)

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

# === 3. Visualization ===
def main():
    global running
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🎨 Album Pixel Pulse Visualizer")

    threading.Thread(target=audio_thread, daemon=True).start()
    clock = pygame.time.Clock()

    start_time = time.time()
    pixel_mode = False

    # Precompute center
    center = (WIDTH // 2, HEIGHT // 2)
    base_rect = album_surface.get_rect(center=center)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        elapsed = time.time() - start_time
        if elapsed > 3 and not pixel_mode:
            pixel_mode = True  # switch to pixel art mode
            print("🎆 Switching to pixel mode!")

        screen.fill((0, 0, 0))

        max_val = max(bands.values()) or 1
        bass, mid, treb = [bands[k] / max_val for k in bands]

        if not pixel_mode:
            # --- Regular album art view ---
            scale = 1.0 + 0.1 * bass
            scaled_img = pygame.transform.rotozoom(album_surface, 0, scale)
            rect = scaled_img.get_rect(center=center)
            screen.blit(scaled_img, rect)

            # Overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(int(120 * (bass + mid + treb) / 3))
            overlay.fill((
                int(255 * bass),
                int(255 * mid),
                int(255 * treb)
            ))
            screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        else:
            # --- Pixel mode ---
            small = album_img.resize((album_img.width // PIXEL_SIZE, album_img.height // PIXEL_SIZE))
            pixels = np.array(small)
            pixel_w = album_img.width // small.width
            pixel_h = album_img.height // small.height
            offset_x = WIDTH // 2 - (small.width * pixel_w) // 2
            offset_y = HEIGHT // 2 - (small.height * pixel_h) // 2

            for y in range(small.height):
                for x in range(small.width):
                    r, g, b = pixels[y, x]
                    brightness = (bass + mid + treb) / 3
                    r = min(255, int(r * (0.5 + brightness)))
                    g = min(255, int(g * (0.5 + brightness)))
                    b = min(255, int(b * (0.5 + brightness)))
                    pygame.draw.rect(screen, (r, g, b),
                                     (offset_x + x * pixel_w, offset_y + y * pixel_h,
                                      pixel_w, pixel_h))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()
