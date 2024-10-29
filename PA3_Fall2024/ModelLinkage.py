"""
Model our creature and wrap it in one class
First version at 09/28/2021

:author: micou(Zezhou Sun)
:version: 2021.2.1

Modified by Daniel Scrivener 08/2022
"""
import random

from Component import Component
from Shapes import Cube, Cylinder, Sphere, Cone
from Point import Point
import ColorType as Ct
from EnvironmentObject import EnvironmentObject

try:
    import OpenGL

    try:
        import OpenGL.GL as gl
        import OpenGL.GLU as glu
    except ImportError:
        from ctypes import util

        orig_util_find_library = util.find_library


        def new_util_find_library(name):
            res = orig_util_find_library(name)
            if res:
                return res
            return '/System/Library/Frameworks/' + name + '.framework/' + name


        util.find_library = new_util_find_library
        import OpenGL.GL as gl
        import OpenGL.GLU as glu
except ImportError:
    raise ImportError("Required dependency PyOpenGL not present")

##### TODO 1: Construct your two different creatures
# Requirements:
#   1. For the basic parts of your creatures, feel free to use routines provided with the previous assignment.
#   You are also free to create your own basic parts, but they must be polyhedral (solid).
#   2. The creatures you design should have moving linkages of the basic parts: legs, arms, wings, antennae,
#   fins, tentacles, etc.
#   3. Model requirements:
#         1. Predator: At least one (1) creature. Should have at least two moving parts in addition to the main body
#         2. Prey: At least two (2) creatures. The two prey can be instances of the same design. Should have at
#         least one moving part.
#         3. The predator and prey should have distinguishable different colors.
#         4. You are welcome to reuse your PA2 creature in this assignment.

class Linkage(Component, EnvironmentObject):
    """
    A Linkage with animation enabled and is defined as an object in environment
    """
    components = None
    rotation_speed = None
    translation_speed = None

    def __init__(self, parent, position, shaderProg):
        super(Linkage, self).__init__(position)
        arm1 = ModelArm(parent, Point((0, 0, 0)), shaderProg, 0.1)
        arm2 = ModelArm(parent, Point((0, 0, 0)), shaderProg, 0.1)
        arm2.setDefaultAngle(120, arm2.vAxis)
        arm3 = ModelArm(parent, Point((0, 0, 0)), shaderProg, 0.1)
        arm3.setDefaultAngle(240, arm3.vAxis)

        self.components = arm1.components + arm2.components + arm3.components
        self.addChild(arm1)
        self.addChild(arm2)
        self.addChild(arm3)

        self.rotation_speed = []
        for comp in self.components:

            comp.setRotateExtent(comp.uAxis, 0, 35)
            comp.setRotateExtent(comp.vAxis, -45, 45)
            comp.setRotateExtent(comp.wAxis, -45, 45)
            self.rotation_speed.append([0.5, 0, 0])

        self.translation_speed = Point([random.random()-0.5 for _ in range(3)]).normalize() * 0.01

        self.bound_center = Point((0, 0, 0))
        self.bound_radius = 0.1 * 4
        self.species_id = 1

    def animationUpdate(self):
        ##### TODO 2: Animate your creature!
        # Requirements:
        #   1. Set reasonable joints limit for your creature
        #   2. The linkages should move back and forth in a periodic motion, as the creatures move about the vivarium.
        #   3. Your creatures should be able to move in 3 dimensions, not only on a plane.

        # create periodic animation for creature joints
        for i, comp in enumerate(self.components):
            comp.rotate(self.rotation_speed[i][0], comp.uAxis)
            comp.rotate(self.rotation_speed[i][1], comp.vAxis)
            comp.rotate(self.rotation_speed[i][2], comp.wAxis)
            if comp.uAngle in comp.uRange:  # rotation reached the limit
                self.rotation_speed[i][0] *= -1
            if comp.vAngle in comp.vRange:
                self.rotation_speed[i][1] *= -1
            if comp.wAngle in comp.wRange:
                self.rotation_speed[i][2] *= -1
        self.vAngle = (self.vAngle + 3) % 360

        ##### BONUS 6: Group behaviors
        # Requirements:
        #   1. Add at least 5 creatures to the vivarium and make it possible for creatures to engage in group behaviors,
        #   for instance flocking together. This can be achieved by implementing the
        #   [Boids animation algorithms](http://www.red3d.com/cwr/boids/) of Craig Reynolds.

        self.update()

    def stepForward(self, components, tank_dimensions, vivarium):

        ##### TODO 3: Interact with the environment
        # Requirements:
        #   1. Your creatures should always stay within the fixed size 3D "tank". You should do collision detection
        #   between the creature and the tank walls. When it hits the tank walls, it should turn and change direction to stay
        #   within the tank.
        #   2. Your creatures should have a prey/predator relationship. For example, you could have a bug being chased
        #   by a spider, or a fish eluding a shark. This means your creature should react to other creatures in the tank.
        #       1. Use potential functions to change its direction based on other creatures’ location, their
        #       inter-creature distances, and their current configuration.
        #       2. You should detect collisions between creatures.
        #           1. Predator-prey collision: The prey should disappear (get eaten) from the tank.
        #           2. Collision between the same species: They should bounce apart from each other. You can use a
        #           reflection vector about a plane to decide the after-collision direction.
        #       3. You are welcome to use bounding spheres for collision detection.

        pass

class Predator(Linkage):

    components = None
    rotation_speed = None
    translation_speed = None

    def __init__(self, parent, position, shaderProg, display_obj=None):
        super().__init__(position, display_obj)
        self.contextParent = parent

        # Makes each body part following format of above class
        body = Cylinder(Point((0, 0, 0)), shaderProg, [0.15, 0.15, 0.5], Ct.GREENYELLOW)

        head = Sphere(Point((0, 0, 1.25 / 2)), shaderProg, [0.25, 0.25, 0.25], Ct.GREENYELLOW)

        nose1 = Cylinder(Point((0, 0.1 / 2, 0.5 / 2)), shaderProg, [0.025, 0.025, 0.1], Ct.PINK)
        nose2 = Cylinder(Point((0, 0, 0.4 / 2)), shaderProg, [0.025, 0.025, 0.1], Ct.PINK)
        nose2.setDefaultAngle(30, self.uAxis)

        leftEye = Sphere(Point((-0.25 / 2, 0.3 / 2, 0.3 / 2)), shaderProg, [0.015, 0.025, 0.01], Ct.BLACK)
        rightEye = Sphere(Point((0.25 / 2, 0.3 / 2, 0.3 / 2)), shaderProg, [0.015, 0.025, 0.01], Ct.BLACK)
        mouth = Cylinder(Point((0, -0.15 / 2, 0.45 / 2)), shaderProg, [0.05, 0.05, 0.025], Ct.BLACK)
        mouth.setDefaultAngle(30, self.uAxis)

        leftAnt1 = Cube(Point((-0.2 / 2, 0.35 / 2, 0.1 / 2)), shaderProg, [0.025, 0.025, 0.15], Ct.BLACK)
        leftAnt2 = Cube(Point((0, 0, 0.3 / 2)), shaderProg, [0.025, 0.025, 0.15], Ct.PURPLE)
        leftAnt1.setDefaultAngle(-70, self.uAxis)

        rightAnt1 = Cube(Point((0.2 / 2, 0.35 / 2, 0.1 / 2)), shaderProg, [0.025, 0.025, 0.15], Ct.BLACK)
        rightAnt2 = Cube(Point((0, 0, 0.3 / 2)), shaderProg, [0.025, 0.025, 0.15], Ct.PURPLE)
        rightAnt1.setDefaultAngle(-70, self.uAxis)

        leftLeg1 = Cube(Point((-0.2 / 2, -0.2 / 2, 0.25 / 2)), shaderProg, [0.1, 0.1, 0.15], Ct.CYAN)
        leftLeg2 = Cube(Point((0, 0, 0.4 / 2)), shaderProg, [0.1, 0.1, 0.3], Ct.SILVER)
        leftLeg1.setDefaultAngle(90, self.uAxis)
        leftLeg2.setDefaultAngle(45, self.uAxis)
        # leftLeg1.setDefaultAngle(-20, self.wAxis)

        rightLeg1 = Cube(Point((0.2 / 2, -0.2 / 2, 0.25 / 2)), shaderProg, [0.1, 0.1, 0.15], Ct.CYAN)
        rightLeg2 = Cube(Point((0, 0, 0.4 / 2)), shaderProg, [0.1, 0.1, 0.3], Ct.SILVER)
        rightLeg1.setDefaultAngle(-90, self.uAxis)
        rightLeg1.setDefaultAngle(180, self.vAxis)
        rightLeg2.setDefaultAngle(-45, self.uAxis)
        # rightLeg1.setDefaultAngle(20, self.wAxis)

        tail1 = Cylinder(Point((0, 0, -0.66 / 2)), shaderProg, [0.15, 0.15, 0.15], Ct.DARKORANGE1)
        tail2 = Cylinder(Point((0, 0, 0.5 / 2)), shaderProg, [0.1, 0.1, 0.15], Ct.DARKORANGE2)
        tail3 = Cylinder(Point((0, 0, 0.5 / 2)), shaderProg, [0.05, 0.05, 0.15], Ct.DARKORANGE3)
        tailEnd = Cone(Point((0, 0, 0.4 / 2)), shaderProg, [0.05, 0.05, 0.05], Ct.DARKORANGE4)
        tail1.setDefaultAngle(180, self.vAxis)
        tail1.setDefaultAngle(-30, self.uAxis)
        tail2.setDefaultAngle(-30, self.uAxis)
        tail3.setDefaultAngle(-30, self.uAxis)

        # set hierarchy
        self.addChild(body)
        body.addChild(head)
        head.addChild(nose1)
        nose1.addChild(nose2)
        head.addChild(leftEye)
        head.addChild(rightEye)
        head.addChild(mouth)
        head.addChild(leftAnt1)
        leftAnt1.addChild(leftAnt2)
        head.addChild(rightAnt1)
        rightAnt1.addChild(rightAnt2)
        body.addChild(leftLeg1)
        leftLeg1.addChild(leftLeg2)
        body.addChild(rightLeg1)
        rightLeg1.addChild(rightLeg2)
        body.addChild(tail1)
        tail1.addChild(tail2)
        tail2.addChild(tail3)
        tail3.addChild(tailEnd)

        self.componentList = [body, head, nose1, nose2, leftEye, rightEye, mouth, leftAnt1, leftAnt2, rightAnt1, rightAnt2, leftLeg1, leftLeg2, rightLeg1, rightLeg2, tail1, tail2, tail3, tailEnd]

        self.componentDict = {
            "body": body,
            "head": head,
            "nose1": nose1,
            "nose2": nose2,
            "leftEye": leftEye,
            "rightEye": rightEye,
            "mouth": mouth,
            "leftAnt1": leftAnt1,
            "leftAnt2": leftAnt2,
            "rightAnt1": rightAnt1,
            "rightAnt2": rightAnt2,
            "rightLeg1": rightLeg1,
            "rightLeg2": rightLeg2,
            "leftLeg1": leftLeg1,
            "leftLeg2": leftLeg2,
            "tail1": tail1,
            "tail2": tail2,
            "tail3": tail3,
            "tailEnd": tailEnd
        }

        # main body rotation extents 
        body.setRotateExtent(self.uAxis, -90, 90)
        body.setRotateExtent(self.vAxis, -90, 90)
        body.setRotateExtent(self.wAxis, 0, 0)

        # left leg 1 rotation
        leftLeg1.setRotateExtent(self.uAxis, 20, 160)
        leftLeg1.setRotateExtent(self.vAxis, 0, 0)
        leftLeg1.setRotateExtent(self.wAxis, 0, 0)

        # left leg 2 rotation
        leftLeg2.setRotateExtent(self.uAxis, 0, 90)
        leftLeg2.setRotateExtent(self.vAxis, 0, 0)
        leftLeg2.setRotateExtent(self.wAxis, 0, 0)

        # right leg 1 rotation
        rightLeg1.setRotateExtent(self.uAxis, -160, -20)
        rightLeg1.setRotateExtent(self.vAxis, 0, 0)
        rightLeg1.setRotateExtent(self.wAxis, 0, 0)

        # right leg 2 rotation
        rightLeg2.setRotateExtent(self.uAxis, -90, 0)
        rightLeg2.setRotateExtent(self.vAxis, 0, 0)
        rightLeg2.setRotateExtent(self.wAxis, 0, 0)

        # tail 1 rotation
        tail1.setRotateExtent(self.uAxis, 0, 0)
        tail1.setRotateExtent(self.vAxis, 110, 250)
        tail1.setRotateExtent(self.wAxis, 0, 0)

        # tail 2 rotation
        tail2.setRotateExtent(self.uAxis, 0, 0)
        tail2.setRotateExtent(self.vAxis, -70, 70)
        tail2.setRotateExtent(self.wAxis, 0, 0)

        # tail 3 rotation
        tail3.setRotateExtent(self.uAxis, 0, 0)
        tail3.setRotateExtent(self.vAxis, -70, 70)
        tail3.setRotateExtent(self.wAxis, 0, 0)

        # tail end rotation
        tailEnd.setRotateExtent(self.uAxis, 0, 0)
        tailEnd.setRotateExtent(self.vAxis, 0, 0)
        tailEnd.setRotateExtent(self.wAxis, 0, 0)

        # this is list of moveable components: legs and tail
        self.components = [leftLeg1, leftLeg2, rightLeg1, rightLeg2, tail1, tail2, tail3]

        # set rotation speeds for each component
        self.rotation_speed = [[1.4, 0, 0], [.9, 0, 0], [1.4, 0, 0], [.9, 0, 0], [0, .5, 0], [0, .5, 0], [0, .5, 0]]


    # def animationUpdate(self):
    #     for i, comp in enumerate(self.components):
    #         comp.rotate(self.rotation_speed[i][0], comp.uAxis)
    #         comp.rotate(self.rotation_speed[i][1], comp.vAxis)
    #         comp.rotate(self.rotation_speed[i][2], comp.wAxis)
    #         if comp.uAngle in comp.uRange:  # rotation reached the limit
    #             self.rotation_speed[i][0] *= -1
    #         if comp.vAngle in comp.vRange:
    #             self.rotation_speed[i][1] *= -1
    #         if comp.wAngle in comp.wRange:
    #             self.rotation_speed[i][2] *= -1
    #     self.vAngle = (self.vAngle + 3) % 360

    #     self.update()

class Prey(Linkage):

    components = None
    rotation_speed = None
    translation_speed = None

    def __init__(self, parent, position, shaderProg, display_obj=None):
        super().__init__(position, display_obj)
        self.contextParent = parent

        head = Sphere(Point((0, 0, 0.2)), shaderProg, [0.133, 0.133, 0.133], Ct.RED)
        eyeL = Sphere(Point((0.067, 0.067, 0.067)), shaderProg, [0.047, 0.047, 0.047], Ct.BLACK)
        eyeR = Sphere(Point((-0.067, 0.067, 0.067)), shaderProg, [0.047, 0.047, 0.047], Ct.BLACK)
        body = Cylinder(Point((0, 0, 0)), shaderProg, [0.133, 0.133, 0.2], Ct.RED)
        tail1 = Sphere(Point((0, 0, 0)), shaderProg, [0.133, 0.133, 0.133], Ct.ORANGE)
        tail1.setDefaultAngle(180, self.vAxis)
        tailend = Cone(Point((0, 0, 0.275)), shaderProg, [0.1, 0.1, 0.2], Ct.YELLOW)
        fin = Sphere(Point((0, .133, 0)), shaderProg, [0, .1, .18], Ct.BLUE)

        self.addChild(body)
        body.addChild(head)
        head.addChild(eyeL)
        head.addChild(eyeR)
        body.addChild(tail1)
        tail1.addChild(tailend)
        body.addChild(fin)

        self.componentList = [body, head, tail1, tailend, eyeR, eyeL, fin]
        self.componentDict = {
            "body": body,
            "head": head,
            "tail1": tail1,
            "tailend": tailend,
            "eyeL": eyeL,
            "eyeR": eyeR,
            "fin": fin
        }

        tail1.setRotateExtent(self.uAxis, -30, 30)
        tail1.setRotateExtent(self.vAxis, 110, 250)
        tail1.setRotateExtent(self.wAxis, 0, 0)

        tailend.setRotateExtent(self.uAxis, -30, 30)
        tailend.setRotateExtent(self.vAxis, -70, 70)
        tailend.setRotateExtent(self.wAxis, 0, 0)

        # list of moveable components
        self.components = [tail1, tailend]

        # set rotation speed for components
        self.rotation_speed = [[.5, .5, 0], [.5, .5, 0]]

    # def animationUpdate(self):
    #     for i, comp in enumerate(self.components):
    #         comp.rotate(self.rotation_speed[i][0], comp.uAxis)
    #         comp.rotate(self.rotation_speed[i][1], comp.vAxis)
    #         comp.rotate(self.rotation_speed[i][2], comp.wAxis)
    #         if comp.uAngle in comp.uRange:  # rotation reached the limit
    #             self.rotation_speed[i][0] *= -1
    #         if comp.vAngle in comp.vRange:
    #             self.rotation_speed[i][1] *= -1
    #         if comp.wAngle in comp.wRange:
    #             self.rotation_speed[i][2] *= -1
    #     self.vAngle = (self.vAngle + 3) % 360

    #     self.update()


class ModelArm(Component):
    """
    Define our linkage model
    """

    components = None
    contextParent = None

    def __init__(self, parent, position, shaderProg, linkageLength=0.5, display_obj=None):
        super().__init__(position, display_obj)
        self.components = []
        self.contextParent = parent

        link1 = Cube(Point((0, 0, 0)), shaderProg, [linkageLength / 4, linkageLength / 4, linkageLength], Ct.DARKORANGE1)
        link2 = Cube(Point((0, 0, linkageLength)), shaderProg, [linkageLength / 4, linkageLength / 4, linkageLength], Ct.DARKORANGE2)
        link3 = Cube(Point((0, 0, linkageLength)), shaderProg, [linkageLength / 4, linkageLength / 4, linkageLength], Ct.DARKORANGE3)
        link4 = Cube(Point((0, 0, linkageLength)), shaderProg, [linkageLength / 4, linkageLength / 4, linkageLength], Ct.DARKORANGE4)

        self.addChild(link1)
        link1.addChild(link2)
        link2.addChild(link3)
        link3.addChild(link4)

        self.components = [link1, link2, link3, link4]
