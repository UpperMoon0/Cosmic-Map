from math import sin
from math import cos


class CelestialBody:
    def __init__(self, loader, render, model_path, color, size, name, position=(0, 0, 0), parent=None, velocity=0,
                 distance=0):
        self.model = loader.loadModel(model_path)
        self.model.setColor(color)
        self.model.setScale(size)
        self.model.reparentTo(render)
        self.name = name
        self.parent = parent
        self.velocity = velocity
        self.distance = distance
        self.size = size

        if not self.parent:
            self.model.setPos(position)

    def update_position(self, time):
        if self.parent:
            angle = time * self.velocity
            x = self.parent.model.getX() + self.distance * cos(angle)
            y = self.parent.model.getY()
            z = self.parent.model.getZ() + self.distance * sin(angle)
            self.model.setPos(x, y, z)
