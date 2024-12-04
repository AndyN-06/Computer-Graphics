"""
Define displayable cube here. Current version only use VBO
First version in 10/20/2021

:author: micou(Zezhou Sun)
:version: 2021.1.1

Andrew Nguyen U10666001
I made a new vertices array that has 4 vertices for each face. I then made a indices
array that connected the vertices using triangles to create the cube. I made the color
of the cube black to work with changes i made in glprogram and switched the ebo.
"""

from Displayable import Displayable
from GLBuffer import VAO, VBO, EBO
import numpy as np
import ColorType

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


class DisplayableCube(Displayable):
    vao = None
    vbo = None
    ebo = None
    shaderProg = None

    vertices = None  # array to store vertices information
    indices = None  # stores triangle indices to vertices

    # stores current cube's information, read-only
    length = None
    width = None
    height = None
    color = None

    def __init__(self, shaderProg, length=1, width=1, height=1, color=ColorType.BLACK):
        super(DisplayableCube, self).__init__()
        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()  # vbo can only be initiate with glProgram activated
        self.ebo = EBO()

        self.generate(length, width, height, color)

    def generate(self, length=1, width=1, height=1, color=None):
        self.length = length
        self.width = width
        self.height = height
        self.color = color

        lx = length / 2
        wy = width / 2
        hz = height / 2

        # vertices
        self.vertices = np.array([
            # Front face
            -lx, -wy, hz,  0, 0, 1, *color,  # Bottom left
            lx, -wy, hz,  0, 0, 1, *color,  # Bottom right
            lx,  wy, hz,  0, 0, 1, *color,  # Top right
            -lx,  wy, hz,  0, 0, 1, *color,  # Top left

            # Back face
            -lx, -wy, -hz,  0, 0, -1, *color,
            -lx,  wy, -hz,  0, 0, -1, *color,
            lx,  wy, -hz,  0, 0, -1, *color,
            lx, -wy, -hz,  0, 0, -1, *color,

            # Left face
            -lx, -wy, -hz, -1, 0, 0, *color,
            -lx, -wy,  hz, -1, 0, 0, *color,
            -lx,  wy,  hz, -1, 0, 0, *color,
            -lx,  wy, -hz, -1, 0, 0, *color,

            # Right face
            lx, -wy, -hz, 1, 0, 0, *color,
            lx,  wy, -hz, 1, 0, 0, *color,
            lx,  wy,  hz, 1, 0, 0, *color,
            lx, -wy,  hz, 1, 0, 0, *color,

            # Top face
            -lx,  wy, -hz, 0, 1, 0, *color,
            -lx,  wy,  hz, 0, 1, 0, *color,
            lx,  wy,  hz, 0, 1, 0, *color,
            lx,  wy, -hz, 0, 1, 0, *color,

            # Bottom face
            -lx, -wy, -hz, 0, -1, 0, *color,
            lx, -wy, -hz, 0, -1, 0, *color,
            lx, -wy,  hz, 0, -1, 0, *color,
            -lx, -wy,  hz, 0, -1, 0, *color,
        ], dtype=np.float32)

        # indices array to create cube
        self.indices = np.array([
            # Front face
            0, 1, 2,
            2, 3, 0,

            # Back face
            4, 5, 6,
            6, 7, 4,

            # Left face
            8, 9, 10,
            10, 11, 8,

            # Right face
            12, 13, 14,
            14, 15, 12,

            # Top face
            16, 17, 18,
            18, 19, 16,

            # Bottom face
            20, 21, 22,
            22, 23, 20,
        ], dtype=np.uint32)

    def draw(self):
        self.vao.bind()
        # TODO 1.1 is at here, switch from vbo to ebo
        # self.vbo.draw()
        self.ebo.draw()
        self.vao.unbind()

    def initialize(self):
        """
        Remember to bind VAO before this initialization. If VAO is not bind, program might throw an error
        in systems that don't enable a default VAO after GLProgram compilation
        """
        self.vao.bind()
        self.vbo.setBuffer(self.vertices, 9)
        self.ebo.setBuffer(self.indices)

        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexPos"),
                                  stride=9, offset=0, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexNormal"),
                                  stride=9, offset=3, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexColor"),
                                  stride=9, offset=6, attribSize=3)
        # TODO/BONUS 6.1 is at here, you need to set attribPointer for texture coordinates
        # you should check the corresponding variable name in GLProgram and set the pointer
        self.vao.unbind()

