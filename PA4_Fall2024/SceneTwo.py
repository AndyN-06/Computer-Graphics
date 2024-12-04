import math
import numpy as np

import ColorType
from Animation import Animation
from Component import Component
from Light import Light
from Material import Material
from Point import Point
import GLUtility

from DisplayableCube import DisplayableCube
from DisplayableCylinder import DisplayableCylinder
from DisplayableEllipsoid import DisplayableEllipsoid

class SceneTwo(Component, Animation):
    lights = None
    lightCubes = None
    shaderProg = None
    glutility = None

    lRadius = None
    lAngles = None
    lTransformations = None

    def __init__(self, shaderProg):
        super().__init__(Point((0, 0, 0)))
        self.shaderProg = shaderProg
        self.glutility = GLUtility.GLUtility()

        self.lTransformations = [
            self.glutility.translate(0, 2, 0, False),
            self.glutility.rotate(60, [0, 1, 0], False)
        ]
        self.lRadius = 4
        self.lAngles = [0, 0]

        # Object 1: Cube
        cube = Component(Point((-1.5, 0, 0)), DisplayableCube(shaderProg, 1.0))
        m1 = Material(
            np.array((0.2, 0.2, 0.2, 1.0)),
            np.array((0.5, 0.0, 0.0, 1.0)),
            np.array((0.7, 0.6, 0.6, 1.0)),
            32
        )
        cube.setMaterial(m1)
        cube.renderingRouting = "lighting"
        self.addChild(cube)

        # Object 2: Cylinder
        cylinder = Component(Point((0, 0, 0)), DisplayableCylinder(shaderProg, 0.5, 1.5, 36))
        m2 = Material(
            np.array((0.2, 0.2, 0.2, 1.0)),
            np.array((0.0, 0.5, 0.0, 1.0)),
            np.array((0.6, 0.7, 0.6, 1.0)),
            32
        )
        cylinder.setMaterial(m2)
        cylinder.renderingRouting = "lighting"
        self.addChild(cylinder)

        # Object 3: Ellipsoid
        ellipsoid = Component(Point((1.5, 0, 0)), DisplayableEllipsoid(shaderProg, 0.6, 0.9, 0.6, 36, 36))
        m3 = Material(
            np.array((0.2, 0.2, 0.2, 1.0)),
            np.array((0.0, 0.0, 0.5, 1.0)),
            np.array((0.6, 0.6, 0.7, 1.0)),
            32
        )
        ellipsoid.setMaterial(m3)
        ellipsoid.renderingRouting = "lighting"
        self.addChild(ellipsoid)

        # Light 1: Point Light
        l0 = Light(
            position=self.lightPos(self.lRadius, self.lAngles[0], self.lTransformations[0]),
            color=np.array((*ColorType.SOFTGREEN, 1.0)),
            spotRadialFactor=np.array((1.0, 0.0, 0.0))  # No attenuation
        )
        lightCube0 = Component(Point((0, 0, 0)), DisplayableCube(shaderProg, 0.2, 0.2, 0.2, ColorType.SOFTGREEN))
        lightCube0.renderingRouting = "vertex"

        # Light 2: Infinite Light
        l1 = Light(
            color=np.array((*ColorType.SOFTBLUE, 1.0)),
            infiniteDirection=np.array([0.0, -1.0, 0.0])
        )
        # Light cube to represent the infinite light
        lightCube1 = Component(Point((0, 5, 0)), DisplayableCube(shaderProg, 0.2, 0.2, 0.2, ColorType.SOFTBLUE))
        lightCube1.renderingRouting = "vertex"

        self.addChild(lightCube0)
        self.addChild(lightCube1)
        self.lights = [l0, l1]
        self.lightCubes = [lightCube0, lightCube1]

    def lightPos(self, radius, thetaAng, transformationMatrix):
        r = np.zeros(4)
        r[0] = radius * math.cos(thetaAng / 180 * math.pi)
        r[2] = radius * math.sin(thetaAng / 180 * math.pi)
        r[3] = 1
        r = transformationMatrix @ r
        return r[0:3]

    def animationUpdate(self):
        self.lAngles[0] = (self.lAngles[0] + 1.0) % 360
        for i, v in enumerate(self.lights):
            if i == 0:  # Update only the point light position
                lPos = self.lightPos(self.lRadius, self.lAngles[i], self.lTransformations[i])
                self.lightCubes[i].setCurrentPosition(Point(lPos))
                self.lights[i].setPosition(lPos)
            else:
                # Infinite light; keep light cube stationary
                pass
            self.shaderProg.setLight(i, v)

        for c in self.children:
            if isinstance(c, Animation):
                c.animationUpdate()

    def initialize(self):
        self.shaderProg.clearAllLights()
        for i, v in enumerate(self.lights):
            self.shaderProg.setLight(i, v)
        super().initialize()
