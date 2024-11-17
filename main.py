from direct.showbase.ShowBase import ShowBase
from panda3d.core import LColor, LineSegs, ClockObject
from direct.gui.DirectGui import DirectButton, DirectFrame
from math import sin, cos, pi

from model.CelestialBody import CelestialBody


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Set the background color to black
        self.setBackgroundColor(0, 0, 0)

        # Create Earth
        self.earth = CelestialBody(self.loader, self.render, "models/misc/sphere", LColor(0, 0, 1, 1), 1, "Earth")

        # Create Moon
        self.moon = CelestialBody(self.loader, self.render, "models/misc/sphere", LColor(0.5, 0.5, 0.5, 1), 0.27,
                                  "Moon", parent=self.earth, velocity=0.5, distance=30.1)

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

        # Set the frame rate to 60 FPS
        globalClock = ClockObject.getGlobalClock()
        globalClock.setMode(ClockObject.MLimited)
        globalClock.setFrameRate(60)

        # Create the 2D menu
        self.menu_frame = DirectFrame(frameColor=(0, 0, 0, 0.5), frameSize=(-0.5, 0.5, -0.5, 0.5), pos=(0, 0, 0))
        self.menu_frame.hide()

        # Create buttons for each celestial body
        self.create_body_buttons()

        # Accept the 'T' key to toggle the menu
        self.accept("t", self.toggle_menu)

        # Attribute to keep track of the currently focused object
        self.focused_object = None

        # Add a task to update the camera position
        self.taskMgr.add(self.update_camera_position, "update_camera_position")

    def create_body_buttons(self):
        bodies = [self.earth, self.moon]
        for i, body in enumerate(bodies):
            DirectButton(text=body.name, scale=0.05, command=self.focus_on_body, extraArgs=[body], parent=self.menu_frame, pos=(0, 0, -0.1 * i))

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
        distance = self.moon.distance  # Get the distance of the Moon from the Earth
        segs.moveTo(distance * cos(0), y, distance * sin(0))  # Start at the first point
        for i in range(1, 361):
            angle = i * (pi / 180)
            x = distance * cos(angle)
            z = distance * sin(angle)
            segs.drawTo(x, y, z)
        self.orbit_path.attachNewNode(segs.create())

    def toggle_menu(self):
        if self.menu_frame.isHidden():
            self.menu_frame.show()
        else:
            self.menu_frame.hide()

    def focus_on_body(self, body):
        self.focused_object = body

    def update_camera_position(self, task):
        if self.focused_object:
            self.cam.lookAt(self.focused_object.model)
        return task.cont


app = MyApp()
app.run()