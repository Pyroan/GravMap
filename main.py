# Lol if I was smart I'd figure out a way to not do this
# extremely slowly

# TODO Make this viewport/world space and not just camera space
# TODO figure out examples that are actually stable orbits
# TODO make it so you can supply starting vectors to each mass
# TODO Make each mass visible as a white circle
# TODO arg parse.
# TODO Rolling average for time remaining so it's more stable.
from multiprocessing import Pool

from PIL import Image
from colorsys import hsv_to_rgb
from spacemath import Mass, Vector2
import time

frames_to_render = 300
fps = 30
size = 500, 500
masses = []


# TODO replace with argument input
with open("input.txt") as f:
    for l in f.readlines():
        x, y, mass = list(map(int, l.strip().split(", ")))
        masses.append(Mass(x, y, mass))


def drawChunk(params):
    bounds, masses = params[0], params[1]
    # print(masses[0])
    img = Image.new("RGB", (bounds[2]-bounds[0], bounds[3]-bounds[1]))
    for x in range(bounds[0], bounds[2]):
        for y in range(bounds[1], bounds[3]):
            v = Vector2(0, 0)
            for m in masses:
                v2 = Vector2(m.x, m.y) - Vector2(x, y)
                if v2.magnitude() != 0:
                    v2 *= m.mass / (v2.magnitude()**2)
                v += v2

            theta = v.angle()
            color = tuple(int(l*256) for l in hsv_to_rgb(theta/360, 1, 1))

            img.putpixel((x-bounds[0], y-bounds[1]), color)
    return (img, (bounds[0], bounds[1]))


# Return the drawn image i guess.
def draw(divisions: int):
    # Generate boundries for each chunk...
    x = size[0] // divisions
    y = size[1] // divisions
    bounds = []
    for i in range(divisions):
        for j in range(divisions):
            bounds.append((i*x, j*y, (i+1)*x, (j+1)*y))
        (bounds, masses)

    params = []
    for bound in bounds:
        params.append((bound, masses))

    # Draw each chunk
    with Pool() as pool:
        chunks = pool.map(drawChunk, params)

    # Copy them into the larger image
    img = Image.new("RGB", size)
    for chunk in chunks:
        img.paste(chunk[0], chunk[1])

    return img


def updateBodies():
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
        m.x = int(m.x + m.velocity.x)
        m.y = int(m.y + m.velocity.y)


if __name__ == "__main__":
    timeOfLastFrame = time.time()

    print('\rRendering... {0:.2f}%, {1:4}s remaining'.format(
        0.00, '??'), end='', flush=True)

    frames = []
    for i in range(frames_to_render):
        frames.append(draw(4))
        updateBodies()

        print('\rRendering... {0:.2f}%, {1:4}s remaining'.format(
            (i/frames_to_render) * 100, int(time.time() - timeOfLastFrame)*(frames_to_render-i)), end='', flush=True)
        timeOfLastFrame = time.time()
    frames[0].save("output/test.gif", save_all=True, append_images=frames[1:], optimize=False,
                   duration=1000//fps, loop=0)
