from math import atan, degrees, sqrt

# In retrospect I'm sure there's a library that'll do this all for me.


class Vector2:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def magnitude(self) -> float:
        return sqrt(self.x*self.x + self.y*self.y)

    # This is way too complicated for what it should be. Hecking atan.
    def angle(self) -> float:
        if self.x == 0:
            if self.y == 0:
                theta = 0.0
            elif self.y > 0:
                theta = 90.0
            elif self.y < 0:
                theta = 270.0
            return theta
        else:
            theta = degrees(atan(self.y/self.x))

        if self.x < 0:
            theta += 180
        elif self.y < 0:
            theta += 360

        return theta

    def __str__(self):
        return "Vector2: ({},{})".format(self.x, self.y)

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        return Vector2(self.x * other, self.y * other)


class Mass:
    velocity = Vector2(0, 0)

    def __init__(self, x: float, y: float, mass: float, xvel: float = 0, yvel: float = 0):
        self.x = x
        self.y = y
        self.mass = mass
        self.velocity = Vector2(xvel, yvel)

    def __str__(self):
        return"x: {}, y: {}, mass: {}".format(self.x, self.y, self.mass)
