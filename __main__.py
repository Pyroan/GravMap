# Lol if I was smart I'd figure out a way to not do this
# extremely slowly

# TODO figure out examples that are actually stable orbits
# TODO Rolling average for time remaining so it's more stable.
import argparse
import json
from multiprocessing import Pool
import time

from PIL import Image, ImageDraw

from spacemath import Mass, Vector2
from gravplotter import draw

with open('config.json') as f:
    config = json.loads(f.read())


def update_bodies(masses):
    """Move each body to its new location and update its velocity."""

    # Compute velocity for each body which is necessarily n^2 LAME
    for i in range(len(masses)):
        v = Vector2(0, 0)
        for m in masses[i+1:] + masses[:i]:
            v2 = Vector2(m.x, m.y) - Vector2(masses[i].x, masses[i].y)
            if v2.magnitude() != 0:
                v2 *= m.mass / (v2.magnitude()**2)
            v += v2
        masses[i].velocity += v
    # Actually move them
    for m in masses:
        m.x = m.x + m.velocity.x
        m.y = m.y + m.velocity.y


if __name__ == "__main__":
    masses = []

    # TODO replace with argument input
    with open("input/3bodies.txt") as f:
        for l in f.readlines():
            x, y, mass, xvel, yvel = list(map(float, l.strip().split(", ")))
            masses.append(Mass(x, y, mass, xvel, yvel))

    timeOfLastFrame = time.time()

    print('\rRendering... {0:.2f}%, {1:4}s remaining'.format(
        0.00, '  ??'), end='', flush=True)

    if config['animated']:
        # frames = []
        with Pool() as pool:
            for i in range(config['frames_to_render']):
                # frames.append(draw(pool, 8))
                draw(pool, masses, 8).save(
                    "output/mp4testbodies/{}.png".format(i))
                update_bodies(masses)

                print('\rRendering... {0:.2f}%, {1:4}s remaining'.format((
                    i/config['frames_to_render']) * 100,
                    int((time.time() - timeOfLastFrame)*(config['frames_to_render']-i))),
                    end='',
                    flush=True)
                timeOfLastFrame = time.time()

        # frames[0].save("output/equidistant.gif", save_all=True, append_images=frames[1:], optimize=False,
                #    duration=1000//config['fps'], loop=0)
        # Print final state of all objects so we can stitch together smaller gifs into larger ones.
        if config['dump_final_state']:
            for m in masses:
                print("\n" + str(m))
    else:
        with Pool() as pool:
            img = draw(pool, masses, 4)
            img.save("output/0.png")
