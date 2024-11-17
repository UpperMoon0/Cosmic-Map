# model/CelestialBody.py
from math import sin, cos


class CelestialBody:
    def __init__(self, loader, render, model_path, color, scale, parent=None, velocity=0, distance=0):
        self.model = loader.loadModel(model_path)
        self.model.setColor(color)
        self.model.setScale(scale)
        self.model.reparentTo(render)
        self.parent = parent
        self.velocity = velocity
        self.distance = distance

    def update_position(self, time):
        if self.parent:
            angle = time * self.velocity
            x = self.distance * cos(angle)
            y = self.parent.model.getY()
            z = self.distance * sin(angle)
            self.model.setPos(x, y, z)
