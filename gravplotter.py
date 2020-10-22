# Functions for drawing the gravity map
# TODO banding options
import json
from colorsys import hsv_to_rgb
from multiprocessing import Pool

from PIL import Image, ImageDraw

from spacemath import Vector2

with open('config.json') as f:
    config = json.loads(f.read())


def screen_to_world_space(x, y):
    x2 = x - (config['screen_size'][0]//2)
    x2 /= config['ppu']
    y2 = y - (config['screen_size'][1]//2)
    y2 /= config['ppu']
    return Vector2(x2, y2)


def world_to_screen_space(x, y):
    x2 = x * config['ppu']
    x2 += config['screen_size'][0]//2
    y2 = y * config['ppu']
    y2 += config['screen_size'][1]//2
    return Vector2(x2, y2)


def draw_grav_map(img, bounds, masses):
    """Draw the pretty colors at each pixel.

    Basically a really slow fragment shader
    """
    for x in range(bounds[0], bounds[2]):
        for y in range(bounds[1], bounds[3]):
            v = Vector2(0, 0)
            for m in masses:
                v2 = Vector2(m.x, m.y) - screen_to_world_space(x, y)
                if v2.magnitude() != 0:
                    v2 *= m.mass / (v2.magnitude()**2)
                v += v2

            theta = v.angle()
            color = tuple(int(l*256) for l in hsv_to_rgb(theta/360, 1, 1))
            # if theta < 1 or theta > 359 or 179 < theta < 181 or 59 < theta < 61 or 239 < theta < 241 or 119 < theta < 121 or 299 < theta < 301:
            img.putpixel((x-bounds[0], y-bounds[1]), color)


def draw_bodies(img, bounds, masses):
    # honestly probably more complicated than it needed to be but that's what happens when you throw these things together
    draw = ImageDraw.Draw(img)
    for m in masses:
        # first check if the body is in these bounds
        pos = world_to_screen_space(m.x, m.y) - Vector2(bounds[0], bounds[1])
        if pos.x <= img.width + config['ppu']//2 and pos.y <= img.height + config['ppu']//2:
            draw.ellipse([pos.x - (m.mass * config['ppu']//2), pos.y - (m.mass * config['ppu']//2),
                          pos.x + (m.mass * config['ppu']//2), pos.y + (m.mass * config['ppu']//2)],
                         fill=(255, 255, 255))


def draw_chunk(params):
    bounds, masses = params[0], params[1]
    # print(masses[0])
    img = Image.new("RGB", (bounds[2]-bounds[0], bounds[3]-bounds[1]))
    if config['draw_gravmap']:
        draw_grav_map(img, bounds, masses)
    if config['draw_bodies']:
        draw_bodies(img, bounds, masses)
    return (img, (bounds[0], bounds[1]))


def draw(pool: Pool, masses, divisions: int) -> Image:
    """Return the drawn image I guess."""

    # Generate boundaries for each chunk...
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
    chunks = pool.map(draw_chunk, params)

    # Copy them into the larger image
    img = Image.new("RGB", config['screen_size'])
    for chunk in chunks:
        img.paste(chunk[0], chunk[1])

    return img
