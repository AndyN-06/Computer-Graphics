import math
import numpy as np

import ColorType
from Animation import Animation
from Component import Component
from Light import Light
from Material import Material
from Point import Point
import GLUtility

from DisplayableTorus import DisplayableTorus
from DisplayableCube import DisplayableCube
from DisplayableCylinder import DisplayableCylinder

class SceneThree(Component, Animation):
    lights = None
    lightCubes = None
    shaderProg = None
    glutility = None

    def __init__(self, shaderProg):
        super().__init__(Point((0, 0, 0)))
        self.shaderProg = shaderProg
        self.glutility = GLUtility.GLUtility()

        # Object 1: Torus
        torus = Component(Point((0, 0, 0)), DisplayableTorus(shaderProg, 0.5, 1.0, 36, 36))
        m1 = Material(
            np.array((0.1, 0.1, 0.1, 1.0)),
            np.array((0.5, 0.3, 0.0, 1.0)),
            np.array((0.7, 0.6, 0.5, 1.0)),
            64
        )
        torus.setMaterial(m1)
        torus.renderingRouting = "lighting"
        self.addChild(torus)

        # Object 2: Cube
        cube = Component(Point((2, 0, 0)), DisplayableCube(shaderProg, 1.0))
        m2 = Material(
            np.array((0.1, 0.1, 0.1, 1.0)),
            np.array((0.0, 0.5, 0.5, 1.0)),
            np.array((0.6, 0.7, 0.7, 1.0)),
            32
        )
        cube.setMaterial(m2)
        cube.renderingRouting = "lighting"
        self.addChild(cube)

        # Object 3: Cylinder
        cylinder = Component(Point((-2, 0, 0)), DisplayableCylinder(shaderProg, 0.5, 1.5, 36))
        m3 = Material(
            np.array((0.1, 0.1, 0.1, 1.0)),
            np.array((0.5, 0.0, 0.5, 1.0)),
            np.array((0.7, 0.5, 0.7, 1.0)),
            32
        )
        cylinder.setMaterial(m3)
        cylinder.renderingRouting = "lighting"
        self.addChild(cylinder)

        # Light 1: Spotlight with SOFTGREEN color
        l0 = Light(
            position=np.array([0.0, 5.0, 0.0]),
            color=np.array((*ColorType.RED, 1.0)),
            spotDirection=np.array([0.0, -1.0, 0.0]),
            spotRadialFactor=np.array([.1, 0.1, 0.1]),
            spotAngleLimit=math.cos(math.radians(15.0))
        )
        lightCube0 = Component(
            Point((0.0, 5.0, 0.0)),
            DisplayableCube(shaderProg, 0.3, 0.3, 0.3, ColorType.RED)
        )
        lightCube0.renderingRouting = "vertex"

        # Light 2: Infinite Light with SOFTBLUE color
        l1 = Light(
            color=np.array((*ColorType.SOFTBLUE, 1.0)),
            infiniteDirection=np.array([-1.0, -1.0, 0.0])
        )
        # Light cube to represent the infinite light
        lightCube1 = Component(
            Point((5.0, 5.0, 0.0)),
            DisplayableCube(shaderProg, 0.3, 0.3, 0.3, ColorType.SOFTBLUE)
        )
        lightCube1.renderingRouting = "vertex"

        # Add light cubes to the scene
        self.addChild(lightCube0)
        self.addChild(lightCube1)
        self.lights = [l0, l1]
        self.lightCubes = [lightCube0, lightCube1]

    def animationUpdate(self):
        # No moving lights in this scene
        for i, v in enumerate(self.lights):
            self.shaderProg.setLight(i, v)

    def initialize(self):
        self.shaderProg.clearAllLights()
        for i, v in enumerate(self.lights):
            self.shaderProg.setLight(i, v)
        super().initialize()
