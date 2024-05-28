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
from OpenGL import GL, GLUT

from names import Names
from devices import Devices
from network import Network
from monitors import Monitors
from scanner import Scanner
from parse import Parser
import collections


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

    render(self, text): Handles all drawing operations.

    on_paint(self, event): Handles the paint event.

    on_size(self, event): Handles the canvas resize event.

    on_mouse(self, event): Handles mouse events.

    render_text(self, text, x_pos, y_pos): Handles text drawing
                                           operations.
    """

    def __init__(self, parent, devices, monitors):
        """Initialise canvas properties and useful variables."""
        super().__init__(parent, -1,
                         attribList=[wxcanvas.WX_GL_RGBA,
                                     wxcanvas.WX_GL_DOUBLEBUFFER,
                                     wxcanvas.WX_GL_DEPTH_SIZE, 16, 0])
        GLUT.glutInit()
        self.init = False
        self.context = wxcanvas.GLContext(self)

        # Initialise variables for panning
        self.pan_x = 0
        self.pan_y = 0
        self.last_mouse_x = 0  # previous mouse x position
        self.last_mouse_y = 0  # previous mouse y position

        # Initialise variables for zooming
        self.zoom = 1

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
        GL.glDrawBuffer(GL.GL_BACK)
        GL.glClearColor(137/255, 207/255, 240/255, 1.0)
        GL.glViewport(0, 0, size.width, size.height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(0, size.width, 0, size.height, -1, 1)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        GL.glTranslated(self.pan_x, self.pan_y, 0.0)
        GL.glScaled(self.zoom, self.zoom, self.zoom)

    def render(self, text):
        """Handle all drawing operations."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Draw specified text at position (10, 10)
        self.render_text(text, 10, 10)
        '''
        # Draw a sample signal trace
        GL.glColor3f(0.0, 0.0, 1.0)  # signal trace is blue
        GL.glBegin(GL.GL_LINE_STRIP)
        for i in range(10):
            x = (i * 20) + 10
            x_next = (i * 20) + 30
            if i % 2 == 0:
                y = 75
            else:
                y = 100
            GL.glVertex2f(x, y)
            GL.glVertex2f(x_next, y)
        GL.glEnd()
        '''
        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()
        

    def display_signals_gui(self):
        '''Draw the signal trace(s) on the canvas.'''
        print("Displaying signals on GUI.")
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        # Clear everything
        print("clearing")
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        '''Testing
        margin = 60 
        monitors_dictionary = collections.OrderedDict([
            (("G1", None), ["HIGH", "HIGH", "LOW", "LOW"]),
            (("Q", "QBAR"), ["HIGH", "LOW", "LOW", "HIGH"])])
        monitors_names = {
            ("G1", None): "G1",
            ("Q", "QBAR"): "Q.QBAR"
        '''
        margin = self.monitors.get_margin()
        y_pos = 125  # starting y position for drawing
        #for device_id, output_id in monitors_dictionary:
        for device_id, output_id in self.monitors.monitors_dictionary:
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            # monitor_name = monitors_names[(device_id, output_id)]
            signal_list = self.monitors.monitors_dictionary[(device_id, output_id)]
            # signal_list = monitors_dictionary[(device_id, output_id)]
            print("Signal list=", signal_list)
            # Render the monitor name at the start of the line
            self.render_text(monitor_name, 10, y_pos)
            x_pos = 10 + margin  # starting x position for drawing signals
            prev_y = y_pos
            for signal in signal_list:
                GL.glColor3f(0.0, 0.0, 1.0)  
                GL.glBegin(GL.GL_LINE_STRIP)  # start drawing line strip
                if signal == self.devices.HIGH:   
                    y = y_pos + 20
                if signal == self.devices.LOW:
                    y = y_pos
                if signal == self.devices.RISING: 
                    y = y_pos + 5
                if signal == self.devices.FALLING: 
                    y = y_pos - 5
                if signal == self.devices.BLANK:  
                    y = y_pos
                GL.glVertex2f(x_pos, prev_y)  # vertex at the previous y position
                GL.glVertex2f(x_pos, y)  # vertex at the new y position
                GL.glVertex2f(x_pos + 20, y)  # vertex at the new y position and next x position
                GL.glEnd()  # end drawing line strip
                prev_y = y
                x_pos += 20  # move to the next position for drawing
            y_pos += 40  # move to the next line for drawing
        # We have been drawing to the back buffer, flush the graphics pipeline
        # and swap the back buffer to the front
        GL.glFlush()
        self.SwapBuffers()

    def on_paint(self, event):
        """Handle the paint event."""
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices
            self.init_gl()
            self.init = True

        size = self.GetClientSize()
        text = "".join(["Canvas redrawn on paint event, size is ",
                        str(size.width), ", ", str(size.height)])
        self.render(text)

    def on_size(self, event):
        """Handle the canvas resize event."""
        # Forces reconfiguration of the viewport, modelview and projection
        # matrices on the next paint event
        self.init = False

    def on_mouse(self, event):
        """Handle mouse events."""
        text = ""
        # Calculate object coordinates of the mouse position
        size = self.GetClientSize()
        ox = (event.GetX() - self.pan_x) / self.zoom
        oy = (size.height - event.GetY() - self.pan_y) / self.zoom
        old_zoom = self.zoom
        if event.ButtonDown():
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            text = "".join(["Mouse button pressed at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.ButtonUp():
            text = "".join(["Mouse button released at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Leaving():
            text = "".join(["Mouse left canvas at: ", str(event.GetX()),
                            ", ", str(event.GetY())])
        if event.Dragging():
            self.pan_x += event.GetX() - self.last_mouse_x
            self.pan_y -= event.GetY() - self.last_mouse_y
            self.last_mouse_x = event.GetX()
            self.last_mouse_y = event.GetY()
            self.init = False
            text = "".join(["Mouse dragged to: ", str(event.GetX()),
                            ", ", str(event.GetY()), ". Pan is now: ",
                            str(self.pan_x), ", ", str(self.pan_y)])
        if event.GetWheelRotation() < 0:
            self.zoom *= (1.0 + (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Negative mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if event.GetWheelRotation() > 0:
            self.zoom /= (1.0 - (
                event.GetWheelRotation() / (20 * event.GetWheelDelta())))
            # Adjust pan so as to zoom around the mouse position
            self.pan_x -= (self.zoom - old_zoom) * ox
            self.pan_y -= (self.zoom - old_zoom) * oy
            self.init = False
            text = "".join(["Positive mouse wheel rotation. Zoom is now: ",
                            str(self.zoom)])
        if text:
            self.render(text)
        else:
            self.Refresh()  # triggers the paint event

    def render_text(self, text, x_pos, y_pos):
        """Handle text drawing operations."""
        GL.glColor3f(0.0, 0.0, 0.0)  # text is black
        GL.glRasterPos2f(x_pos, y_pos)
        font = GLUT.GLUT_BITMAP_HELVETICA_12

        for character in text:
            if character == '\n':
                y_pos = y_pos - 20
                GL.glRasterPos2f(x_pos, y_pos)
            else:
                GLUT.glutBitmapCharacter(font, ord(character))


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
    OpenID = 998  # define the ID for the open file operation
    def __init__(self, title, path, names, devices, network, monitors):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))

        # Parameters
        self.names = names
        self.devices = devices
        self.network = network
        self.monitors = monitors
        self.cycles_completed = 0  # number of simulation cycles completed

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_ABOUT, "&About")
        fileMenu.Append(wx.ID_EXIT, "&Exit")
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(self, devices, monitors)

        # Configure the widgets
        self.text = wx.StaticText(self, wx.ID_ANY, "Cycles")
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, "Run")
        self.continue_button = wx.Button(self, wx.ID_ANY, "Continue")
        self.text_box = wx.TextCtrl(self, wx.ID_ANY, "",
                                    style=wx.TE_PROCESS_ENTER)

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.text_box.Bind(wx.EVT_TEXT_ENTER, self.on_text_box)

        # Create checkboxes for signals
        self.monitored_signals, self.not_monitored_signals = self.monitors.get_signal_names()  # replace with your list variable
        # self.monitored_signals = ["Q1.QBAR"]
        # self.not_monitored_signals = ["G1", "SW2", "SW4"]

        for signal in self.monitored_signals:
            checkbox = wx.CheckBox(self, label=signal)
            checkbox.SetValue(True)  # Set checkbox as ticked
            self.Bind(wx.EVT_CHECKBOX, self.on_checkbox, checkbox)

        for signal in self.not_monitored_signals:
            checkbox = wx.CheckBox(self, label=signal)
            checkbox.SetValue(False)  # Set checkbox as unticked
            self.Bind(wx.EVT_CHECKBOX, self.on_checkbox, checkbox)
        
        # Create Sliders for Switches
        self.switch_sliders = []
        switches = self.devices.find_devices(device_kind="SWITCH")
        for switch in switches:
            switch_name = self.names.get_name_string(switch)
            label = wx.StaticText(self, label=switch_name)
            slider = wx.Slider(self, value=switch.switch_state, minValue=0, maxValue=1, style=wx.SL_HORIZONTAL)
            slider.Bind(wx.EVT_SLIDER, lambda event, index=switch: self.on_slider_change(event, index))
            self.switch_sliders.append(slider)

            switch_sizer = wx.BoxSizer(wx.HORIZONTAL)
            switch_sizer.Add(label, 1, wx.ALL, 5)
            switch_sizer.Add(slider, 1, wx.ALL, 5)

            side_sizer.Add(switch_sizer, 1, wx.EXPAND)


        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(side_sizer, 1, wx.ALL, 5)

        side_sizer.Add(self.text, 1, wx.TOP, 10)
        side_sizer.Add(self.spin, 1, wx.ALL, 5)
        side_sizer.Add(self.run_button, 1, wx.ALL, 5)
        side_sizer.Add(self.continue_button, 1, wx.ALL, 5)
        side_sizer.Add(self.text_box, 1, wx.ALL, 5)

        # Add checkboxes to side_sizer
        for checkbox in self.GetChildren():
            if isinstance(checkbox, wx.CheckBox):
                side_sizer.Add(checkbox, 1, wx.ALL, 5)
        
        self.SetSizeHints(600, 600)
        self.SetSizer(main_sizer)

        # Create a toolbar with an open file button
        toolbar = self.CreateToolBar()
        open_image = wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR)
        toolbar.AddTool(self.OpenID, "Open file", open_image)
        toolbar.Bind(wx.EVT_TOOL, self.on_toolbar)
        toolbar.Realize()
        self.ToolBar = toolbar

        

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        Id = event.GetId()
        if Id == wx.ID_EXIT:
            self.Close(True)
        if Id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Mojisola Agboola\n2017",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)

    def on_spin(self, event):
        """Handle the event when the user changes the spin control value."""
        spin_value = self.spin.GetValue()
        text = "".join(["New spin control value: ", str(spin_value)])
        self.canvas.render(text)

    def on_run_button(self, event):
        """Handle the event when the user clicks the run button."""
        #text = "Run button pressed."
        #self.canvas.render(text)

        """Run the simulation from scratch."""
        self.cycles_completed = 0
        cycles = self.spin.GetValue()
        #self.run_simulation(cycles)
        
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
        self.canvas.display_signals_gui()
        print("Completed simulation.")
        return True
        

    def on_text_box(self, event):
        """Handle the event when the user enters text."""
        text_box_value = self.text_box.GetValue()
        text = "".join(["New text box value: ", text_box_value])
        #self.canvas.render(text)

    def on_toolbar(self, event):  # handle toolbar events
        if event.GetId() == self.OpenID:
            openFileDialog = wx.FileDialog(self, "Open txt file", "", "", wildcard="TXT files (*.txt)|*.txt", style=wx.FD_OPEN + wx.FD_FILE_MUST_EXIST)
            if openFileDialog.ShowModal() == wx.ID_CANCEL:
                print("The user cancelled")
                return
            print("File chosen=", openFileDialog.GetPath())

    def on_checkbox(self, event):
        checkbox = event.GetEventObject()
        signal = checkbox.GetLabel()
        is_checked = checkbox.IsChecked()

        if is_checked:
            print(f"{signal} is checked")
             # Add the signal to the monitored_signals list
            if signal not in self.monitored_signals:
                self.monitored_signals.append(signal)
            # Remove the signal from the not_monitored_signals list
            if signal in self.not_monitored_signals:
                self.not_monitored_signals.remove(signal)
            self.monitor_command(signal)
        else:
            print(f"{signal} is unchecked")
            # Remove the signal from the monitored_signals list
            if signal in self.monitored_signals:
                self.monitored_signals.remove(signal)
            # Add the signal to the not_monitored_signals list
            if signal not in self.not_monitored_signals:
                self.not_monitored_signals.append(signal)
            self.zap_command(signal)
    
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
        """Handle the event when the user changes the slider value."""
        slider = event.GetEventObject()
        value = slider.GetValue()
        print(f"Slider {index} value is {value}")
        self.devices.set_switch_value(index, value)
        self.canvas.display_signals_gui()