# Lol if I was smart I'd figure out a way to not do this
# extremely slowly

# TODO figure out examples that are actually stable orbits
# TODO make it so you can supply starting vectors to each mass
# TODO Make each mass visible as a white circle
# TODO arg parse.
# TODO Rolling average for time remaining so it's more stable.
from multiprocessing import Pool
from colorsys import hsv_to_rgb
import time
import json

from PIL import Image, ImageDraw

from spacemath import Mass, Vector2

with open('config.json') as f:
    config = json.loads(f.read())

masses = []

# TODO replace with argument input
with open("input.txt") as f:
    for l in f.readlines():
        x, y, mass, xvel, yvel = list(map(float, l.strip().split(", ")))
        masses.append(Mass(x, y, mass, xvel, yvel))


def screenToWorldSpace(x, y):
    x2 = x - (config['screen_size'][0]//2)
    x2 /= config['ppu']
    y2 = y - (config['screen_size'][1]//2)
    y2 /= config['ppu']
    return Vector2(x2, y2)


def worldToScreenSpace(x, y):
    x2 = x * config['ppu']
    x2 += config['screen_size'][0]//2
    y2 = y * config['ppu']
    y2 += config['screen_size'][1]//2
    return Vector2(x2, y2)


def drawChunk(params):
    bounds, masses = params[0], params[1]
    # print(masses[0])
    img = Image.new("RGB", (bounds[2]-bounds[0], bounds[3]-bounds[1]))
    if config['draw_gravmap']:
        for x in range(bounds[0], bounds[2]):
            for y in range(bounds[1], bounds[3]):
                v = Vector2(0, 0)
                for m in masses:
                    v2 = Vector2(m.x, m.y) - screenToWorldSpace(x, y)
                    if v2.magnitude() != 0:
                        v2 *= m.mass / (v2.magnitude()**2)
                    v += v2

                theta = v.angle()
                color = tuple(int(l*256) for l in hsv_to_rgb(theta/360, 1, 1))

                img.putpixel((x-bounds[0], y-bounds[1]), color)
    # honestly probably more complicated than it needed to be but that's what happens when you throw these things together
    if config['draw_bodies']:
        draw = ImageDraw.Draw(img)
        for m in masses:
            # first check if the body is in these bounds
            pos = worldToScreenSpace(m.x, m.y) - Vector2(bounds[0], bounds[1])
            if pos.x <= img.width + config['ppu']//2 and pos.y <= img.height + config['ppu']//2:
                draw.ellipse([pos.x - (m.mass * config['ppu']//2), pos.y - (m.mass * config['ppu']//2),
                              pos.x + (m.mass * config['ppu']//2), pos.y + (m.mass * config['ppu']//2)],
                             fill=(255, 255, 255))
    return (img, (bounds[0], bounds[1]))


# Return the drawn image i guess.
def draw(pool: Pool, divisions: int):
    # Generate boundries for each chunk...
    x = config['screen_size'][0] // divisions
    y = config['screen_size'][1] // divisions
    bounds = []
    for i in range(divisions):
        for j in range(divisions):
            bounds.append((i*x, j*y, (i+1)*x, (j+1)*y))
        (bounds, masses)

    params = []
    for bound in bounds:
        params.append((bound, masses))

    # Draw each chunk
    chunks = pool.map(drawChunk, params)

    # Copy them into the larger image
    img = Image.new("RGB", config['screen_size'])
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
        m.x = m.x + m.velocity.x
        m.y = m.y + m.velocity.y


if __name__ == "__main__":
    timeOfLastFrame = time.time()

    print('\rRendering... {0:.2f}%, {1:4}s remaining'.format(
        0.00, '  ??'), end='', flush=True)

    if config['animated']:
        frames = []
        with Pool() as pool:
            for i in range(config['frames_to_render']):
                frames.append(draw(pool, 8))
                updateBodies()

                print('\rRendering... {0:.2f}%, {1:4}s remaining'.format(
                    (i/config['frames_to_render']) * 100, int((time.time() - timeOfLastFrame)*(config['frames_to_render']-i))), end='', flush=True)
                timeOfLastFrame = time.time()
        frames[0].save("output/out.gif", save_all=True, append_images=frames[1:], optimize=False,
                       duration=1000//config['fps'], loop=0)
    else:
        with Pool() as pool:
            img = draw(pool, 4)
            img.save("output/out.png")
