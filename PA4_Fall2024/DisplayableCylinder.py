'''
Andrew Nguyen U10666001
This file creates the cylinder class. It has all the initial components of other shapes. It uses cylinder formula
to create vertices and connect the vertices in the index array
'''


from Displayable import Displayable
from GLBuffer import VAO, VBO, EBO
import numpy as np
import ColorType
import math

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


class DisplayableCylinder(Displayable):
    vao = None
    vbo = None
    ebo = None
    shaderProg = None

    vertices = None
    indices = None

    # Cylinder properties
    radius = None
    height = None
    slices = None
    color = None

    def __init__(self, shaderProg, radius=0.5, height=1.0, slices=36, color=ColorType.BLACK):
        super(DisplayableCylinder, self).__init__()
        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()
        self.ebo = EBO()

        self.generate(radius, height, slices, color)

    # arbitrary values based on size of other shapes
    def generate(self, radius=0.5, height=1.0, slices=36, color=None):
        self.radius = radius
        self.height = height
        self.slices = slices
        self.color = color

        # Number of vertices and indices
        numVertices = (slices + 1) * 2 + 2
        numIndices = slices * 12

        self.vertices = np.zeros([numVertices, 11])
        self.indices = np.zeros([numIndices], dtype=np.uint32)

        # Generate vertices
        vertexIndex = 0
        for i in range(slices + 1):
            theta = i * (2 * math.pi / slices)
            cos_theta = math.cos(theta)
            sin_theta = math.sin(theta)

            # Top circle vertex
            x_top = radius * cos_theta
            y_top = radius * sin_theta
            z_top = height / 2

            # Bottom circle vertex
            x_bottom = radius * cos_theta
            y_bottom = radius * sin_theta
            z_bottom = -height / 2

            # Top vertex
            self.vertices[vertexIndex] = [x_top, y_top, z_top, cos_theta, sin_theta, 0, *color, i / slices, 1]
            vertexIndex += 1

            # Bottom vertex
            self.vertices[vertexIndex] = [x_bottom, y_bottom, z_bottom, cos_theta, sin_theta, 0, *color, i / slices, 0]
            vertexIndex += 1

        # Add center vertices for the top and bottom caps
        # Top center
        self.vertices[vertexIndex] = [0, 0, height / 2, 0, 0, 1, *color, 0.5, 1]
        topCenterIndex = vertexIndex
        vertexIndex += 1

        # Bottom center
        self.vertices[vertexIndex] = [0, 0, -height / 2, 0, 0, -1, *color, 0.5, 0]
        bottomCenterIndex = vertexIndex

        # Generate indices
        index = 0
        for i in range(slices):
            top1 = i * 2
            bottom1 = i * 2 + 1
            top2 = (i + 1) * 2
            bottom2 = (i + 1) * 2 + 1

            # Side quad
            self.indices[index] = top1
            self.indices[index + 1] = bottom1
            self.indices[index + 2] = top2

            self.indices[index + 3] = top2
            self.indices[index + 4] = bottom1
            self.indices[index + 5] = bottom2
            index += 6

            # Top cap triangle
            self.indices[index] = top1
            self.indices[index + 1] = top2
            self.indices[index + 2] = topCenterIndex
            index += 3

            # Bottom cap triangle
            self.indices[index] = bottom1
            self.indices[index + 1] = bottom2
            self.indices[index + 2] = bottomCenterIndex
            index += 3

    def draw(self):
        self.vao.bind()
        self.ebo.draw()
        self.vao.unbind()

    def initialize(self):

        self.vao.bind()
        self.vbo.setBuffer(self.vertices, 11)
        self.ebo.setBuffer(self.indices)

        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexPos"),
                                  stride=11, offset=0, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexNormal"),
                                  stride=11, offset=3, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexColor"),
                                  stride=11, offset=6, attribSize=3)
        self.vao.unbind()
