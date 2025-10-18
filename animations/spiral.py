from itertools import product, count
from math import sin, cos, pi

import pygame

SIDE = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((SIDE, SIDE))
screen.fill(WHITE)

VARIABLE = 20

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
    return (
        SIDE // 2
        + (1 + sin(time) / variant)
        * percentage * (SIDE // 3) * cos(variant * pi * percentage + time),
        SIDE // 2
        + (1 + sin(time) / VARIABLE)
        * percentage * (SIDE // 3) * sin(variant * pi * percentage + time),
    )


def background(time, variant):
    some_meaningful_number=30*variant
    rgb_code = (
        (some_meaningful_number + int(abs(30 * sin(0.05 * time))))%255,
        (some_meaningful_number + int(abs(30 * sin(0.05 * time))))%255,
        (some_meaningful_number + int(abs(30 * sin(0.05 * time))))%255
    )
    return rgb_code

def fg(time):
    return (
        255 - int(abs(15 * sin(0.1 * time))),
        85 + int(abs(160 * sin(0.1 * time))),
        85 + int(abs(60 * sin(0.1 * time))),
    )

STEPS = 3000
step_count = 0.01
tick = 1
while tick < STEPS:
    screen.fill(background(tick, variant=VARIABLE))
    clr = fg(tick)
    for step in range(STEPS + 1):
        percentage = step / STEPS
        x, y = rotating_spiral(percentage, tick, VARIABLE*step+1)
        draw_pixel(screen, x, y, clr)
    pygame.display.flip()
    tick += step_count
