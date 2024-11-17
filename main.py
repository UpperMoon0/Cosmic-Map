from direct.showbase.ShowBase import ShowBase
from panda3d.core import LColor, LineSegs
from math import sin, cos, pi


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Set the background color to black
        self.setBackgroundColor(0, 0, 0)

        # Load the default sphere model for Earth
        self.earth = self.loader.loadModel("models/misc/sphere")
        self.earth.setColor(LColor(0, 0, 1, 1))  # Set the color to blue
        self.earth.reparentTo(self.render)
        self.earth.setPos(0, 10, 0)

        # Load the default sphere model for Moon
        self.moon = self.loader.loadModel("models/misc/sphere")
        self.moon.setColor(LColor(0.5, 0.5, 0.5, 1))  # Set the color to gray
        self.moon.setScale(0.27)  # Scale the moon to 0.27 times the size of Earth
        self.moon.reparentTo(self.render)

        self.cam.setPos(0, -30, 0)
        self.cam.lookAt(self.earth)

        # Add a task to update the moon's position
        self.taskMgr.add(self.update_moon, "update_moon")

        # Flag to toggle orbit path display
        self.show_orbit = False

        # Create an empty node for the orbit path
        self.orbit_path = self.render.attachNewNode("orbit_path")

        # Accept the 'O' key to toggle the orbit path
        self.accept("o", self.toggle_orbit_path)

    def update_moon(self, task):
        angle = task.time * 0.5  # Adjust the speed of the orbit
        x = 5 * cos(angle)
        y = 10
        z = 5 * sin(angle)
        self.moon.setPos(x, y, z)

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
        for i in range(360):
            angle = i * (pi / 180)
            x = 5 * cos(angle)
            z = 5 * sin(angle)
            segs.drawTo(x, 10, z)
        self.orbit_path.attachNewNode(segs.create())


app = MyApp()
app.run()
