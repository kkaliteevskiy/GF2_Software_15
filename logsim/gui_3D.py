"""Implement the graphical user interface for the Logic Simulator.

Used in the Logic Simulator project to enable the user to run the simulation
or adjust the network properties.

Classes:
--------
MyGLCanvas - handles all canvas drawing operations.
Gui - configures the main window and all the widgets.
"""
import wx
import wx.glcanvas as wxcanvas
import numpy as np
import math
from OpenGL import GL, GLU, GLUT

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
import argparse



class MyGLCanvas(wxcanvas.GLCanvas):
    """Handle all drawing operations.

    This class contains functions for drawing onto the canvas. It
    also contains handlers for events relating to the canvas.

    Parameters
    ----------
    parent: parent window.
    devices: instance of the devices.Devices() class.
    monitors: instance of the monitors.Monitors() class.

    Public methods
    --------------
    init_gl(self): Configures the OpenGL context.

    render(self): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos, z_pos): Handles text drawing
                                                  operations.
    """

    def __init__(self, parent, devices, monitors, id, pos, size):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Constants for OpenGL materials and lights
        self.mat_diffuse = [0.0, 0.0, 0.0, 1.0]
        self.mat_no_specular = [0.0, 0.0, 0.0, 0.0]
        self.mat_no_shininess = [0.0]
        self.mat_specular = [0.5, 0.5, 0.5, 1.0]
        self.mat_shininess = [50.0]
        self.top_right = [1.0, 1.0, 1.0, 0.0]
        self.straight_on = [0.0, 0.0, 1.0, 0.0]
        self.no_ambient = [0.0, 0.0, 0.0, 1.0]
        self.dim_diffuse = [0.5, 0.5, 0.5, 1.0]
        self.bright_diffuse = [1.0, 1.0, 1.0, 1.0]
        self.med_diffuse = [0.75, 0.75, 0.75, 1.0]
        self.full_specular = [0.5, 0.5, 0.5, 1.0]
        self.no_specular = [0.0, 0.0, 0.0, 1.0]

        # Initialise variables for panning
        self.pan_x = -300
        self.pan_y = -300
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise the scene rotation matrix
        self.scene_rotate = np.identity(4, 'f')

        # Initialise variables for zooming
        self.zoom = 1

        # Offset between viewpoint and origin of the scene
        self.depth_offset = 1000

        # Bind events to the canvas
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)

        # Parameters
        self.devices = devices
        self.monitors = monitors

    def init_gl(self):
        """Configure and initialise the OpenGL context."""
        size = self.GetClientSize()
        self.SetCurrent(self.context)

        GL.glViewport(0, 0, size.width, size.height)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(45, size.width / size.height, 10, 10000)

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()  # lights positioned relative to the viewer
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, self.no_ambient)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_DIFFUSE, self.med_diffuse)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_SPECULAR, self.no_specular)
        GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, self.top_right)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_AMBIENT, self.no_ambient)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_DIFFUSE, self.dim_diffuse)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_SPECULAR, self.no_specular)
        GL.glLightfv(GL.GL_LIGHT1, GL.GL_POSITION, [-1.0, 1.0, 0.0, 0.0])

        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SPECULAR, self.mat_specular)
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_SHININESS, self.mat_shininess)
        GL.glMaterialfv(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE,
                        self.mat_diffuse)
        GL.glColorMaterial(GL.GL_FRONT, GL.GL_AMBIENT_AND_DIFFUSE)

        GL.glClearColor(1.0, 1.0, 1.0, 1.0)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glCullFace(GL.GL_BACK)
        GL.glEnable(GL.GL_COLOR_MATERIAL)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_LIGHT0)
        GL.glEnable(GL.GL_LIGHT1)
        GL.glEnable(GL.GL_NORMALIZE)

        
        # Viewing transformation - set the viewpoint back from the scene
        GL.glTranslatef(0.0, 0.0, -self.depth_offset)

        # Modelling transformation - pan, zoom and rotate
        GL.glTranslatef(self.pan_x, self.pan_y, 0.0)
        GL.glMultMatrixf(self.scene_rotate)
        GL.glScalef(self.zoom, self.zoom, self.zoom)

    def render(self):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the OpenGL rendering context
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        margin = self.monitors.get_margin()
        margin = margin * 10 if margin is not None else 0
        y_pos = 60  # Starting y position for drawing.
        num_signals_list = []

        for device_id, output_id in self.monitors.monitors_dictionary:
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            signal_list = self.monitors.monitors_dictionary[(device_id, output_id)]
            num_signals_list.append(len(signal_list))
            
            # Render the monitor name at the start of the line.
            self.render_text(monitor_name, 0, y_pos, 0)
            x_pos = 40 + margin  # Starting x position for drawing signals.
            prev_y = y_pos
            cycle = 0
            for signal in signal_list:
                GL.glColor3f(173/255, 216/255, 230/255)

                if signal == self.devices.HIGH:
                    h = 20
                    self.draw_cuboid(x_pos, y_pos, 0, 20, 10, h)
                elif signal == self.devices.LOW:
                    h = 2
                    self.draw_cuboid(x_pos, y_pos, 0, 20, 10, h)
                elif signal == self.devices.RISING:
                    h = 20
                    self.draw_cuboid(x_pos, y_pos, 0, 20, 10, h)
                elif signal == self.devices.FALLING:
                    h = 2
                    self.draw_cuboid(x_pos, y_pos, 0, 20, 10, h)
                elif signal == self.devices.BLANK:
                    h = 0 

                #self.draw_cuboid(x_pos, y, 10, 10, 10)
                self.render_text("|", x_pos-20, -15, 0)
                self.render_text(str(cycle), x_pos-20, 0, 0)
                cycle += 1
                
                x_pos += 40  # Move to the next position for drawing.
            y_pos += 40  # Move to the next line for drawing.
        try:
            x_axis_length = max(num_signals_list) * 40
        except:
            x_axis_length = 0
        GL.glColor3f(0.0, 0.0, 0.0)  # Set color to black.
        GL.glBegin(GL.GL_LINES)  # Start drawing lines.
        GL.glVertex3f(20 + margin, -15, 0)  # Vertex at the start of the x-axis.
        GL.glVertex3f(20 + margin + x_axis_length, -15, 0)  # Vertex at the end of the x-axis.
        GL.glEnd()  # End drawing lines.

        GL.glFlush()
        self.SwapBuffers()

    def draw_cuboid(self, x_pos, y_pos, z_pos, half_width, half_depth, height):
        """Draw a cuboid.

        Draw a cuboid at the specified position, with the specified
        dimensions.
        """
       
        GL.glBegin(GL.GL_QUADS)
        GL.glNormal3f(0, -1, 0)
        GL.glVertex3f(x_pos - half_width, y_pos, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, y_pos, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, y_pos, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, y_pos, z_pos + half_depth)
        GL.glNormal3f(0, 1, 0)
        GL.glVertex3f(x_pos + half_width, y_pos + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, y_pos + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, y_pos + height, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, y_pos + height, z_pos + half_depth)
        GL.glNormal3f(-1, 0, 0)
        GL.glVertex3f(x_pos - half_width, y_pos + height, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, y_pos, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, y_pos, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, y_pos + height, z_pos + half_depth)
        GL.glNormal3f(1, 0, 0)
        GL.glVertex3f(x_pos + half_width, y_pos, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, y_pos + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, y_pos + height, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, y_pos, z_pos + half_depth)
        GL.glNormal3f(0, 0, -1)
        GL.glVertex3f(x_pos - half_width, y_pos, z_pos - half_depth)
        GL.glVertex3f(x_pos - half_width, y_pos + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, y_pos + height, z_pos - half_depth)
        GL.glVertex3f(x_pos + half_width, y_pos, z_pos - half_depth)
        GL.glNormal3f(0, 0, 1)
        GL.glVertex3f(x_pos - half_width, y_pos + height, z_pos + half_depth)
        GL.glVertex3f(x_pos - half_width, y_pos, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, y_pos, z_pos + half_depth)
        GL.glVertex3f(x_pos + half_width, y_pos + height, z_pos + half_depth)
        GL.glEnd()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the OpenGL rendering context
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render()

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        self.SetCurrent(self.context)

        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()

        if event.Dragging():
            GL.glMatrixMode(GL.GL_MODELVIEW)
            GL.glLoadIdentity()
            x = event.GetX() - self.last_mouse_x
            y = event.GetY() - self.last_mouse_y
            if event.LeftIsDown():
                GL.glRotatef(math.sqrt((x * x) + (y * y)), y, x, 0)
           # if event.MiddleIsDown():
           #     GL.glRotatef((x + y), 0, 0, 1)
            if event.RightIsDown():
                self.pan_x += x
                self.pan_y -= y
            GL.glMultMatrixf(self.scene_rotate)
            GL.glGetFloatv(GL.GL_MODELVIEW_MATRIX, self.scene_rotate)
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False

        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False

        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            self.init = False

        self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos, z_pos):
        """Handle text drawing operations."""
        GL.glDisable(GL.GL_LIGHTING)
        GL.glColor3f(0.0, 0.0, 0.0)
        GL.glRasterPos3f(x_pos, y_pos, z_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_10

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos3f(x_pos, y_pos, z_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))

        GL.glEnable(GL.GL_LIGHTING)

    def reset_view(self):
        """Reset the canvas view to the initial state."""
        self.zoom = 1.0  
        self.pan_x = -300.0  
        self.pan_y = -300.0  
        self.scene_rotate = np.identity(4, 'f')
        self.init = False  
        


class Gui(wx.Frame):
    """Configure the main window and all the widgets.

    This class provides a graphical user interface for the Logic Simulator and
    enables the user to change the circuit properties and run simulations.

    Parameters
    ----------
    title: title of the window.

    Public methods
    --------------
    on_menu(self, event): Event handler for the file menu.

    on_spin(self, event): Event handler for when the user changes the spin
                           control value.

    on_run_button(self, event): Event handler for when the user clicks the run
                                button.

    on_text_box(self, event): Event handler for when the user enters text.
    """
    QuitID=999
    OpenID=998
    def __init__(self, title, path, names, devices, network, monitors, cycles_completed):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Parse command-line arguments.
        parser = argparse.ArgumentParser(description='Open a text file.')
        parser.add_argument('file_path', help='The path to the text file.')
        args = parser.parse_args()

        # Store the path to the text file.
        self.file_path = args.file_path

        # Parameters
        self.path = path
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.cycles_completed = cycles_completed 

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_OPEN, "&Open File")
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors, wx.ID_ANY, wx.DefaultPosition, wx.Size(800, 600))

        # Set font
        font = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Verdana")

        # Configure the widgets
        self.switch_button = wx.Button(self, label="Switch to 2D", size=(300, 25))
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles")
        self.text.SetFont(font)
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        #self.text_box = wx.TextCtrl(self, wx.ID_ANY, "",
                                   # style=wx.TE_PROCESS_ENTER)
        self.continue_button = wx.Button(self, wx.ID_ANY, "Continue")
        self.reset_view_button = wx.Button(self, wx.ID_ANY, "Reset View")

        # Edit switch to 2D button
        self.switch_button.SetBackgroundColour(wx.Colour(173, 216, 230))  # Set the color of the button to light blue

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        #self.text_box.Bind(wx.EVT_TEXT_ENTER, self.on_text_box)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.reset_view_button.Bind(wx.EVT_BUTTON, self.on_reset_view_button)
        self.Bind(wx.EVT_CLOSE, self.on_close_window)
        self.switch_button.Bind(wx.EVT_BUTTON, self.on_switch)

        # Create a scrolled window for the switches and signals
        scroll = wx.ScrolledWindow(self, -1, size=wx.Size(300, 400))
        scroll.SetScrollbars(0, 16, 50, 15)  
        self.scroll_sizer = wx.BoxSizer(wx.VERTICAL)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        side_sizer.Add(self.switch_button, 0, wx.TOP | wx.FIXED_MINSIZE, 5)
        side_sizer.Add(self.text, 1, wx.TOP, 10)
        side_sizer.Add(self.spin, 0, wx.ALL, 5)
        side_sizer.Add(self.run_button, 0, wx.TOP, 5)
        #side_sizer.Add(self.text_box, 1, wx.ALL, 5)
        side_sizer.Add(self.continue_button, 0, wx.TOP, 5)
        side_sizer.Add(self.reset_view_button, 0, wx.TOP, 5)

        # Create a label for switches
        switches_label = wx.StaticText(scroll, label="Switches")
        switches_label.SetFont(font)  
        self.scroll_sizer.Add(switches_label, 0, wx.ALL, 10)

        # Create Sliders for Switches
        self.switch_sliders = []
        switches = self.devices.find_devices(device_kind=self.devices.SWITCH)
        
        for switch in switches:
            switch_name = self.names.get_name_string(switch)
            switch_device = self.devices.get_device(switch)
            label = wx.StaticText(scroll, label=switch_name)
            label.SetFont(font)
            slider = wx.Slider(scroll, value=switch_device.switch_state, minValue=0, maxValue=1, style=wx.SL_HORIZONTAL)
            slider.Bind(wx.EVT_SLIDER, lambda event, index=switch: self.on_slider_change(event, index))
            self.switch_sliders.append(slider)
            
            min_label = wx.StaticText(scroll, label="0")
            max_label = wx.StaticText(scroll, label="1")

            switch_sizer = wx.BoxSizer(wx.HORIZONTAL)
            switch_sizer.Add(label, 1, wx.ALL, 5)
            switch_sizer.Add(min_label, 0, wx.ALIGN_LEFT | wx.ALL, 5)
            switch_sizer.Add(slider, 1, wx.ALL, 5)
            switch_sizer.Add(max_label, 0, wx.EXPAND | wx.ALL, 5)
            
            self.scroll_sizer.Add(switch_sizer, 1, wx.ALL)
        
        # Create checkboxes for signals
        self.monitored_signals, self.not_monitored_signals = self.monitors.get_signal_names()
        outputs_label = wx.StaticText(scroll, label="Outputs (tick to monitor)")
        outputs_label.SetFont(font)
        self.scroll_sizer.Add(outputs_label, 0, wx.ALL, 10)

        self.checkboxes = []  # List to store all checkboxes

        for signal in self.monitored_signals:
            checkbox = wx.CheckBox(scroll, label=signal)
            checkbox.SetValue(True)  # Set checkbox as ticked
            self.Bind(wx.EVT_CHECKBOX, lambda event, cb=checkbox: self.on_checkbox(event, cb), checkbox)
            self.checkboxes.append(checkbox)

        for signal in self.not_monitored_signals:
            checkbox = wx.CheckBox(scroll, label=signal)
            checkbox.SetValue(False)  # Set checkbox as unticked
            self.Bind(wx.EVT_CHECKBOX, lambda event, cb=checkbox: self.on_checkbox(event, cb), checkbox)
            self.checkboxes.append(checkbox)

        # Add checkboxes to sizer
        for checkbox in self.checkboxes:
            self.scroll_sizer.Add(checkbox, 1, wx.ALL, 5)
        
        side_sizer.AddSpacer(10)
        scroll.SetSizer(self.scroll_sizer)
        side_sizer.Add(scroll, 1, wx.EXPAND | wx.RIGHT, 5)
        side_sizer.AddSpacer(10)

        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)
        self.Layout()

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Group 15\n2024",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)
        if event.GetId() == wx.ID_OPEN:
            # Read the file content.
            with open(self.file_path, 'r') as f:
                content = f.read()

            # Create a dialog to display the file content.
            dialog = wx.Dialog(self, title="File Content")
            textctrl = wx.TextCtrl(dialog, value=content, style=wx.TE_MULTILINE | wx.TE_READONLY)
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(textctrl, proportion=1, flag=wx.EXPAND)
            dialog.SetSizer(sizer)
            dialog.ShowModal()

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        self.canvas.render()
    
    def on_reset_view_button(self, event):
        """Handle the event when the user clicks the reset view button."""
        self.canvas.reset_view()
        self.canvas.render()
    
    def on_switch(self, event):
        self.Close()
        from gui import Gui as Gui2D
        gui = Gui2D('2D GUI', self.path, self.names, self.devices, self.network, self.monitors, self.cycles_completed)
        gui.Show(True)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button. Run the simulation from scratch."""
        # Reset the canvas view
        self.canvas.reset_view()
        self.cycles_completed = 0
        cycles = self.spin.GetValue()
        self.network.global_counter = 0
        
        if cycles is not None:  # if the number of cycles provided is valid
            self.monitors.reset_monitors()
            print("".join(["Running for ", str(cycles), " cycles"]))
            self.devices.cold_startup()
            if self.run_simulation(cycles):
                self.cycles_completed += cycles
                
    def on_continue_button(self, event):
        """Continue a previously run simulation."""
        cycles = self.spin.GetValue()
        if cycles is not None:  # if the number of cycles provided is valid
            if self.cycles_completed == 0:
                print("Error! Nothing to continue. Run first.")
            elif self.run_simulation(cycles):
                self.cycles_completed += cycles
                print(" ".join(["Continuing for", str(cycles), "cycles.",
                                "Total:", str(self.cycles_completed)]))
    
    def run_simulation(self, cycles):
        """Run the simulation for a specific number of cycles."""
        for _ in range(cycles):
            if self.network.execute_network():
                self.monitors.record_signals()
            else:
                print("Error! Network oscillating.")
                return False 
        self.canvas.render()
        print("Completed simulation.")
        return True
        
    def on_text_box(self, event):
        """Handle the event when the user enters text."""
        text_box_value = self.text_box.GetValue()
        text = "".join(["New text box value: ", text_box_value])
        self.canvas.render()
    
    def on_checkbox(self, event, checkbox):
        """Handle the event when the user checks or unchecks a checkbox.
        Monitor or zap the output signal accordingly."""
        signal = checkbox.GetLabel()   
        
        if checkbox.IsChecked():
            # Add the signal to the monitored_signals list
            if signal not in self.monitored_signals:
                self.monitored_signals.append(signal)
            
            # Remove the signal from the not_monitored_signals list
            if signal in self.not_monitored_signals:
                self.not_monitored_signals.remove(signal)
            self.monitor_command(signal)
        else:
            # Remove the signal from the monitored_signals list
            if signal in self.monitored_signals:
                self.monitored_signals.remove(signal)
            
            # Add the signal to the not_monitored_signals list
            if signal not in self.not_monitored_signals:
                self.not_monitored_signals.append(signal)
            self.zap_command(signal)

        self.Layout()  # Refresh layout
    
    def monitor_command(self, signal):
        """Set the specified monitor."""
        monitor = self.devices.get_signal_ids(signal)
        if monitor is not None:
            [device, port] = monitor
            monitor_error = self.monitors.make_monitor(device, port,
                                                       self.cycles_completed)
            if monitor_error == self.monitors.NO_ERROR:
                print("Successfully made monitor.")
            else:
                print("Error! Could not make monitor.")

    def zap_command(self, signal):
        """Remove the specified monitor."""
        monitor = self.devices.get_signal_ids(signal)
        if monitor is not None:
            [device, port] = monitor
            if self.monitors.remove_monitor(device, port):
                print("Successfully zapped monitor")
            else:
                print("Error! Could not zap monitor.")
    
    def on_slider_change(self, event, index):
        """Handle the event when the user changes the slider value. Set the switch value accordingly."""
        slider = event.GetEventObject()
        value = slider.GetValue()
        self.devices.set_switch(index, value)
    
    def on_close_window(self, event):
        """Handle the event when the user closes the window."""
        self.Destroy()
    