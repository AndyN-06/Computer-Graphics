'''
Define Our class which is stores collision detection and environment information here
Created on Nov 1, 2018

:author: micou(Zezhou Sun)
:version: 2021.1.1

modified by Daniel Scrivener 08/2022
'''

import math
from Point import Point
from Quaternion import Quaternion
import numpy as np


class EnvironmentObject:
    """
    Define properties and interface for a object in our environment
    """
    env_obj_list = None  # list<Environment>
    item_id = 0
    species_id = 0

    bound_radius = None
    bound_center = Point((0,0,0))

    def addCollisionObj(self, a):
        """
        Add an environment object for this creature to interact with
        """
        if isinstance(a, EnvironmentObject):
            self.env_obj_list.append(a)

    def rmCollisionObj(self, a):
        """
        Remove an environment object for this creature to interact with
        """
        if isinstance(a, EnvironmentObject):
            self.env_obj_list.remove(a)

    def animationUpdate(self):
        """
        Perform the next frame of this environment object's animation.
        """
        self.update()

    def stepForward(self):
        """
        Have this environment object take a step forward in the simulation.
        """
        return

    ##### TODO 4: Eyes on the road!
        # Requirements:
        #   1. Creatures should face in the direction they are moving. For instance, a fish should be facing the
        #   direction in which it swims. Remember that we require your creatures to be movable in 3 dimensions,
        #   so they should be able to face any direction in 3D space.
        
    def rotateDirection(self, v1):
        """
        change this environment object's orientation to v1.
        :param v1: targed facing direction
        :type v1: Point
        """
         # Normalize v1 to get the unit vector for the target direction
        target_dir = v1.normalize()

        # Define the current forward direction as the local positive z-axis
        current_dir = Point((0, 0, 1))

        # Calculate rotation axis and angle to align z-axis with the target direction
        rotation_axis = current_dir.cross3d(target_dir)
        rotation_angle = math.acos(current_dir.dot(target_dir) / (current_dir.norm() * target_dir.norm()))

        # Handle the case where no rotation is needed (already facing target direction)
        if rotation_axis.norm() < 1e-6:
            return

        # Normalize rotation axis
        rotation_axis = rotation_axis.normalize()
        sin_half_angle = math.sin(rotation_angle / 2)
        cos_half_angle = math.cos(rotation_angle / 2)

        # Create quaternion components manually
        rotation_quat = Quaternion(
            s=cos_half_angle,
            v0=rotation_axis[0] * sin_half_angle,
            v1=rotation_axis[1] * sin_half_angle,
            v2=rotation_axis[2] * sin_half_angle
        )

        # Convert quaternion to a rotation matrix and set post-rotation
        rotation_matrix = rotation_quat.toMatrix()
        self.setPostRotation(rotation_matrix)