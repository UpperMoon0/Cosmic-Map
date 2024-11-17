from direct.showbase.ShowBase import ShowBase
from panda3d.core import LColor, LineSegs
from math import sin, cos, pi

from model.CelestialBody import CelestialBody


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Set the background color to black
        self.setBackgroundColor(0, 0, 0)

        # Create Earth
        self.earth = CelestialBody(self.loader, self.render, "models/misc/sphere", LColor(0, 0, 1, 1), 1)

        # Create Moon
        self.moon = CelestialBody(self.loader, self.render, "models/misc/sphere", LColor(0.5, 0.5, 0.5, 1), 0.27,
                                  parent=self.earth, velocity=0.5, distance=5)

        self.cam.setPos(0, -30, 0)
        self.cam.lookAt(self.earth.model)

        # Add a task to update the celestial bodies' positions
        self.taskMgr.add(self.update_positions, "update_positions")

        # Flag to toggle orbit path display
        self.show_orbit = False

        # Create an empty node for the orbit path
        self.orbit_path = self.render.attachNewNode("orbit_path")

        # Accept the 'O' key to toggle the orbit path
        self.accept("o", self.toggle_orbit_path)

    def update_positions(self, task):
        self.moon.update_position(task.time)

        if self.show_orbit:
            self.draw_orbit_path()

        return task.cont

    def toggle_orbit_path(self):
        self.show_orbit = not self.show_orbit
        if not self.show_orbit:
            self.orbit_path.node().removeAllChildren()

    def draw_orbit_path(self):
        self.orbit_path.node().removeAllChildren()
        segs = LineSegs()
        segs.setColor(1, 1, 1, 1)  # Set the color to white
        y = self.earth.model.getY()  # Get the y coordinate of the Earth
        segs.moveTo(5 * cos(0), y, 5 * sin(0))  # Start at the first point
        for i in range(1, 361):
            angle = i * (pi / 180)
            x = 5 * cos(angle)
            z = 5 * sin(angle)
            segs.drawTo(x, y, z)
        self.orbit_path.attachNewNode(segs.create())


app = MyApp()
app.run()
