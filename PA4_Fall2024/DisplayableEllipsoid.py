"""
Define ellipsoid here.
First version in 11/01/2021

:author: micou(Zezhou Sun)
:version: 2021.1.1

Andrew Nguyen U10666001
Shape is made by iteratively calculating vertices using the parametric equations for
ellipsoid in cartesian coords. triangles form strips across stacks and slices to make
surface.
"""

from Displayable import Displayable
from GLBuffer import VAO, VBO, EBO
from Point import Point
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


class DisplayableEllipsoid(Displayable):
    vao = None
    vbo = None
    ebo = None
    shaderProg = None

    # stores current torus's information, read-only
    stacks = 0
    slices = 0
    radiusX = 0
    radiusY = 0
    radiusZ = 0
    color = None

    vertices = None
    indices = None

    def __init__(self, shaderProg, radiusX=0.6, radiusY=0.3, radiusZ=0.9, stacks=18, slices=36, color=ColorType.BLACK):
        super(DisplayableEllipsoid, self).__init__()
        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()  # vbo can only be initiate with glProgram activated
        self.ebo = EBO()

        self.generate(radiusX, radiusY, radiusZ, stacks, slices, color)

    def generate(self, radiusX=0.6, radiusY=0.3, radiusZ=0.9, stacks=18, slices=36, color=None):
        self.radiusX = radiusX
        self.radiusY = radiusY
        self.radiusZ = radiusZ
        self.stacks = stacks
        self.slices = slices
        self.color = color

        # we need to pad two more rows for poles and one more column for slice seam, to assign correct texture coord
        # self.vertices = np.zeros([(stacks) * (slices), 11])

        # self.indices = np.zeros(0)
        # Total number of vertices (including duplicate for texture seam)
        numVertices = (stacks + 1) * (slices + 1)
        self.vertices = np.zeros([numVertices, 11])  # 11 attributes: position(3), normal(3), color(3), texCoords(2)

        # Create vertices
        vertexIndex = 0
        for i in range(stacks + 1):  # Iterate over latitude (stacks)
            phi = -math.pi / 2 + i * (math.pi / stacks)  # From -pi/2 to pi/2
            for j in range(slices + 1):  # Iterate over longitude (slices)
                theta = j * (2 * math.pi / slices)  # From 0 to 2*pi

                # Cartesian coordinates
                x = radiusX * math.cos(phi) * math.cos(theta)
                y = radiusY * math.cos(phi) * math.sin(theta)
                z = radiusZ * math.sin(phi)

                # Normal vector (normalized position on unit sphere)
                nx = math.cos(phi) * math.cos(theta)
                ny = math.cos(phi) * math.sin(theta)
                nz = math.sin(phi)

                # Texture coordinates
                u = j / slices  # Longitude
                v = i / stacks  # Latitude

                # Add to vertices array
                self.vertices[vertexIndex] = [x, y, z, nx, ny, nz, *color, u, v]
                vertexIndex += 1

        # Create indices for triangle strips
        numIndices = stacks * slices * 6  # 2 triangles per patch * 3 vertices each
        self.indices = np.zeros([numIndices], dtype=np.uint32)

        index = 0
        for i in range(stacks):  # Iterate over latitude strips
            for j in range(slices):  # Iterate over longitude segments
                # Indices for the two triangles forming a quad
                topLeft = i * (slices + 1) + j
                bottomLeft = (i + 1) * (slices + 1) + j
                topRight = topLeft + 1
                bottomRight = bottomLeft + 1

                # First triangle
                self.indices[index] = topLeft
                self.indices[index + 1] = bottomLeft
                self.indices[index + 2] = topRight

                # Second triangle
                self.indices[index + 3] = topRight
                self.indices[index + 4] = bottomLeft
                self.indices[index + 5] = bottomRight

                index += 6

    def draw(self):
        self.vao.bind()
        self.ebo.draw()
        self.vao.unbind()

    def initialize(self):
        """
        Remember to bind VAO before this initialization. If VAO is not bind, program might throw an error
        in systems which don't enable a default VAO after GLProgram compilation
        """
        self.vao.bind()
        self.vbo.setBuffer(self.vertices, 11)
        self.ebo.setBuffer(self.indices)

        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexPos"),
                                  stride=11, offset=0, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexNormal"),
                                  stride=11, offset=3, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexColor"),
                                  stride=11, offset=6, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexTexture"),
                                  stride=11, offset=9, attribSize=2)
        self.vao.unbind()
