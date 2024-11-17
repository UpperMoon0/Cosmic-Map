from direct.showbase.ShowBase import ShowBase
from panda3d.core import LColor
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

    def update_moon(self, task):
        angle = task.time * 0.5  # Adjust the speed of the orbit
        x = 5 * cos(angle)
        y = 10
        z = 5 * sin(angle)
        self.moon.setPos(x, y, z)
        return task.cont

app = MyApp()
app.run()