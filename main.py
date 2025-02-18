from direct.showbase.ShowBase import ShowBase
from panda3d.core import LColor, LineSegs, ClockObject, Vec3, Point3
from direct.gui.DirectGui import DirectButton, DirectFrame, DirectCheckButton, DirectLabel, DirectOptionMenu
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode
from math import sin, cos, pi

from model.CelestialBody import CelestialBody

EARTH_SIZE_KM = 12742  # Earth's diameter in km; 1 game unit equals 1 Earth size

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.focused_object = None  # initialize focused_object to avoid AttributeError
        self.distance_unit = "km"  # new property: "km" or "mi"

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

        # Set the frame rate to 60 FPS
        globalClock = ClockObject.getGlobalClock()
        globalClock.setMode(ClockObject.MLimited)
        globalClock.setFrameRate(60)

        # Set initial camera distance (no zoom change)
        self.camera_distance = 30  # default distance

        # Store camera lens for coordinate projection and adjust near clipping plane for small distances
        self.camLens = self.cam.node().getLens()
        self.camLens.setNear(0.001)

        # Create name labels for each celestial body (fixed-size, 2D)
        self.create_labels()
        self.taskMgr.add(self.update_labels, "update_labels")

        # Orbit path node (for drawing orbits)
        self.orbit_path = self.render.attachNewNode("orbit_path")

        # Initialize toggle settings
        self.show_orbits = False
        self.show_names = True
        self.show_distances = False

        # Create control menu (initially hidden) to toggle options and focus on bodies using M key
        self.create_control_menu()
        self.accept("m", self.toggle_control_menu)

    def update_positions(self, task):
        # Update positions of orbiting bodies
        self.moon.update_position(task.time)
        self.phobos.update_position(task.time)
        self.deimos.update_position(task.time)

        # Draw orbit paths if enabled
        if self.show_orbits:
            self.draw_orbit_path()
        else:
            self.orbit_path.node().removeAllChildren()

        # Update the camera position if a body is focused
        if self.focused_object:
            self.update_camera_position()

        return task.cont

    def draw_orbit_path(self):
        self.orbit_path.node().removeAllChildren()
        segs = LineSegs()
        segs.setColor(1, 1, 1, 1)  # white color

        # Draw orbits for bodies that orbit a parent
        for body in [self.moon, self.phobos, self.deimos]:
            if body.parent:
                parent = body.parent
                parent_pos = parent.model.getPos(self.render)
                distance = body.distance  # orbital radius from parent
                segs.moveTo(parent_pos[0] + distance, parent_pos[1], parent_pos[2])
                for i in range(1, 361):
                    angle = i * (pi / 180)
                    x = distance * cos(angle)
                    z = distance * sin(angle)
                    segs.drawTo(parent_pos[0] + x, parent_pos[1], parent_pos[2] + z)

        self.orbit_path.attachNewNode(segs.create())

    def focus_on_body(self, body):
        """Focus on the given body and auto-adjust the camera zoom based on the body's size."""
        self.focused_object = body
        scale = body.model.getScale()[0]  # uniform scaling assumed
        computed_distance = scale * 30  # dynamic distance calculation
        # Enforce a minimum distance to avoid camera clipping issues
        self.camera_distance = max(computed_distance, 5)
        self.update_camera_position()

    def update_camera_position(self):
        """Keeps the camera at a constant distance from the focused object and makes it follow."""
        if self.focused_object:
            body_pos = self.focused_object.model.getPos(self.render)
            direction = (body_pos - self.cam.getPos()).normalized()
            new_cam_pos = body_pos - direction * self.camera_distance
            self.cam.setPos(new_cam_pos)
            self.cam.lookAt(self.focused_object.model)

    def create_labels(self):
        """
        Creates a fixed-size text label for each celestial body.
        These labels are parented to aspect2d so that their size on screen remains constant.
        """
        self.labels = {}
        bodies = [self.earth, self.moon, self.mars, self.phobos, self.deimos]
        for body in bodies:
            self.labels[body.name] = OnscreenText(text=body.name,
                                                    pos=(0, 0),
                                                    scale=0.07,
                                                    fg=(1, 1, 1, 1),
                                                    align=TextNode.ACenter,
                                                    mayChange=True,
                                                    parent=self.aspect2d)

    def update_labels(self, task):
        """
        Projects each celestial body's 3D position to 2D screen coordinates and updates its label.
        If 'Show Names' is enabled, it displays the name (and optionally, the distance from the camera).
        """
        for body in [self.earth, self.moon, self.mars, self.phobos, self.deimos]:
            label = self.labels[body.name]
            if self.show_names:
                # Calculate distance from camera to the object if needed
                text = body.name
                if self.show_distances:
                    # Compute the true world center using the model's bounding volume,
                    # so the label stays centered even when the camera rotates.
                    local_center = body.model.getBounds().getCenter()
                    world_center = body.model.getMat(self.render).xformPoint(local_center)
                    pos3d = self.cam.getRelativePoint(self.render, world_center)
                    distance = (world_center - self.cam.getPos(self.render)).length() * EARTH_SIZE_KM
                    if self.distance_unit == "mi":
                        distance_mi = distance * 0.621371  # convert km to miles
                        text += " (%.2f mi)" % distance_mi
                    else:
                        text += " (%.2f km)" % distance
                label.setText(text)

                pos3d = self.cam.getRelativePoint(self.render, body.model.getPos(self.render))
                pos2d = Point3()
                if self.camLens.project(pos3d, pos2d):
                    label.setPos(pos2d.getX(), pos2d.getY())
                    label['align'] = TextNode.ACenter  # ensure the label remains centered
                    label.show()
                else:
                    label.hide()
            else:
                label.hide()

        return task.cont

    def create_control_menu(self):
        """
        Creates a control menu with checkboxes for toggling options:
        "Show Orbits", "Show Names", and "Show Distances".
        Also creates buttons to focus on specific celestial bodies.
        The menu is toggled by pressing the "M" key.
        """
        # Main container for the control menu in the top left
        self.control_menu = DirectFrame(parent=self.aspect2d,
                                        pos=(-1, 0, 0.85),
                                        frameColor=(0, 0, 0, 0))
        self.control_menu.hide()  # start hidden

        # --- Toggle Options Frame ---
        self.toggle_frame = DirectFrame(parent=self.control_menu,
                                        pos=(0, 0, 0),
                                        frameColor=(0.2, 0.2, 0.2, 0.8),
                                        frameSize=(0, 0.6, -0.35, 0))
        # Checkbox: Show Orbits
        self.cb_show_orbits = DirectCheckButton(parent=self.toggle_frame,
                                                text="Show Orbits",
                                                scale=0.05,
                                                pos=(0.05, 0, -0.1),
                                                command=self.set_show_orbits)
        # Checkbox: Show Names
        self.cb_show_names = DirectCheckButton(parent=self.toggle_frame,
                                               text="Show Names",
                                               scale=0.05,
                                               pos=(0.05, 0, -0.2),
                                               command=self.set_show_names)
        # Set initial state to checked for names
        self.cb_show_names["indicatorValue"] = 1

        # Checkbox: Show Distances
        self.cb_show_distances = DirectCheckButton(parent=self.toggle_frame,
                                                   text="Show Distances",
                                                   scale=0.05,
                                                   pos=(0.05, 0, -0.3),
                                                   command=self.set_show_distances)
        # OptionMenu: Distance Unit toggle (km or mi)
        self.om_distance_unit = DirectOptionMenu(parent=self.toggle_frame,
                                                   text="Distance Unit",
                                                   scale=0.05,
                                                   pos=(0.05, 0, -0.4),
                                                   items=["km", "mi"],
                                                   initialitem=0,
                                                   command=self.set_distance_unit)

        # --- Focus Menu Frame ---
        self.focus_frame = DirectFrame(parent=self.control_menu,
                                       pos=(0, 0, -0.4),
                                       frameColor=(0.2, 0.2, 0.2, 0.8),
                                       frameSize=(0, 0.6, -0.35, 0))
        # Label for focus menu
        DirectLabel(parent=self.focus_frame,
                    text="Focus on Body",
                    scale=0.05,
                    pos=(0.3, 0, -0.05),
                    frameColor=(0, 0, 0, 0))
        bodies = [self.earth, self.moon, self.mars, self.phobos, self.deimos]
        for i, body in enumerate(bodies):
            DirectButton(parent=self.focus_frame,
                         text=body.name,
                         scale=0.05,
                         pos=(0.25, 0, -0.15 - i * 0.1),
                         command=self.focus_on_body,
                         extraArgs=[body])

    def set_show_orbits(self, status):
        self.show_orbits = bool(status)
        if not self.show_orbits:
            self.orbit_path.node().removeAllChildren()

    def set_show_names(self, status):
        self.show_names = bool(status)
        if not self.show_names:
            for label in self.labels.values():
                label.hide()

    def set_show_distances(self, status):
        self.show_distances = bool(status)

    def set_distance_unit(self, selection):
        self.distance_unit = selection

    def toggle_control_menu(self):
        if self.control_menu.isHidden():
            self.control_menu.show()
        else:
            self.control_menu.hide()


app = MyApp()
app.run()
