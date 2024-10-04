"""
Model our creature and wrap it in one class.
First version on 09/28/2021

:author: micou(Zezhou Sun)
:version: 2021.2.1

----------------------------------

Modified by Daniel Scrivener 09/2023
"""

from Component import Component
from Point import Point
import ColorType as Ct
from Shapes import Cube, Cylinder, Cone, Sphere
import numpy as np


class ModelLinkage(Component):
    """
    Define our linkage model
    """

    ##### TODO 2: Model the Creature
    # Build the class(es) of objects that could utilize your built geometric object/combination classes. E.g., you could define
    # three instances of the cyclinder trunk class and link them together to be the "limb" class of your creature. 
    #
    # In order to simplify the process of constructing your model, the rotational origin of each Shape has been offset by -1/2 * dz,
    # where dz is the total length of the shape along its z-axis. In other words, the rotational origin lies along the smallest 
    # local z-value rather than being at the translational origin, or the object's true center. 
    # 
    # This allows Shapes to rotate "at the joint" when chained together, much like segments of a limb. 
    #
    # In general, you should construct each component such that it is longest in its local z-direction: 
    # otherwise, rotations may not behave as expected.
    #
    # Please see Blackboard for an illustration of how this behavior works.
    components = None
    contextParent = None

    def __init__(self, parent, position, shaderProg, display_obj=None):
        super().__init__(position, display_obj)
        self.contextParent = parent

        

        linkageLength = 0.5
        link1 = Cube(Point((0, 0, 0)), shaderProg, [0.2, 0.2, linkageLength], Ct.DARKORANGE1)
        link2 = Cube(Point((0, 0, linkageLength)), shaderProg, [0.2, 0.2, linkageLength], Ct.DARKORANGE2)
        link3 = Cube(Point((0, 0, linkageLength)), shaderProg, [0.2, 0.2, linkageLength], Ct.DARKORANGE3)
        link4 = Cube(Point((0, 0, linkageLength)), shaderProg, [0.2, 0.2, linkageLength], Ct.DARKORANGE4)

        self.addChild(link1)
        link1.addChild(link2)
        link2.addChild(link3)
        link3.addChild(link4)

        self.componentList = [link1, link2, link3, link4]
        self.componentDict = {
            "link1": link1,
            "link2": link2,
            "link3": link3,
            "link4": link4
        }

# My creature class
class creature(Component):

    def __init__(self, parent, position, shaderProg, display_obj=None):
        super().__init__(position, display_obj)
        self.contextParent = parent

        # Makes each body part following format of above class
        body = Cylinder(Point((0, 0, 0)), shaderProg, [0.3, 0.3, 1], Ct.GREENYELLOW)
        head = Sphere(Point((0, 0, 1.25)), shaderProg, [.5, .5, .5], Ct.GREEN)
        
        nose1 = Cylinder(Point((0, .1, .5)), shaderProg, [.05, .05, .2], Ct.PINK)
        nose2 = Cylinder(Point((0, 0, .4)), shaderProg, [.05, .05, .2], Ct.RED)
        nose2.rotate(30, self.uAxis)

        leftEye = Sphere(Point((-.25, .3, .3)), shaderProg, [.03, .05, .02], Ct.BLACK)
        righttEye = Sphere(Point((.25, .3, .3)), shaderProg, [.03, .05, .02], Ct.BLACK)
        mouth = Cylinder(Point((0, -.15, .45)), shaderProg, [.1, .1, .05], Ct.BLACK)
        mouth.rotate(30, self.uAxis)

        leftAnt1 = Cube(Point((-.2, .6, 0.1)), shaderProg, [.05, .05, .3], Ct.BLACK)
        leftAnt2 = Cube(Point((0, 0, -.3)), shaderProg, [.05, .05, .3], Ct.PURPLE)
        leftAnt1.rotate(90, self.uAxis)

        rightAnt1 = Cube(Point((.2, .6, 0.1)), shaderProg, [.05, .05, .3], Ct.BLACK)
        righttAnt2 = Cube(Point((0, 0, -.3)), shaderProg, [.05, .05, .3], Ct.PURPLE)
        rightAnt1.rotate(90, self.uAxis)

        leftLeg1 = Cube(Point((-.2, -.2, .25)), shaderProg, [.2, .2, .3], Ct.CYAN)
        leftLeg2 = Cube(Point((0, 0, .3)), shaderProg, [.2, .2, .3], Ct.SILVER)
        leftLeg1.rotate(80, self.uAxis)
        leftLeg1.rotate(-20, self.wAxis)

        rightLeg1 = Cube(Point((.2, -.2, .25)), shaderProg, [.2, .2, .3], Ct.CYAN)
        rightLeg2 = Cube(Point((0, 0, .3)), shaderProg, [.2, .2, .3], Ct.SILVER)
        rightLeg1.rotate(80, self.uAxis)
        rightLeg1.rotate(20, self.wAxis)

        tail1 = Cylinder(Point((0, 0, -.66)), shaderProg, [.3, .3, .3], Ct.RED)
        tail2 = Cylinder(Point((0, 0, .5)), shaderProg, [.2, .2, .3], Ct.DARKORANGE2)
        tail3 = Cylinder(Point((0, 0, .5)), shaderProg, [.1, .1, .3], Ct.DARKORANGE4)
        tailEnd = Cone(Point((0, 0, .4)), shaderProg, [.1, .1, .1], Ct.DARKORANGE3)
        tail1.rotate(180, self.vAxis)
        tail1.rotate(-30, self.uAxis)
        tail2.rotate(-30, self.uAxis)
        tail3.rotate(-30, self.uAxis)

        self.addChild(body)
        body.addChild(head)
        head.addChild(nose1)
        nose1.addChild(nose2)
        head.addChild(leftEye)
        head.addChild(righttEye)
        head.addChild(mouth)
        head.addChild(leftAnt1)
        leftAnt1.addChild(leftAnt2)
        head.addChild(rightAnt1)
        rightAnt1.addChild(righttAnt2)
        body.addChild(leftLeg1)
        leftLeg1.addChild(leftLeg2)
        body.addChild(rightLeg1)
        rightLeg1.addChild(rightLeg2)
        body.addChild(tail1)
        tail1.addChild(tail2)
        tail2.addChild(tail3)
        tail3.addChild(tailEnd)

        self.componentList = [body, head, nose1, nose2, leftEye, righttEye, mouth, leftAnt1, leftAnt2, rightAnt1, righttAnt2, leftLeg1, leftLeg2, rightLeg1, rightLeg2, tail1, tail2, tail3, tailEnd]
        self.componentDict = {
            "body": body,
            "head": head,
            "nose1": nose1,
            "nose2": nose2,
            "leftEye": leftEye,
            "rightEye": righttEye,
            "mouth": mouth,
            "leftAnt1": leftAnt1,
            "leftAnt2": leftAnt2,
            "rightAnt1": rightAnt1,
            "rightAnt2": righttAnt2,
            "rightLeg1": rightLeg1,
            "rightLeg2": rightLeg2,
            "leftLeg1": leftLeg1,
            "leftLeg2": leftLeg2,
            "tail1": tail1,
            "tail2": tail2,
            "tail3": tail3,
            "tailEnd": tailEnd
        }
    

        ##### TODO 4: Define creature's joint behavior
        # Requirements:
        #   1. Set a reasonable rotation range for each joint,
        #      so that creature won't intersect itself or bend in unnatural ways
        #   2. Orientation of joint rotations for the left and right parts should mirror each other.