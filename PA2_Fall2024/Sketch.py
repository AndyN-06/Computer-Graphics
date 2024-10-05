"""
This is the main entry of your program. Almost all things you need to implement are in this file.
The main class Sketch inherits from CanvasBase. For the parts you need to implement, they are all marked with TODO.
First version Created on 09/28/2018

:author: micou(Zezhou Sun)
:version: 2021.1.1

Modified by Daniel Scrivener 07/2022

Modified by Andrew Nguyen U10666001
- added variable in the Sketch class called selected_components that holds all selected components
for the multi-select feature. It is then initialized to empty in the __init__ function

- changed keyboard interrupt function
    - pressing enter/return now doesnt always set axis to 0, which is red for u axis. It also only reset the color
    of the last selected component if it wasn't selected for multi-select
    - added a press tab to add the currently selected component to the multi-select list
    - left/right were changed so they change the color of every component selected instead of just current
    - 5 poses were added to keys 1-5 for the test cases

- ScrollINterrupt changed so that it can rotate every component multi-selected

"""

import math

import numpy as np
from ModelAxes import ModelAxes
from ModelLinkage import ModelLinkage

# import my creature class
from ModelLinkage import creature

import ColorType
from Point import Point
from CanvasBase import CanvasBase
from GLProgram import GLProgram
from Quaternion import Quaternion
import GLUtility

try:
    import wx
    from wx import glcanvas
except ImportError:
    raise ImportError("Required dependency wxPython not present")
try:
    # From pip package "Pillow"
    from PIL import Image
except:
    print("Need to install PIL package. Pip package name is Pillow")
    raise ImportError
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


class Sketch(CanvasBase):
    """
    Drawing methods and interrupt methods will be implemented in this class.
    
    Variable Instruction:
        * debug(int): Define debug level for log printing

        * 0 for stable version, minimum log is printed
        * 1 will print general logs for lines and triangles
        * 2 will print more details and do some type checking, which might be helpful in debugging

        
    Method Instruction:
        
        
    Here are the list of functions you need to override:
        * Interrupt_MouseL: Used to deal with mouse click interruption. Canvas will be refreshed with updated buff
        * Interrupt_MouseLeftDragging: Used to deal with mouse dragging interruption.
        * Interrupt_Keyboard: Used to deal with keyboard press interruption. Use this to add new keys or new methods
        
    Here are some public variables in parent class you might need:
        
        
    """
    context = None

    debug = 1

    last_mouse_leftPosition = None
    last_mouse_middlePosition = None
    components = None

    texture = None
    shaderProg = None
    glutility = None

    lookAtPt = None
    upVector = None
    backgroundColor = None
    # use these three to control camera position, mainly used in mouse dragging
    cameraDis = None
    cameraTheta = None  # theta on horizontal sphere cut, in range [0, 2pi]
    cameraPhi = None  # in range [-pi, pi], for smooth purpose

    viewMat = None
    perspMat = None

    select_obj_index = -1 # index of selected component in self.components
    select_axis_index = -1  # index of selected axis
    select_color = [ColorType.ColorType(1, 0, 0), ColorType.ColorType(0, 1, 0), ColorType.ColorType(0, 0, 1)]
    
    # list to hold selected components
    selected_components = []

    # If you are having trouble rotating the camera, try increasing this parameter
    # (Windows users with trackpads may need this)
    MOUSE_ROTATE_SPEED = 1
    MOUSE_SCROLL_SPEED = 2.5

    def __init__(self, parent):
        super(Sketch, self).__init__(parent)
        # prepare OpenGL context
        contextAttrib = glcanvas.GLContextAttrs()
        contextAttrib.PlatformDefaults().CoreProfile().MajorVersion(3).MinorVersion(3).EndList()
        self.context = glcanvas.GLContext(self, ctxAttrs=contextAttrib)
        # Initialize Parameters
        self.last_mouse_leftPosition = [0, 0]
        self.last_mouse_middlePosition = [0, 0]
        self.backgroundColor = ColorType.BLUEGREEN

        # initialize selected components list
        self.selected_components = []

        # add components to top level
        self.resetView()

        self.glutility = GLUtility.GLUtility()

    def resetView(self):
        self.lookAtPt = [0, 0, 0]
        self.upVector = [0, 1, 0]
        self.cameraDis = 6
        self.cameraPhi = math.pi / 6
        self.cameraTheta = math.pi / 2

        
    def InitGL(self):
        """
        Called once in order to initialize the OpenGL environemnt.
        You must set your model here (and not in __init__)
        due to the fact that the shader is only compiled once we reach this function.
        """
        self.shaderProg = GLProgram()
        self.shaderProg.compile()

        ##### TODO 3: Initialize your model
        # You should initialize your model here.
        # self.topLevelComponent should refer to your model
        # and self.components should refer to your model's components.
        # Optionally, you can create a dictionary (self.cDict) to index your model's components by name.

        model = creature(self, Point((0, 0, 0)), self.shaderProg)
        axes = ModelAxes(self, Point((-1, -1, -1)), self.shaderProg)

        self.topLevelComponent.clear()
        self.topLevelComponent.addChild(model)
        self.topLevelComponent.addChild(axes)
        self.topLevelComponent.initialize()

        self.components = model.componentList
        self.cDict = model.componentDict

        gl.glClearColor(*self.backgroundColor, 1.0)
        gl.glClearDepth(1.0)
        gl.glViewport(0, 0, self.size[0], self.size[1])

        # enable depth checking
        gl.glEnable(gl.GL_DEPTH_TEST)

        # set basic viewing matrix
        self.perspMat = self.glutility.perspective(45, self.size.width, self.size.height, 0.01, 100)
        self.shaderProg.setMat4("projectionMat", self.perspMat)
        self.shaderProg.setMat4("viewMat", self.glutility.view(self.getCameraPos(), self.lookAtPt, self.upVector))
        self.shaderProg.setMat4("modelMat", np.identity(4))

    def getCameraPos(self):
        ct = math.cos(self.cameraTheta)
        st = math.sin(self.cameraTheta)
        cp = math.cos(self.cameraPhi)
        sp = math.sin(self.cameraPhi)
        result = [self.lookAtPt[0] + self.cameraDis * ct * cp,
                  self.lookAtPt[1] + self.cameraDis * sp,
                  self.lookAtPt[2] + self.cameraDis * st * cp]
        return result

    def OnResize(self, event):
        contextAttrib = glcanvas.GLContextAttrs()
        contextAttrib.PlatformDefaults().CoreProfile().MajorVersion(3).MinorVersion(3).EndList()
        self.context = glcanvas.GLContext(self, ctxAttrs=contextAttrib)
        self.size = self.GetClientSize()
        self.size[1] = max(1, self.size[1])  # avoid divided by 0
        self.SetCurrent(self.context)

        self.init = False
        self.Refresh(eraseBackground=True)
        self.Update()

    def OnPaint(self, event=None):
        """
        This will be called at every frame
        """
        self.SetCurrent(self.context)
        if not self.init:
            # Init the OpenGL environment if not initialized
            self.InitGL()
            self.init = True
        # the draw method
        self.OnDraw()

    def OnDraw(self):
        gl.glClearColor(*self.backgroundColor, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # These are per-frame updates to the shader. Update the viewing matrix
        self.viewMat = self.glutility.view(self.getCameraPos(), self.lookAtPt, self.upVector)
        self.shaderProg.setMat4("viewMat", self.viewMat)

        self.topLevelComponent.update(np.identity(4))
        self.topLevelComponent.draw(self.shaderProg)

        self.SwapBuffers()

    def OnDestroy(self, event):
        """
        Window destroy event binding

        :param event: Window destroy event
        :return: None
        """
        if self.shaderProg is not None:
            del self.shaderProg
        super(Sketch, self).OnDestroy(event)

    def Interrupt_MouseMoving(self, x, y):
        ##### TODO 6 (CS680 Required, CS480 Extra Credit): Eye movement
        # Make your creature's eyes follow the cursor.
        # The eye rotation only needs to work correctly when the creature is looking toward the viewer.
        # You do not need to account for other camera orientations.
        # Try to implement this using quaternions for additional credit!
        return

    def Interrupt_Scroll(self, wheelRotation):
        """
        When mouse wheel rotating detected, do following things

        :param wheelRotation: mouse wheel changes, normally +120 or -120
        :return: None
        """
        if wheelRotation == 0:
            return
        wheelChange = wheelRotation / abs(wheelRotation)  # normalize wheel change

        # rotate components in selected components together
        if len(self.selected_components) > 0:
            for component in self.selected_components:
                component.rotate(wheelChange * self.MOUSE_SCROLL_SPEED, component.axisBucket[self.select_axis_index])

        # rotate current selected component if its not in list
        if len(self.components) > 0 and self.select_obj_index >= 0:
            self.components[self.select_obj_index].rotate(wheelChange * self.MOUSE_SCROLL_SPEED,
                                                            self.components[self.select_obj_index].
                                                            axisBucket[self.select_axis_index])
        self.update()

    def unprojectCanvas(self, x, y, u=0.5):
        """
        unproject a canvas point to world coordiantes. 2D -> 3D
        you need give an extra parameter u, to tell the method how far are you from znear
        u is the proportion of distance to znear / zfar-znear
        in the gluUnProject, the distribution of z is not linear when using perspective projection,
        so z=0.5 is not in the middle,
        that's why we compute out the ray and use linear interpolation and u to get the point

        :param u: u is the proportion to the znear/, in range [0, 1]
        :type u: float
        """
        result1 = self._unproject(x, y, 0.0)
        result2 = self._unproject(x, y, 1.0)
        result = Point([(1 - u) * r1 + u * r2 for r1, r2 in zip(result1, result2)])
        return result

    def _unproject(self, x, y, z):
        model_matrix = np.identity(4)
        proj_matrix = self.viewMat @ self.perspMat
        viewport = gl.glGetIntegerv(gl.GL_VIEWPORT)
        model_view_proj_matrix = proj_matrix @ model_matrix
        inv_model_view_proj_matrix = np.linalg.inv(model_view_proj_matrix)

        x_ndc = (x - viewport[0]) / viewport[2] * 2.0 - 1.0
        y_ndc = (y - viewport[1]) / viewport[3] * 2.0 - 1.0
        z_ndc = 2.0 * z - 1.0
        
        ndc_coords = np.array([x_ndc, y_ndc, z_ndc, 1.0])
        world_coords = inv_model_view_proj_matrix.T @ ndc_coords # transpose because they are row-major
        if world_coords[3] != 0:
            world_coords /= world_coords[3]
        return world_coords[:3]

    def Interrupt_MouseL(self, x, y):
        """
        When mouse click detected, store current position in last_mouse_leftPosition

        :param x: Mouse click's x coordinate
        :type x: int
        :param y: Mouse click's y coordinate
        :type y: int
        :return: None
        """
        self.last_mouse_leftPosition[0] = x
        self.last_mouse_leftPosition[1] = y

    def Interrupt_MouseMiddleDragging(self, x, y):
        """
        When mouse drag motion with middle key detected, interrupt with new mouse position

        :param x: Mouse drag new position's x coordinate
        :type x: int
        :param y: Mouse drag new position's x coordinate
        :type y: int
        :return: None
        """

        if self.new_dragging_event:
            self.last_mouse_middlePosition[0] = x
            self.last_mouse_middlePosition[1] = y
            return
        
        dx = x - self.last_mouse_middlePosition[0]
        dy = y - self.last_mouse_middlePosition[1]

        originalMidPt = self.unprojectCanvas(*self.last_mouse_middlePosition, 0.5)

        self.last_mouse_middlePosition[0] = x
        self.last_mouse_middlePosition[1] = y

        currentMidPt = self.unprojectCanvas(x, y, 0.5)
        changes = currentMidPt - originalMidPt
        moveSpeed = 0.185 * self.cameraDis / 6
        self.lookAtPt = [self.lookAtPt[0] - changes[0] * moveSpeed,
                         self.lookAtPt[1] - changes[1] * moveSpeed,
                         self.lookAtPt[2] - changes[2] * moveSpeed]

    def Interrupt_MouseLeftDragging(self, x, y):
        """
        When mouse drag motion detected, interrupt with new mouse position

        :param x: Mouse drag new position's x coordinate
        :type x: int
        :param y: Mouse drag new position's x coordinate
        :type y: int
        :return: None
        """

        if self.new_dragging_event:
            self.last_mouse_leftPosition[0] = x
            self.last_mouse_leftPosition[1] = y
            return

        # Change viewing angle when dragging happened
        dx = x - self.last_mouse_leftPosition[0]
        dy = y - self.last_mouse_leftPosition[1]

        # restrict phi movement range, stop cameraphi changes at pole points
        self.cameraPhi = min(math.pi / 2, max(-math.pi / 2, self.cameraPhi - dy / 50))
        self.cameraTheta += dx / 100 * (self.MOUSE_ROTATE_SPEED)

        self.cameraTheta = self.cameraTheta % (2 * math.pi)

        self.last_mouse_leftPosition[0] = x
        self.last_mouse_leftPosition[1] = y

    def update(self):
        """
        Update current canvas
        :return: None
        """
        self.topLevelComponent.update(np.identity(4))

    def Interrupt_Keyboard(self, keycode):
        """
        Keyboard interrupt bindings

        :param keycode: wxpython keyboard event's keycode
        :return: None
        """

        ##### TODO 5: Set up your poses and finish the user interface
        # Define keyboard events to make your creature act in different ways when keys are pressed.
        # Create five unique poses to demonstrate your creature's joint rotations.
        # HINT: selecting individual components is easier if you create a dictionary of components (self.cDict)
        # that can be indexed by name (e.g. self.cDict["leg1"] instead of self.components[10])
            
        if keycode in [wx.WXK_RETURN]:
            # enter component editing mode
            # sets current axis to whatever axis we are currently on, not 0 always
            self.select_axis_index = self.select_axis_index % 3

            if len(self.components) > 0:
                # reset color of last selected component if it is not in selected_components
                if self.components[self.select_obj_index] not in self.selected_components:
                    self.components[self.select_obj_index].reset("color")

                # set new selected component & its color
                self.select_obj_index = (self.select_obj_index + 1) % len(self.components)
                self.components[self.select_obj_index].setCurrentColor(self.select_color[self.select_axis_index])
                
            self.update()
        
        # press tab to add selected component to list of components
        if keycode in [wx.WXK_TAB]:
            if self.select_obj_index >= 0:
                selected = self.components[self.select_obj_index]

                # remove component from list if already there
                if selected in self.selected_components:
                    self.selected_components.remove(selected)
                    selected.reset("color")

                # add component to list
                else:
                    self.selected_components.append(selected)
                    selected.setCurrentColor(self.select_color[self.select_axis_index])

            self.update()

        if keycode in [wx.WXK_LEFT]: 
            # Last rotation axis of this component
            self.select_axis_index = (self.select_axis_index - 1) % 3
            
            # update color of every component selected
            for component in self.selected_components:
                component.selfCurrentColor(self.select_color[self.select_axis_index])
            
            # change color of current selected
            if self.select_obj_index >= 0:
                self.components[self.select_obj_index].setCurrentColor(self.select_color[self.select_axis_index])

            self.update()
        if keycode in [wx.WXK_RIGHT]:
            # Next rotation axis of this component
            self.select_axis_index = (self.select_axis_index + 1) % 3

            # update color of every component selected
            for component in self.selected_components:
                component.setCurrentColor(self.select_color[self.select_axis_index])

            # change color of current selected
            if self.select_obj_index >= 0:
                self.components[self.select_obj_index].setCurrentColor(self.select_color[self.select_axis_index])
            self.update()
        if keycode in [wx.WXK_UP]:
            # Increase rotation angle
            self.Interrupt_Scroll(1)
            self.update()
        if keycode in [wx.WXK_DOWN]:
            # Decrease rotation angle
            self.Interrupt_Scroll(-1)
            self.update()
        if keycode in [wx.WXK_ESCAPE]:
            # exit component editing mode

            # clear selected components
            for component in self.selected_components:
                component.reset("color")
            self.selected_components.clear()

            self.components[self.select_obj_index].reset("color")
            self.select_obj_index = -1
            self.select_axis_index = -1
            self.update()
        if chr(keycode) in "r":
            # reset viewing angle only
            self.resetView()
        if chr(keycode) in "R":
            # reset everything
            for c in self.components:
                c.reset()
            self.resetView()
            self.select_obj_index = -1
            self.select_axis_index = -1
            self.update()

        # pose 1
        if chr(keycode) in "1":
            self.cDict["body"].setCurrentAngle(38, self.cDict["body"].uAxis)
            self.cDict["body"].setCurrentAngle(49, self.cDict["body"].vAxis)
            self.cDict["body"].setCurrentAngle(0, self.cDict["body"].wAxis)
            self.cDict["head"].setCurrentAngle(4, self.cDict["head"].uAxis)
            self.cDict["head"].setCurrentAngle(-10, self.cDict["head"].vAxis)
            self.cDict["head"].setCurrentAngle(-22, self.cDict["head"].wAxis)
            self.cDict["nose1"].setCurrentAngle(-22, self.cDict["nose1"].uAxis)
            self.cDict["nose1"].setCurrentAngle(26, self.cDict["nose1"].vAxis)
            self.cDict["nose1"].setCurrentAngle(-28, self.cDict["nose1"].wAxis)
            self.cDict["nose2"].setCurrentAngle(-1, self.cDict["nose2"].uAxis)
            self.cDict["nose2"].setCurrentAngle(-9, self.cDict["nose2"].vAxis)
            self.cDict["nose2"].setCurrentAngle(-24, self.cDict["nose2"].wAxis)
            self.cDict["leftAnt1"].setCurrentAngle(-40, self.cDict["leftAnt1"].uAxis)
            self.cDict["leftAnt1"].setCurrentAngle(18, self.cDict["leftAnt1"].vAxis)
            self.cDict["leftAnt1"].setCurrentAngle(13, self.cDict["leftAnt1"].wAxis)
            self.cDict["leftAnt2"].setCurrentAngle(-64, self.cDict["leftAnt2"].uAxis)
            self.cDict["leftAnt2"].setCurrentAngle(-38, self.cDict["leftAnt2"].vAxis)
            self.cDict["leftAnt2"].setCurrentAngle(-63, self.cDict["leftAnt2"].wAxis)
            self.cDict["rightAnt1"].setCurrentAngle(-135, self.cDict["rightAnt1"].uAxis)
            self.cDict["rightAnt1"].setCurrentAngle(64, self.cDict["rightAnt1"].vAxis)
            self.cDict["rightAnt1"].setCurrentAngle(-16, self.cDict["rightAnt1"].wAxis)
            self.cDict["rightAnt2"].setCurrentAngle(-63, self.cDict["rightAnt2"].uAxis)
            self.cDict["rightAnt2"].setCurrentAngle(63, self.cDict["rightAnt2"].vAxis)
            self.cDict["rightAnt2"].setCurrentAngle(50, self.cDict["rightAnt2"].wAxis)
            self.cDict["leftLeg1"].setCurrentAngle(120, self.cDict["leftLeg1"].uAxis)
            self.cDict["leftLeg1"].setCurrentAngle(-34, self.cDict["leftLeg1"].vAxis)
            self.cDict["leftLeg1"].setCurrentAngle(-23, self.cDict["leftLeg1"].wAxis)
            self.cDict["leftLeg2"].setCurrentAngle(45, self.cDict["leftLeg2"].uAxis)
            self.cDict["leftLeg2"].setCurrentAngle(-13, self.cDict["leftLeg2"].vAxis)
            self.cDict["leftLeg2"].setCurrentAngle(0, self.cDict["leftLeg2"].wAxis)
            self.cDict["rightLeg1"].setCurrentAngle(48, self.cDict["rightLeg1"].uAxis)
            self.cDict["rightLeg1"].setCurrentAngle(-20, self.cDict["rightLeg1"].vAxis)
            self.cDict["rightLeg1"].setCurrentAngle(74, self.cDict["rightLeg1"].wAxis)
            self.cDict["rightLeg2"].setCurrentAngle(-14, self.cDict["rightLeg2"].uAxis)
            self.cDict["rightLeg2"].setCurrentAngle(9, self.cDict["rightLeg2"].vAxis)
            self.cDict["rightLeg2"].setCurrentAngle(0, self.cDict["rightLeg2"].wAxis)
            self.cDict["tail1"].setCurrentAngle(-55, self.cDict["tail1"].uAxis)
            self.cDict["tail1"].setCurrentAngle(120, self.cDict["tail1"].vAxis)
            self.cDict["tail1"].setCurrentAngle(50, self.cDict["tail1"].wAxis)
            self.cDict["tail2"].setCurrentAngle(35, self.cDict["tail2"].uAxis)
            self.cDict["tail2"].setCurrentAngle(45, self.cDict["tail2"].vAxis)
            self.cDict["tail2"].setCurrentAngle(-20, self.cDict["tail2"].wAxis)
            self.cDict["tail3"].setCurrentAngle(-40, self.cDict["tail3"].uAxis)
            self.cDict["tail3"].setCurrentAngle(50, self.cDict["tail3"].vAxis)
            self.cDict["tail3"].setCurrentAngle(-15, self.cDict["tail3"].wAxis)
            self.cDict["tailEnd"].setCurrentAngle(0, self.cDict["tailEnd"].uAxis)
            self.cDict["tailEnd"].setCurrentAngle(0, self.cDict["tailEnd"].vAxis)
            self.cDict["tailEnd"].setCurrentAngle(0, self.cDict["tailEnd"].wAxis)

        if chr(keycode) in "2":
            self.cDict["body"].setCurrentAngle(0, self.cDict["body"].uAxis)
            self.cDict["body"].setCurrentAngle(0, self.cDict["body"].vAxis)
            self.cDict["body"].setCurrentAngle(0, self.cDict["body"].wAxis)
            self.cDict["head"].setCurrentAngle(-17, self.cDict["head"].uAxis)
            self.cDict["head"].setCurrentAngle(33, self.cDict["head"].vAxis)
            self.cDict["head"].setCurrentAngle(-45, self.cDict["head"].wAxis)
            self.cDict["nose1"].setCurrentAngle(13, self.cDict["nose1"].uAxis)
            self.cDict["nose1"].setCurrentAngle(21, self.cDict["nose1"].vAxis)
            self.cDict["nose1"].setCurrentAngle(-4, self.cDict["nose1"].wAxis)
            self.cDict["nose2"].setCurrentAngle(22, self.cDict["nose2"].uAxis)
            self.cDict["nose2"].setCurrentAngle(8, self.cDict["nose2"].vAxis)
            self.cDict["nose2"].setCurrentAngle(39, self.cDict["nose2"].wAxis)
            self.cDict["leftAnt1"].setCurrentAngle(-65, self.cDict["leftAnt1"].uAxis)
            self.cDict["leftAnt1"].setCurrentAngle(-4, self.cDict["leftAnt1"].vAxis)
            self.cDict["leftAnt1"].setCurrentAngle(33, self.cDict["leftAnt1"].wAxis)
            self.cDict["leftAnt2"].setCurrentAngle(-67, self.cDict["leftAnt2"].uAxis)
            self.cDict["leftAnt2"].setCurrentAngle(13, self.cDict["leftAnt2"].vAxis)
            self.cDict["leftAnt2"].setCurrentAngle(-42, self.cDict["leftAnt2"].wAxis)
            self.cDict["rightAnt1"].setCurrentAngle(-118, self.cDict["rightAnt1"].uAxis)
            self.cDict["rightAnt1"].setCurrentAngle(56, self.cDict["rightAnt1"].vAxis)
            self.cDict["rightAnt1"].setCurrentAngle(-37, self.cDict["rightAnt1"].wAxis)
            self.cDict["rightAnt2"].setCurrentAngle(-37, self.cDict["rightAnt2"].uAxis)
            self.cDict["rightAnt2"].setCurrentAngle(-81, self.cDict["rightAnt2"].vAxis)
            self.cDict["rightAnt2"].setCurrentAngle(-38, self.cDict["rightAnt2"].wAxis)
            self.cDict["leftLeg1"].setCurrentAngle(92, self.cDict["leftLeg1"].uAxis)
            self.cDict["leftLeg1"].setCurrentAngle(-23, self.cDict["leftLeg1"].vAxis)
            self.cDict["leftLeg1"].setCurrentAngle(-67, self.cDict["leftLeg1"].wAxis)
            self.cDict["leftLeg2"].setCurrentAngle(-67, self.cDict["leftLeg2"].uAxis)
            self.cDict["leftLeg2"].setCurrentAngle(8, self.cDict["leftLeg2"].vAxis)
            self.cDict["leftLeg2"].setCurrentAngle(0, self.cDict["leftLeg2"].wAxis)
            self.cDict["rightLeg1"].setCurrentAngle(60, self.cDict["rightLeg1"].uAxis)
            self.cDict["rightLeg1"].setCurrentAngle(-7, self.cDict["rightLeg1"].vAxis)
            self.cDict["rightLeg1"].setCurrentAngle(48, self.cDict["rightLeg1"].wAxis)
            self.cDict["rightLeg2"].setCurrentAngle(19, self.cDict["rightLeg2"].uAxis)
            self.cDict["rightLeg2"].setCurrentAngle(20, self.cDict["rightLeg2"].vAxis)
            self.cDict["rightLeg2"].setCurrentAngle(0, self.cDict["rightLeg2"].wAxis)
            self.cDict["tail1"].setCurrentAngle(28, self.cDict["tail1"].uAxis)
            self.cDict["tail1"].setCurrentAngle(190, self.cDict["tail1"].vAxis)
            self.cDict["tail1"].setCurrentAngle(-40, self.cDict["tail1"].wAxis)
            self.cDict["tail2"].setCurrentAngle(68, self.cDict["tail2"].uAxis)
            self.cDict["tail2"].setCurrentAngle(50, self.cDict["tail2"].vAxis)
            self.cDict["tail2"].setCurrentAngle(22, self.cDict["tail2"].wAxis)
            self.cDict["tail3"].setCurrentAngle(-28, self.cDict["tail3"].uAxis)
            self.cDict["tail3"].setCurrentAngle(-51, self.cDict["tail3"].vAxis)
            self.cDict["tail3"].setCurrentAngle(7, self.cDict["tail3"].wAxis)
            self.cDict["tailEnd"].setCurrentAngle(0, self.cDict["tailEnd"].uAxis)
            self.cDict["tailEnd"].setCurrentAngle(0, self.cDict["tailEnd"].vAxis)
            self.cDict["tailEnd"].setCurrentAngle(0, self.cDict["tailEnd"].wAxis)

        if chr(keycode) in "3":
            self.cDict["body"].setCurrentAngle(-14, self.cDict["body"].uAxis)
            self.cDict["body"].setCurrentAngle(-10, self.cDict["body"].vAxis)
            self.cDict["body"].setCurrentAngle(0, self.cDict["body"].wAxis)
            self.cDict["head"].setCurrentAngle(10, self.cDict["head"].uAxis)
            self.cDict["head"].setCurrentAngle(-27, self.cDict["head"].vAxis)
            self.cDict["head"].setCurrentAngle(30, self.cDict["head"].wAxis)
            self.cDict["nose1"].setCurrentAngle(12, self.cDict["nose1"].uAxis)
            self.cDict["nose1"].setCurrentAngle(10, self.cDict["nose1"].vAxis)
            self.cDict["nose1"].setCurrentAngle(-29, self.cDict["nose1"].wAxis)
            self.cDict["nose2"].setCurrentAngle(35, self.cDict["nose2"].uAxis)
            self.cDict["nose2"].setCurrentAngle(-44, self.cDict["nose2"].vAxis)
            self.cDict["nose2"].setCurrentAngle(23, self.cDict["nose2"].wAxis)
            self.cDict["leftAnt1"].setCurrentAngle(-111, self.cDict["leftAnt1"].uAxis)
            self.cDict["leftAnt1"].setCurrentAngle(-23, self.cDict["leftAnt1"].vAxis)
            self.cDict["leftAnt1"].setCurrentAngle(84, self.cDict["leftAnt1"].wAxis)
            self.cDict["leftAnt2"].setCurrentAngle(49, self.cDict["leftAnt2"].uAxis)
            self.cDict["leftAnt2"].setCurrentAngle(-71, self.cDict["leftAnt2"].vAxis)
            self.cDict["leftAnt2"].setCurrentAngle(-20, self.cDict["leftAnt2"].wAxis)
            self.cDict["rightAnt1"].setCurrentAngle(-130, self.cDict["rightAnt1"].uAxis)
            self.cDict["rightAnt1"].setCurrentAngle(75, self.cDict["rightAnt1"].vAxis)
            self.cDict["rightAnt1"].setCurrentAngle(-36, self.cDict["rightAnt1"].wAxis)
            self.cDict["rightAnt2"].setCurrentAngle(-80, self.cDict["rightAnt2"].uAxis)
            self.cDict["rightAnt2"].setCurrentAngle(62, self.cDict["rightAnt2"].vAxis)
            self.cDict["rightAnt2"].setCurrentAngle(-11, self.cDict["rightAnt2"].wAxis)
            self.cDict["leftLeg1"].setCurrentAngle(90, self.cDict["leftLeg1"].uAxis)
            self.cDict["leftLeg1"].setCurrentAngle(10, self.cDict["leftLeg1"].vAxis)
            self.cDict["leftLeg1"].setCurrentAngle(-41, self.cDict["leftLeg1"].wAxis)
            self.cDict["leftLeg2"].setCurrentAngle(80, self.cDict["leftLeg2"].uAxis)
            self.cDict["leftLeg2"].setCurrentAngle(20, self.cDict["leftLeg2"].vAxis)
            self.cDict["leftLeg2"].setCurrentAngle(0, self.cDict["leftLeg2"].wAxis)
            self.cDict["rightLeg1"].setCurrentAngle(140, self.cDict["rightLeg1"].uAxis)
            self.cDict["rightLeg1"].setCurrentAngle(-5, self.cDict["rightLeg1"].vAxis)
            self.cDict["rightLeg1"].setCurrentAngle(25, self.cDict["rightLeg1"].wAxis)
            self.cDict["rightLeg2"].setCurrentAngle(-35, self.cDict["rightLeg2"].uAxis)
            self.cDict["rightLeg2"].setCurrentAngle(-10, self.cDict["rightLeg2"].vAxis)
            self.cDict["rightLeg2"].setCurrentAngle(0, self.cDict["rightLeg2"].wAxis)
            self.cDict["tail1"].setCurrentAngle(65, self.cDict["tail1"].uAxis)
            self.cDict["tail1"].setCurrentAngle(140, self.cDict["tail1"].vAxis)
            self.cDict["tail1"].setCurrentAngle(-68, self.cDict["tail1"].wAxis)
            self.cDict["tail2"].setCurrentAngle(20, self.cDict["tail2"].uAxis)
            self.cDict["tail2"].setCurrentAngle(-30, self.cDict["tail2"].vAxis)
            self.cDict["tail2"].setCurrentAngle(40, self.cDict["tail2"].wAxis)
            self.cDict["tail3"].setCurrentAngle(70, self.cDict["tail3"].uAxis)
            self.cDict["tail3"].setCurrentAngle(-30, self.cDict["tail3"].vAxis)
            self.cDict["tail3"].setCurrentAngle(-50, self.cDict["tail3"].wAxis)
            self.cDict["tailEnd"].setCurrentAngle(0, self.cDict["tailEnd"].uAxis)
            self.cDict["tailEnd"].setCurrentAngle(0, self.cDict["tailEnd"].vAxis)
            self.cDict["tailEnd"].setCurrentAngle(0, self.cDict["tailEnd"].wAxis)


        if chr(keycode) in "4":
            self.cDict["body"].setCurrentAngle(20, self.cDict["body"].uAxis)
            self.cDict["body"].setCurrentAngle(-15, self.cDict["body"].vAxis)
            self.cDict["body"].setCurrentAngle(0, self.cDict["body"].wAxis)
            self.cDict["head"].setCurrentAngle(-30, self.cDict["head"].uAxis)
            self.cDict["head"].setCurrentAngle(45, self.cDict["head"].vAxis)
            self.cDict["head"].setCurrentAngle(19, self.cDict["head"].wAxis)
            self.cDict["nose1"].setCurrentAngle(-15, self.cDict["nose1"].uAxis)
            self.cDict["nose1"].setCurrentAngle(-5, self.cDict["nose1"].vAxis)
            self.cDict["nose1"].setCurrentAngle(-19, self.cDict["nose1"].wAxis)
            self.cDict["nose2"].setCurrentAngle(20, self.cDict["nose2"].uAxis)
            self.cDict["nose2"].setCurrentAngle(-38, self.cDict["nose2"].vAxis)
            self.cDict["nose2"].setCurrentAngle(-27, self.cDict["nose2"].wAxis)
            self.cDict["leftAnt1"].setCurrentAngle(-50, self.cDict["leftAnt1"].uAxis)
            self.cDict["leftAnt1"].setCurrentAngle(90, self.cDict["leftAnt1"].vAxis)
            self.cDict["leftAnt1"].setCurrentAngle(24, self.cDict["leftAnt1"].wAxis)
            self.cDict["leftAnt2"].setCurrentAngle(36, self.cDict["leftAnt2"].uAxis)
            self.cDict["leftAnt2"].setCurrentAngle(-72, self.cDict["leftAnt2"].vAxis)
            self.cDict["leftAnt2"].setCurrentAngle(-44, self.cDict["leftAnt2"].wAxis)
            self.cDict["rightAnt1"].setCurrentAngle(-30, self.cDict["rightAnt1"].uAxis)
            self.cDict["rightAnt1"].setCurrentAngle(88, self.cDict["rightAnt1"].vAxis)
            self.cDict["rightAnt1"].setCurrentAngle(-45, self.cDict["rightAnt1"].wAxis)
            self.cDict["rightAnt2"].setCurrentAngle(-88, self.cDict["rightAnt2"].uAxis)
            self.cDict["rightAnt2"].setCurrentAngle(45, self.cDict["rightAnt2"].vAxis)
            self.cDict["rightAnt2"].setCurrentAngle(25, self.cDict["rightAnt2"].wAxis)
            self.cDict["leftLeg1"].setCurrentAngle(110, self.cDict["leftLeg1"].uAxis)
            self.cDict["leftLeg1"].setCurrentAngle(30, self.cDict["leftLeg1"].vAxis)
            self.cDict["leftLeg1"].setCurrentAngle(-80, self.cDict["leftLeg1"].wAxis)
            self.cDict["leftLeg2"].setCurrentAngle(45, self.cDict["leftLeg2"].uAxis)
            self.cDict["leftLeg2"].setCurrentAngle(5, self.cDict["leftLeg2"].vAxis)
            self.cDict["leftLeg2"].setCurrentAngle(0, self.cDict["leftLeg2"].wAxis)
            self.cDict["rightLeg1"].setCurrentAngle(140, self.cDict["rightLeg1"].uAxis)
            self.cDict["rightLeg1"].setCurrentAngle(35, self.cDict["rightLeg1"].vAxis)
            self.cDict["rightLeg1"].setCurrentAngle(-15, self.cDict["rightLeg1"].wAxis)
            self.cDict["rightLeg2"].setCurrentAngle(-45, self.cDict["rightLeg2"].uAxis)
            self.cDict["rightLeg2"].setCurrentAngle(-20, self.cDict["rightLeg2"].vAxis)
            self.cDict["rightLeg2"].setCurrentAngle(0, self.cDict["rightLeg2"].wAxis)
            self.cDict["tail1"].setCurrentAngle(-10, self.cDict["tail1"].uAxis)
            self.cDict["tail1"].setCurrentAngle(240, self.cDict["tail1"].vAxis)
            self.cDict["tail1"].setCurrentAngle(-25, self.cDict["tail1"].wAxis)
            self.cDict["tail2"].setCurrentAngle(-55, self.cDict["tail2"].uAxis)
            self.cDict["tail2"].setCurrentAngle(35, self.cDict["tail2"].vAxis)
            self.cDict["tail2"].setCurrentAngle(30, self.cDict["tail2"].wAxis)
            self.cDict["tail3"].setCurrentAngle(60, self.cDict["tail3"].uAxis)
            self.cDict["tail3"].setCurrentAngle(-70, self.cDict["tail3"].vAxis)
            self.cDict["tail3"].setCurrentAngle(10, self.cDict["tail3"].wAxis)
            self.cDict["tailEnd"].setCurrentAngle(0, self.cDict["tailEnd"].uAxis)
            self.cDict["tailEnd"].setCurrentAngle(0, self.cDict["tailEnd"].vAxis)
            self.cDict["tailEnd"].setCurrentAngle(0, self.cDict["tailEnd"].wAxis)


        if chr(keycode) in "5":
            self.cDict["body"].setCurrentAngle(20, self.cDict["body"].uAxis)
            self.cDict["body"].setCurrentAngle(0, self.cDict["body"].vAxis)
            self.cDict["body"].setCurrentAngle(0, self.cDict["body"].wAxis)
            self.cDict["head"].setCurrentAngle(35, self.cDict["head"].uAxis)
            self.cDict["head"].setCurrentAngle(-15, self.cDict["head"].vAxis)
            self.cDict["head"].setCurrentAngle(40, self.cDict["head"].wAxis)
            self.cDict["nose1"].setCurrentAngle(10, self.cDict["nose1"].uAxis)
            self.cDict["nose1"].setCurrentAngle(-20, self.cDict["nose1"].vAxis)
            self.cDict["nose1"].setCurrentAngle(15, self.cDict["nose1"].wAxis)
            self.cDict["nose2"].setCurrentAngle(30, self.cDict["nose2"].uAxis)
            self.cDict["nose2"].setCurrentAngle(-25, self.cDict["nose2"].vAxis)
            self.cDict["nose2"].setCurrentAngle(-5, self.cDict["nose2"].wAxis)
            self.cDict["leftAnt1"].setCurrentAngle(-45, self.cDict["leftAnt1"].uAxis)
            self.cDict["leftAnt1"].setCurrentAngle(75, self.cDict["leftAnt1"].vAxis)
            self.cDict["leftAnt1"].setCurrentAngle(55, self.cDict["leftAnt1"].wAxis)
            self.cDict["leftAnt2"].setCurrentAngle(-70, self.cDict["leftAnt2"].uAxis)
            self.cDict["leftAnt2"].setCurrentAngle(-30, self.cDict["leftAnt2"].vAxis)
            self.cDict["leftAnt2"].setCurrentAngle(10, self.cDict["leftAnt2"].wAxis)
            self.cDict["rightAnt1"].setCurrentAngle(-35, self.cDict["rightAnt1"].uAxis)
            self.cDict["rightAnt1"].setCurrentAngle(85, self.cDict["rightAnt1"].vAxis)
            self.cDict["rightAnt1"].setCurrentAngle(-45, self.cDict["rightAnt1"].wAxis)
            self.cDict["rightAnt2"].setCurrentAngle(-60, self.cDict["rightAnt2"].uAxis)
            self.cDict["rightAnt2"].setCurrentAngle(75, self.cDict["rightAnt2"].vAxis)
            self.cDict["rightAnt2"].setCurrentAngle(-20, self.cDict["rightAnt2"].wAxis)
            self.cDict["leftLeg1"].setCurrentAngle(130, self.cDict["leftLeg1"].uAxis)
            self.cDict["leftLeg1"].setCurrentAngle(-10, self.cDict["leftLeg1"].vAxis)
            self.cDict["leftLeg1"].setCurrentAngle(-30, self.cDict["leftLeg1"].wAxis)
            self.cDict["leftLeg2"].setCurrentAngle(60, self.cDict["leftLeg2"].uAxis)
            self.cDict["leftLeg2"].setCurrentAngle(20, self.cDict["leftLeg2"].vAxis)
            self.cDict["leftLeg2"].setCurrentAngle(0, self.cDict["leftLeg2"].wAxis)
            self.cDict["rightLeg1"].setCurrentAngle(100, self.cDict["rightLeg1"].uAxis)
            self.cDict["rightLeg1"].setCurrentAngle(5, self.cDict["rightLeg1"].vAxis)
            self.cDict["rightLeg1"].setCurrentAngle(25, self.cDict["rightLeg1"].wAxis)
            self.cDict["rightLeg2"].setCurrentAngle(-20, self.cDict["rightLeg2"].uAxis)
            self.cDict["rightLeg2"].setCurrentAngle(30, self.cDict["rightLeg2"].vAxis)
            self.cDict["rightLeg2"].setCurrentAngle(0, self.cDict["rightLeg2"].wAxis)
            self.cDict["tail1"].setCurrentAngle(40, self.cDict["tail1"].uAxis)
            self.cDict["tail1"].setCurrentAngle(200, self.cDict["tail1"].vAxis)
            self.cDict["tail1"].setCurrentAngle(5, self.cDict["tail1"].wAxis)
            self.cDict["tail2"].setCurrentAngle(-50, self.cDict["tail2"].uAxis)
            self.cDict["tail2"].setCurrentAngle(45, self.cDict["tail2"].vAxis)
            self.cDict["tail2"].setCurrentAngle(-15, self.cDict["tail2"].wAxis)
            self.cDict["tail3"].setCurrentAngle(50, self.cDict["tail3"].uAxis)
            self.cDict["tail3"].setCurrentAngle(-40, self.cDict["tail3"].vAxis)
            self.cDict["tail3"].setCurrentAngle(35, self.cDict["tail3"].wAxis)
            self.cDict["tailEnd"].setCurrentAngle(0, self.cDict["tailEnd"].uAxis)
            self.cDict["tailEnd"].setCurrentAngle(0, self.cDict["tailEnd"].vAxis)
            self.cDict["tailEnd"].setCurrentAngle(0, self.cDict["tailEnd"].wAxis)






if __name__ == "__main__":
    print("This is the main entry! ")
    app = wx.App(False)
    # Set FULL_REPAINT_ON_RESIZE will repaint everything when scaling the frame, here is the style setting for it: wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE
    # Resize disabled in this one
    frame = wx.Frame(None, size=(500, 500), title="Test",
                     style=wx.DEFAULT_FRAME_STYLE | wx.FULL_REPAINT_ON_RESIZE)  # Disable Resize: ^ wx.RESIZE_BORDER
    canvas = Sketch(frame)

    frame.Show()
    app.MainLoop()
