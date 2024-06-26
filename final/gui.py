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
import argparse
import subprocess
import builtins
import os
builtins._ = wx.GetTranslation


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

    display_signals_gui(self): Draws the signal trace(s) on the canvas.
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
        GL.glClearColor(1.0, 1.0, 1.0, 1.0)
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
        GL.glFlush()
        self.SwapBuffers()

    def display_signals_gui(self):
        """
        Draw the signal trace(s) on the canvas.

        This method sets the current context,
        initializes the GL if not already done, clears the buffer,
        calculates the margin, and iterates over the monitors
        dictionary to draw the signal traces. Finally, it flushes
        the graphics pipeline and swaps the buffers.
        """
        self.SetCurrent(self.context)
        if not self.init:
            # Configure the viewport, modelview and projection matrices.
            self.init_gl()
            self.init = True

        # Clear everything.
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        margin = self.monitors.get_margin()
        margin = margin * 10 if margin is not None else 0
        y_pos = 125  # Starting y position for drawing.
        num_signals_list = []

        for device_id, output_id in self.monitors.monitors_dictionary:
            monitor_name = self.devices.get_signal_name(device_id, output_id)
            key = (device_id, output_id)
            signal_list = self.monitors.monitors_dictionary[key]
            num_signals_list.append(len(signal_list))

            # Render the monitor name at the start of the line.
            self.render_text(monitor_name, 10, y_pos)
            x_pos = 10 + margin  # Starting x position for drawing signals.
            prev_y = y_pos
            cycle = 0
            for signal in signal_list:
                GL.glColor3f(0.0, 0.0, 1.0)
                GL.glBegin(GL.GL_LINE_STRIP)  # Start drawing line strip.

                if signal == self.devices.HIGH:
                    y = y_pos + 20
                elif signal == self.devices.LOW:
                    y = y_pos
                elif signal == self.devices.RISING:
                    y = y_pos + 5
                elif signal == self.devices.FALLING:
                    y = y_pos - 5
                elif signal == self.devices.BLANK:
                    y = y_pos

                # Vertex at the previous y position.
                GL.glVertex2f(x_pos, prev_y)
                # Vertex at the new y position.
                GL.glVertex2f(x_pos, y)
                # Vertex at the new y position and next x position.
                GL.glVertex2f(x_pos + 20, y)
                GL.glEnd()  # End drawing line strip.
                self.render_text("|", x_pos, 103)
                self.render_text(str(cycle), x_pos - 2, 88)
                cycle += 1
                prev_y = y
                x_pos += 20  # Move to the next position for drawing.
            y_pos += 40  # Move to the next line for drawing.
        try:
            x_axis_length = max(num_signals_list) * 20
        except ValueError:
            x_axis_length = 0
        GL.glColor3f(0.0, 0.0, 0.0)  # Set color to black.
        GL.glBegin(GL.GL_LINES)  # Start drawing lines.
        GL.glVertex2f(10 + margin, 105)
        GL.glVertex2f(10 + margin + x_axis_length, 105)
        GL.glEnd()  # End drawing lines.

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
        self.display_signals_gui()

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
            # self.render(text)
            self.display_signals_gui()
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

    def reset_view(self):
        """Reset the canvas view to the initial state."""
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
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

    on_run_button(self, event): Event handler for when the user clicks the run.
                                    Run the simulation from scratch.

    on_continue_button(self, event): Event handler for when the user clicks
                                        the continue button.

    run_simulation(self, cycles): Run the simulation for a specific
                                    number of cycles.

    on_toolbar(self, event): Event handler for when the user clicks the
                                toolbar. Open a file dialog to choose a file.

    on_checkbox(self, event): Event handler for when the user checks/unchecks
                                a box. Monitor/zap output signal accordingly.

    monitor_command(self, signal): Set the specified monitor.

    zap_command(self, signal): Remove the specified monitor.

    on_slider_change(self, event, index): Event handler for when the user
                                            changes the slider value.
    """

    QuitID = 999
    OpenID = 998

    def __init__(
            self,
            title,
            path,
            names,
            devices,
            network,
            monitors,
            cycles_completed):
        """Initialise widgets and layout."""
        super().__init__(parent=None, title=title, size=(800, 600))
        QuitID = 999
        OpenID = 998

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
        # number of simulation cycles completed
        self.cycles_completed = cycles_completed

        # Configure the file menu
        fileMenu = wx.Menu()
        menuBar = wx.MenuBar()
        fileMenu.Append(wx.ID_OPEN, _("&Open File"))
        fileMenu.Append(wx.ID_ABOUT, _("&About"))
        fileMenu.Append(wx.ID_EXIT, _("&Exit"))
        menuBar.Append(fileMenu, _("&File"))
        self.SetMenuBar(menuBar)

        # Canvas for drawing signals
        self.canvas = MyGLCanvas(
            self,
            devices,
            monitors,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.Size(
                800,
                600))

        # Set font
        font = wx.Font(
            10,
            wx.FONTFAMILY_DEFAULT,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD,
            False,
            "Verdana")

        # Configure the widgets
        self.switch_button = wx.Button(
            self, label=_("Switch to 3D"), size=(300, 25))

        # Edit switch to 3D button
        # Set the color of the button to light blue
        self.switch_button.SetBackgroundColour(wx.Colour(173, 216, 230))

        self.text = wx.StaticText(self, wx.ID_ANY, _("Cycles"))
        self.text.SetFont(font)
        self.spin = wx.SpinCtrl(self, wx.ID_ANY, "10")
        self.run_button = wx.Button(self, wx.ID_ANY, _("Run"))
        self.continue_button = wx.Button(self, wx.ID_ANY, _("Continue"))
        self.reset_view_button = wx.Button(self, wx.ID_ANY, _("Reset View"))

        # Bind events to widgets
        self.Bind(wx.EVT_MENU, self.on_menu)
        self.spin.Bind(wx.EVT_SPINCTRL, self.on_spin)
        self.run_button.Bind(wx.EVT_BUTTON, self.on_run_button)
        self.continue_button.Bind(wx.EVT_BUTTON, self.on_continue_button)
        self.Bind(wx.EVT_CLOSE, self.on_close_window)
        self.reset_view_button.Bind(wx.EVT_BUTTON, self.on_reset_view_button)
        self.switch_button.Bind(wx.EVT_BUTTON, self.on_switch)

        # Create a scrolled window for the switches and signals
        scroll = wx.ScrolledWindow(self, -1, size=wx.Size(300, 400))
        scroll.SetScrollbars(0, 16, 50, 15)
        self.scroll_sizer = wx.BoxSizer(wx.VERTICAL)

        # Configure sizers for layout
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        side_sizer = wx.BoxSizer(wx.VERTICAL)

        main_sizer.Add(self.canvas, 5, wx.EXPAND | wx.ALL, 5)
        main_sizer.Add(side_sizer, 1, wx.EXPAND, 5)

        side_sizer.Add(self.switch_button, 0, wx.TOP | wx.FIXED_MINSIZE, 5)
        side_sizer.Add(self.text, 0, wx.TOP, 10)
        side_sizer.Add(self.spin, 0, wx.TOP, 5)
        side_sizer.Add(self.run_button, 0, wx.TOP, 5)
        side_sizer.Add(self.continue_button, 0, wx.TOP, 5)
        side_sizer.Add(self.reset_view_button, 0, wx.TOP, 5)

        # Create a label for switches
        switches_label = wx.StaticText(scroll, label=_("Switches"))
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
            slider = wx.Slider(
                scroll,
                value=switch_device.switch_state,
                minValue=0,
                maxValue=1,
                style=wx.SL_HORIZONTAL)
            slider.Bind(
                wx.EVT_SLIDER,
                lambda event,
                index=switch: self.on_slider_change(
                    event,
                    index))
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
        signals = self.monitors.get_signal_names()
        self.monitored_signals, self.not_monitored_signals = signals
        outputs_label = wx.StaticText(
            scroll, label=_("Outputs (tick to monitor)"))
        outputs_label.SetFont(font)
        self.scroll_sizer.Add(outputs_label, 0, wx.ALL, 10)

        self.checkboxes = []  # List to store all checkboxes

        for signal in self.monitored_signals:
            checkbox = wx.CheckBox(scroll, label=signal)
            checkbox.SetValue(True)  # Set checkbox as ticked
            self.Bind(
                wx.EVT_CHECKBOX,
                lambda event,
                cb=checkbox: self.on_checkbox(
                    event,
                    cb),
                checkbox)
            self.checkboxes.append(checkbox)

        for signal in self.not_monitored_signals:
            checkbox = wx.CheckBox(scroll, label=signal)
            checkbox.SetValue(False)  # Set checkbox as unticked
            self.Bind(
                wx.EVT_CHECKBOX,
                lambda event,
                cb=checkbox: self.on_checkbox(
                    event,
                    cb),
                checkbox)
            self.checkboxes.append(checkbox)

        # Add checkboxes to sizer
        for checkbox in self.checkboxes:
            self.scroll_sizer.Add(checkbox, 1, wx.ALL, 5)

        side_sizer.AddSpacer(10)
        scroll.SetSizer(self.scroll_sizer)
        side_sizer.Add(scroll, 1, wx.EXPAND | wx.RIGHT, 5)
        side_sizer.AddSpacer(10)
        self.SetSizeHints(500, 500)
        self.SetSizer(main_sizer)
        self.Layout()

    def on_menu(self, event):
        """Handle the event when the user selects a menu item."""
        id = event.GetId()
        if id == wx.ID_EXIT:
            self.Close(True)
        if id == wx.ID_ABOUT:
            wx.MessageBox("Logic Simulator\nCreated by Group 15\n2024",
                          "About Logsim", wx.ICON_INFORMATION | wx.OK)
        if event.GetId() == wx.ID_OPEN:
            # Read the file content.
            with open(self.file_path, 'r') as f:
                content = f.read()

            # Create a dialog to display the file content.
            dialog = wx.Dialog(self, title="File Content")
            textctrl = wx.TextCtrl(
                dialog,
                value=content,
                style=wx.TE_MULTILINE | wx.TE_READONLY)
            sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(textctrl, proportion=1, flag=wx.EXPAND)
            dialog.SetSizer(sizer)
            dialog.ShowModal()

    def on_spin(self, event):
        """Spin control value event."""
        spin_value = self.spin.GetValue()
        text = "".join(["New spin control value: ", str(spin_value)])
        self.canvas.display_signals_gui()

    def on_reset_view_button(self, event):
        """Reset view button handler."""
        self.canvas.reset_view()
        self.canvas.display_signals_gui()

    def on_switch(self, event):
        """Switch to 3D button handler."""
        self.Close()
        from gui_3D import Gui as Gui3D
        gui = Gui3D(
            '3D GUI',
            self.path,
            self.names,
            self.devices,
            self.network,
            self.monitors,
            self.cycles_completed)
        gui.Show(True)

    def on_run_button(self, event):
        """Run button handler."""
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
        self.canvas.display_signals_gui()
        print("Completed simulation.")
        return True

    def on_text_box(self, event):
        """Handle the event when the user enters text."""
        text_box_value = self.text_box.GetValue()
        text = "".join(["New text box value: ", text_box_value])
        self.canvas.display_signals_gui()

    def on_checkbox(self, event, checkbox):
        """Handle the event when the user checks/unchecks a box."""
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
        """Handle the event when the user changes the slider value."""
        slider = event.GetEventObject()
        value = slider.GetValue()
        self.devices.set_switch(index, value)

    def on_close_window(self, event):
        """Handle the event when the user closes the window."""
        self.Destroy()
