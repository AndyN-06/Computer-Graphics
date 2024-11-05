"""
Model our creature and wrap it in one class
First version at 09/28/2021

:author: micou(Zezhou Sun)
:version: 2021.2.1

Modified by Daniel Scrivener 08/2022

Modified by Andrew Nguyen U10666001:
I created two classes here for the predator and prey that are children of the Linkage class. They inherit all of the functions from the linkage class besides the 
initialization. I did not change the animationUpdate very much besides getting rid of the constant rotation of the creature itself. I used bounding sphere for the
collision detection using Ritter's algorithm. I added helper functions for the collision detection. the stepforward function moves the creatures based on speed, does collision
detection between sphere and walls and handles behavior of creatures in relation to other creatures.
"""
import random

from Component import Component
from Shapes import Cube, Cylinder, Sphere, Cone
from Point import Point
import ColorType as Ct
from EnvironmentObject import EnvironmentObject

# for bounding sphere visualization
from math import sin, cos, pi

# for distance calculations
from math import sqrt
import numpy as np

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
    componentList = None
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

        # I got rid of the rotation here

        ##### BONUS 6: Group behaviors
        # Requirements:
        #   1. Add at least 5 creatures to the vivarium and make it possible for creatures to engage in group behaviors,
        #   for instance flocking together. This can be achieved by implementing the
        #   [Boids animation algorithms](http://www.red3d.com/cwr/boids/) of Craig Reynolds.

        self.update()

        # update bounding sphere based on movements
        # self.boundingSphere()

    # use Ritter's algorithm to find bounding sphere for the creature
    def boundingSphere(self):

        # Start with the creature’s root position (e.g., (1.5, 0, 0))
        root_position = self.currentPos
        
        # Collect all world positions of components
        points = [self.getWorldPos(component, root_position) for component in self.componentList]
        # print(points)

        # find the furthest points for initical bounding sphere
        max_distance = 0
        p1, p2 = points[0], points[0]

        # loop through points to find furthest apart
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                distance = sqrt(
                    (points[j][0] - points[i][0]) ** 2 +
                    (points[j][1] - points[i][1]) ** 2 +
                    (points[j][2] - points[i][2]) ** 2
                )
                if distance > max_distance:
                    max_distance = distance
                    p1, p2 = points[i], points[j]
        
        # set the initial center point and radius based on the furthest points
        center_x = (p1[0] + p2[0]) / 2
        center_y = (p1[1] + p2[1]) / 2
        center_z = (p1[2] + p2[2]) / 2
        radius = sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2) / 2

        # make sure sphere covers entire creature
        for point in points:
            distance = sqrt(
                (point[0] - center_x) ** 2 +
                (point[1] - center_y) ** 2 +
                (point[2] - center_z) ** 2
            )
            if distance > radius:
                # update center and expand based on Ritter's algo
                radius = (radius + distance) / 2
                ratio = (distance - radius) / distance
                center_x += (point[0] - center_x) * ratio
                center_y += (point[1] - center_y) * ratio
                center_z += (point[2] - center_z) * ratio

        # set final bounding sphere
        self.bound_center = Point((center_x, center_y, center_z))
        self.bound_radius = radius

    # helper function to find world position of each component
    def getWorldPos(self, component, root_position):
        # position of creature
        world_position = np.array([root_position[0], root_position[1], root_position[2]])

        # relative position of components
        component_position = np.array([component.currentPos[0], component.currentPos[1], component.currentPos[2]])

        # world position of components
        world_position += component_position

        # Return the world position as a Point
        return Point((world_position[0], world_position[1], world_position[2]))
    

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

        # update the position of creature and its bounding sphere based on the translation spd
        self.currentPos += self.translation_speed
        self.bound_center += self.translation_speed

        # print("spd: ", end =" ")
        # print(self.translation_speed)
        # print("pos: ", end =" ")
        # print(self.currentPos)
        # print("center: ", end =" ")
        # print(self.bound_center)
        # print("rad: ", end =" ")
        # print(self.bound_radius)

        # Retrieve tank boundaries
        length, width, height = tank_dimensions

        # Define bounds based on tank dimensions and center position
        x_min, x_max = -length / 2, length / 2
        y_min, y_max = -width / 2,  width / 2
        z_min, z_max = -height / 2, height / 2

        x_spd, y_spd, z_spd = self.translation_speed

        # Check for wall collisions and reverse direction if necessary
        if self.bound_center[0] - self.bound_radius < x_min or self.bound_center[0] + self.bound_radius > x_max:
            self.translation_speed = Point((x_spd * -1, y_spd, z_spd))  # Reverse X direction

        if self.bound_center[1] - self.bound_radius < y_min or self.bound_center[1] + self.bound_radius > y_max:
            self.translation_speed = Point((x_spd, y_spd * -1, z_spd))  # Reverse Y direction

        if self.bound_center[2] - self.bound_radius < z_min or self.bound_center[2] + self.bound_radius > z_max:
            self.translation_speed = Point((x_spd, y_spd, z_spd * -1))  # Reverse Z direction

        # Initialize closest distance for predator tracking
        closest_prey = None
        min_distance = float('inf')

        for creature in vivarium.components[1:]:  # Skip the tank
            if creature is self:
                continue  # Skip self

            # Check for collision
            if self.creature_collide(self, creature):
                if self.species_id == 1 and creature.species_id == 2:
                    # Predator-prey collision: predator eats prey
                    vivarium.delObjInTank(creature)
                    continue  # Skip further processing for this creature

                elif self.species_id == creature.species_id:
                    # Same-species collision: reflect direction to simulate bounce
                    self.translation_speed = Point((-self.translation_speed[0], -self.translation_speed[1], -self.translation_speed[2]))
                    continue

            # Predator logic: find the closest prey to move toward
            if self.species_id == 1 and creature.species_id == 2:
                distance = self.calc_distance(self.bound_center, creature.bound_center)
                if distance < min_distance:
                    closest_prey = creature
                    min_distance = distance

            # Prey logic: avoid predator if heading toward it
            elif self.species_id == 2 and creature.species_id == 1:
                distance = self.calc_distance(self.bound_center, creature.bound_center)
                if distance < self.bound_radius + creature.bound_radius:
                    # Check if the current direction is toward the predator
                    direction_to_predator = (creature.bound_center - self.bound_center).normalize()
                    current_direction = self.translation_speed.normalize()

                    # Adjust direction if heading toward predator
                    if np.dot(current_direction, direction_to_predator) > 0:
                        # Reflect translation speed to steer away
                        self.translation_speed = Point((-self.translation_speed[0], -self.translation_speed[1], -self.translation_speed[2]))

        # Update predator's direction toward the closest prey
        if self.species_id == 1 and closest_prey:
            # Calculate the magnitude of the current speed
            speed_magnitude = np.sqrt(self.translation_speed[0]**2 + self.translation_speed[1]**2 + self.translation_speed[2]**2)
            
            # Set direction to move toward the closest prey while keeping the same speed
            direction_to_prey = (closest_prey.bound_center - self.bound_center).normalize()
            self.translation_speed = direction_to_prey * speed_magnitude

        self.rotateDirection(self.translation_speed)
        self.update()

    # helper method to get the Euc distance between 2 points
    def calc_distance(self, p1, p2):
        return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2)
    
    # helper method to check if 2 creatures collide or not using bounding spheres
    def creature_collide(self, creature1, creature2):
        distance = self.calc_distance(creature1.bound_center, creature2.bound_center)
        return distance < (creature1.bound_radius + creature2.bound_radius)
    

class Predator(Linkage):

    components = None
    rotation_speed = None
    translation_speed = None

    def __init__(self, parent, position, shaderProg, display_obj=None):
        # super().__init__(position, display_obj, shaderProg)
        super(Linkage, self).__init__(position)
        self.contextParent = parent

        # Makes each body part following format of above class
        body = Cylinder(Point((0, 0, 0)), shaderProg, [0.075, 0.075, 0.250], Ct.GREENYELLOW)

        head = Sphere(Point((0, 0, 0.15625)), shaderProg, [0.125, 0.125, 0.125], Ct.GREENYELLOW)

        leftEye = Sphere(Point((-0.0625, 0.075, 0.075)), shaderProg, [0.008, 0.013, 0.005], Ct.BLACK)
        rightEye = Sphere(Point((0.0625, 0.075, 0.075)), shaderProg, [0.008, 0.013, 0.005], Ct.BLACK)
        mouth = Cylinder(Point((0, -0.0375, 0.1125)), shaderProg, [0.025, 0.025, 0.013], Ct.BLACK)
        mouth.setDefaultAngle(30, self.uAxis)

        leftAnt1 = Cube(Point((-0.05, 0.0875, 0.025)), shaderProg, [0.013, 0.013, 0.075], Ct.BLACK)
        leftAnt2 = Cube(Point((0, 0, 0.075)), shaderProg, [0.013, 0.013, 0.075], Ct.PURPLE)
        leftAnt1.setDefaultAngle(-70, self.uAxis)

        rightAnt1 = Cube(Point((0.05, 0.0875, 0.025)), shaderProg, [0.013, 0.013, 0.075], Ct.BLACK)
        rightAnt2 = Cube(Point((0, 0, 0.075)), shaderProg, [0.013, 0.013, 0.075], Ct.PURPLE)
        rightAnt1.setDefaultAngle(-70, self.uAxis)

        leftLeg1 = Cube(Point((-0.05, -0.05, 0.0625)), shaderProg, [0.05, 0.05, 0.075], Ct.CYAN)
        leftLeg2 = Cube(Point((0, 0, 0.1)), shaderProg, [0.05, 0.05, 0.15], Ct.SILVER)
        leftLeg1.setDefaultAngle(90, self.uAxis)
        leftLeg2.setDefaultAngle(45, self.uAxis)

        rightLeg1 = Cube(Point((0.05, -0.05, 0.0625)), shaderProg, [0.05, 0.05, 0.075], Ct.CYAN)
        rightLeg2 = Cube(Point((0, 0, 0.1)), shaderProg, [0.05, 0.05, 0.15], Ct.SILVER)
        rightLeg1.setDefaultAngle(90, self.uAxis)
        rightLeg2.setDefaultAngle(-45, self.uAxis)

        tail1 = Cylinder(Point((0, 0, -0.165)), shaderProg, [0.075, 0.075, 0.075], Ct.DARKORANGE1)
        tail2 = Cylinder(Point((0, 0, 0.125)), shaderProg, [0.05, 0.05, 0.075], Ct.DARKORANGE2)
        tail3 = Cylinder(Point((0, 0, 0.125)), shaderProg, [0.025, 0.025, 0.075], Ct.DARKORANGE3)
        tailEnd = Cone(Point((0, 0, 0.1)), shaderProg, [0.025, 0.025, 0.025], Ct.DARKORANGE4)

        tail1.setDefaultAngle(180, self.vAxis)
        tail1.setDefaultAngle(-30, self.uAxis)
        tail2.setDefaultAngle(-30, self.uAxis)
        tail3.setDefaultAngle(-30, self.uAxis)


        # set hierarchy
        self.addChild(body)
        body.addChild(head)
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

        self.componentList = [body, head, leftEye, rightEye, mouth, leftAnt1, leftAnt2, rightAnt1, rightAnt2, leftLeg1, leftLeg2, rightLeg1, rightLeg2, tail1, tail2, tail3, tailEnd]

        self.componentDict = {
            "body": body,
            "head": head,
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
        body.setRotateExtent(self.uAxis, 0, 0)
        body.setRotateExtent(self.vAxis, 0, 0)
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
        rightLeg1.setRotateExtent(self.uAxis, 20, 160)
        rightLeg1.setRotateExtent(self.vAxis, 0, 0)
        rightLeg1.setRotateExtent(self.wAxis, 0, 0)

        # right leg 2 rotation
        rightLeg2.setRotateExtent(self.uAxis, 0, 90)
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
        self.rotation_speed = [[1.4, 0, 0], [.9, 0, 0], [-1.4, 0, 0], [.9, 0, 0], [0, 1.4, 0], [0, 1.4, 0], [0, 1.4, 0]]

        # call function to set bounding sphere
        self.boundingSphere()

        # set speed
        self.translation_speed = Point([random.random()-0.5 for _ in range(3)]).normalize() * 0.01
        # self.translation_speed = Point((.01, 0, 0))

        # set species id
        self.species_id = 1


class Prey(Linkage):

    components = None
    rotation_speed = None
    translation_speed = None

    def __init__(self, parent, position, shaderProg, display_obj=None):
        # super().__init__(position, display_obj, shaderProg)
        super(Linkage, self).__init__(position)
        self.contextParent = parent

        head = Sphere(Point((0, 0, 0.100)), shaderProg, [0.067, 0.067, 0.067], Ct.RED)
        eyeL = Sphere(Point((0.034, 0.034, 0.034)), shaderProg, [0.024, 0.024, 0.024], Ct.BLACK)
        eyeR = Sphere(Point((-0.034, 0.034, 0.034)), shaderProg, [0.024, 0.024, 0.024], Ct.BLACK)
        body = Cylinder(Point((0, 0, 0)), shaderProg, [0.067, 0.067, 0.100], Ct.RED)
        tail1 = Sphere(Point((0, 0, 0)), shaderProg, [0.067, 0.067, 0.067], Ct.ORANGE)
        tail1.setDefaultAngle(180, self.vAxis)
        tailend = Cone(Point((0, 0, 0.138)), shaderProg, [0.050, 0.050, 0.100], Ct.YELLOW)
        fin = Sphere(Point((0, 0.067, 0)), shaderProg, [0, 0.050, 0.090], Ct.BLUE)


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
        tail1.setRotateExtent(self.vAxis, 150, 210)
        tail1.setRotateExtent(self.wAxis, 0, 0)

        tailend.setRotateExtent(self.uAxis, -30, 30)
        tailend.setRotateExtent(self.vAxis, -50, 50)
        tailend.setRotateExtent(self.wAxis, 0, 0)

        body.setRotateExtent(self.uAxis, 0, 0)
        body.setRotateExtent(self.vAxis, 0, 0)
        body.setRotateExtent(self.wAxis, 0, 0)

        # list of moveable components
        self.components = [tail1, tailend]

        # set rotation speed for components
        self.rotation_speed = [[0, 6, 0], [0, 10, 0]]

        # call function to set bounding sphere
        self.boundingSphere()

        # set speed
        self.translation_speed = Point([random.random()-0.5 for _ in range(3)]).normalize() * 0.01
        # self.translation_speed = Point((-.01, 0, 0))

        # set species id
        self.species_id = 2


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
