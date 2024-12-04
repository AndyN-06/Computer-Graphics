"""
Define Torus here.
First version in 11/01/2021

:author: micou(Zezhou Sun)
:version: 2021.1.1

Andrew Nguyen U10666001
Shape is made using parametric equations of torus. Vertices are connected
with triangles making quads across ring and tube segments
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

##### TODO 6/BONUS 6: Texture Mapping
# Requirements:
#   1. Set up each object's vertex texture coordinates(2D) to the self.vertices 9:11 columns
#   (i.e. the last two columns). Tell OpenGL how to interpret these two columns:
#   you need to set up attribPointer in the Displayable object's initialize method.
#   2. Generate texture coordinates for the torus and sphere. Use “./assets/marble.jpg” for the torus and
#   “./assets/earth.jpg” for the sphere as the texture image.
#   There should be no seams in the resulting texture-mapped model.

class DisplayableTorus(Displayable):
    vao = None
    vbo = None
    ebo = None
    shaderProg = None

    # stores current torus's information, read-only
    nsides = 0
    rings = 0
    innerRadius = 0
    outerRadius = 0
    color = None

    vertices = None
    indices = None

    def __init__(self, shaderProg, innerRadius=0.25, outerRadius=0.5, nsides=36, rings=36, color=ColorType.BLACK):
        super(DisplayableTorus, self).__init__()
        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()  # vbo can only be initiate with glProgram activated
        self.ebo = EBO()

        self.generate(innerRadius, outerRadius, nsides, rings, color)

    def generate(self, innerRadius=0.25, outerRadius=0.5, nsides=36, rings=36, color=None):
        self.innerRadius = innerRadius
        self.outerRadius = outerRadius
        self.nsides = nsides
        self.rings = rings
        self.color = color

        # we need to pad one more row for both nsides and rings, to assign correct texture coord to them
        # self.vertices = np.zeros([(nsides) * (rings), 11])

        # self.indices = np.zeros(0)

        # Total number of vertices
        numVertices = (rings + 1) * (nsides + 1)
        self.vertices = np.zeros([numVertices, 11])  # 11 attributes: position(3), normal(3), color(3), texCoords(2)

        # Total number of indices
        numIndices = rings * nsides * 6  # 2 triangles per quad * 3 vertices each
        self.indices = np.zeros([numIndices], dtype=np.uint32)

        # Generate vertices
        vertexIndex = 0
        for i in range(rings + 1):  # Rings (u angle)
            u = i * (2 * math.pi / rings)
            cos_u = math.cos(u)
            sin_u = math.sin(u)

            for j in range(nsides + 1):  # Tube (v angle)
                v = j * (2 * math.pi / nsides)
                cos_v = math.cos(v)
                sin_v = math.sin(v)

                # Compute position
                x = (outerRadius + innerRadius * cos_v) * cos_u
                y = (outerRadius + innerRadius * cos_v) * sin_u
                z = innerRadius * sin_v

                # Compute normal
                nx = cos_v * cos_u
                ny = cos_v * sin_u
                nz = sin_v

                # Compute texture coordinates
                u_tex = i / rings
                v_tex = j / nsides

                # Add to vertices array
                self.vertices[vertexIndex] = [x, y, z, nx, ny, nz, *color, u_tex, v_tex]
                vertexIndex += 1

        # Generate indices
        index = 0
        for i in range(rings):  # Iterate over rings
            for j in range(nsides):  # Iterate over sides
                # Vertex indices for the two triangles forming a quad
                topLeft = i * (nsides + 1) + j
                bottomLeft = (i + 1) * (nsides + 1) + j
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

        self.vao.unbind()
