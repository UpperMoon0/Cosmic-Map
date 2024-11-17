from direct.showbase.ShowBase import ShowBase
from panda3d.core import LColor, LineSegs, ClockObject, Vec3
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

        # Create Mars
        self.mars = CelestialBody(self.loader, self.render, "models/misc/sphere", LColor(1, 0, 0, 1), 0.531, "Mars", position=(0, 0, 50))

        # Create Phobos
        self.phobos = CelestialBody(self.loader, self.render, "models/misc/sphere", LColor(0.5, 0.5, 0.5, 1), 0.0018,
                                    "Phobos", parent=self.mars, velocity=2.0, distance=1.47)

        # Create Deimos
        self.deimos = CelestialBody(self.loader, self.render, "models/misc/sphere", LColor(0.5, 0.5, 0.5, 1), 0.001,
                                    "Deimos", parent=self.mars, velocity=1.0, distance=3.68)

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

        # Set the default camera distance (no zoom change)
        self.camera_distance = 30  # Set an appropriate value for the initial camera distance

    def create_body_buttons(self):
        bodies = [self.earth, self.moon, self.mars, self.phobos, self.deimos]
        for i, body in enumerate(bodies):
            DirectButton(text=body.name, scale=0.05, command=self.focus_on_body, extraArgs=[body], parent=self.menu_frame, pos=(0, 0, -0.1 * i))

    def update_positions(self, task):
        self.moon.update_position(task.time)
        self.phobos.update_position(task.time)
        self.deimos.update_position(task.time)

        if self.show_orbit:
            self.draw_orbit_path()

        # Update the camera position if a body is focused
        if self.focused_object:
            self.update_camera_position()

        return task.cont

    def toggle_orbit_path(self):
        self.show_orbit = not self.show_orbit
        if not self.show_orbit:
            self.orbit_path.node().removeAllChildren()

    def draw_orbit_path(self):
        self.orbit_path.node().removeAllChildren()
        segs = LineSegs()
        segs.setColor(1, 1, 1, 1)  # Set the color to white

        bodies = [self.moon, self.phobos, self.deimos]
        for body in bodies:
            if body.parent:
                parent = body.parent
                # Get the position of the parent in 3D space
                parent_pos = parent.model.getPos(self.render)
                distance = body.distance  # Get the distance of the body from its parent

                # Start the orbit path at the correct distance from the parent body (Mars in this case)
                segs.moveTo(parent_pos[0] + distance, parent_pos[1], parent_pos[2])

                # Draw the orbit path as a circle around the parent body
                for i in range(1, 361):
                    angle = i * (pi / 180)
                    x = distance * cos(angle)
                    z = distance * sin(angle)
                    segs.drawTo(parent_pos[0] + x, parent_pos[1], parent_pos[2] + z)

        self.orbit_path.attachNewNode(segs.create())

    def toggle_menu(self):
        if self.menu_frame.isHidden():
            self.menu_frame.show()
        else:
            self.menu_frame.hide()

    def focus_on_body(self, body):
        self.focused_object = body
        self.update_camera_position()

    def update_camera_position(self):
        """Keeps the camera at a constant distance from the focused object and makes it follow."""
        if self.focused_object:
            body_pos = self.focused_object.model.getPos(self.render)

            # Get the direction from the camera to the body
            direction = (body_pos - self.cam.getPos()).normalized()

            # Calculate the new camera position, maintaining the distance
            new_cam_pos = body_pos - direction * self.camera_distance
            self.cam.setPos(new_cam_pos)

            # Ensure the camera always looks at the body
            self.cam.lookAt(self.focused_object.model)


app = MyApp()
app.run()
