#coding:utf-8

"""
_____________                           .__ 
\__    ___/  | _____  ___          __ __|__|
  |    |  |  |/ /\  \/  /  ______ |  |  \  |
  |    |  |    <  >    <  /_____/ |  |  /  |
  |____|  |__|_ \/__/\_ \         |____/|__|
               \/      \/                   

The Tkx Python library, create modern frameless GUIs with Python and Tkinter.
    - author : Martin Gate <martingate98000@gmail.com>
    - github repo : https://www.github.com/MartinGate/tkx.git


Copyright (c) 2021, Martin Gate, Xvelta, Inc.
All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.
* Neither the Xvelta, Inc. nor the
  names of its contributors may be used to endorse or promote products
  derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE REGENTS AND CONTRIBUTORS BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

try:
    import tkinter as tk # For Python 3.x
    from tkinter import TclError
except ImportError:
    import Tkinter as tk # For Python 2.x

# internal library imports
from .constants import *

# python built-in libraries imports
import threading
import platform

# Get the height of the taskbar for Windows users
if platform.system() == "Windows":
    try:
        from win32api import GetMonitorInfo, MonitorFromPoint

        monitor_info = GetMonitorInfo(MonitorFromPoint((0,0)))
        monitor_area = monitor_info.get("Monitor")
        work_area = monitor_info.get("Work")
        
        TOOLBAR_HEIGHT = monitor_area[3]-work_area[3]

    except ImportError or ModuleNotFoundError:
        print("!Tkx::WARNING -> You should install win32api by typing the following command : 'pip install win32api'.")
        TOOLBAR_HEIGHT = 0

# On other platforms, we consider that there is no taskbar
else:
    TOOLBAR_HEIGHT = 0


WIDTH_MARGIN, HEIGHT_MARGIN = 30, 10


class FramelessDragBehaviour():

    def __init__(self, master, widget, border_events=True):
        """
        Create a drag behaviour.

        You can apply it to a widget (both tkinter and ttk widgets) so that when you drag it,
        it will automatically move a specified window.

        For instance, the FramelessDragBehaviour class is used, 
        to simulate the border's drag events of a frameless window.

        Params:
            master : tkx.Tk / tkinter.Tk / tix.Tk / tkinter.TopLevel / tix.TopLevel [Draggable window]
            widget : Whatever widget used to drag the specified window
            border_events : True [default] / False [Should the FramelessDragBehaviour simulate the Windows' border resizing events]
        """
        self._master = master
        self._widget = widget
        self._border_events = border_events
        self.x = None
        self.y = None
        self.mouse_x, self.mouse_y = None, None

        self._widget.bind("<Button-1>", self.startMove)
        self._widget.bind("<ButtonRelease-1>", self.stopMove)
        self._widget.bind("<B1-Motion>", self.moving)

    def startMove(self, event=None):
        """ The widget starts moving. """
        self.x = event.x
        self.y = event.y

    def stopMove(self, event=None):
        """ The widget stops moving. """
        screen_width, screen_height = self._master.winfo_screenwidth(), self._master.winfo_screenheight()

        if self._border_events:
            # Reproduces window manager border-drag&drop fonctionnality
            if self.mouse_y <= HEIGHT_MARGIN and (self.mouse_x > WIDTH_MARGIN) and (self.mouse_x < (screen_width - WIDTH_MARGIN)):
                self._master._state = MAXIMIZED
                self._master.geometry("{}x{}+0+0".format(screen_width, screen_height - TOOLBAR_HEIGHT))

            elif self.mouse_y <= HEIGHT_MARGIN and self.mouse_x <= WIDTH_MARGIN:
                self._master._state = UPPER_LEFT
                self._master.geometry("{}x{}+0+0".format(screen_width//2, screen_height//2))

            elif self.mouse_y <= HEIGHT_MARGIN and self.mouse_x >= screen_width - WIDTH_MARGIN:
                self._master._state = UPPER_RIGHT
                self._master.geometry("{}x{}+{}+0".format(screen_width//2, screen_height//2, screen_width - screen_width//2))
            
            elif self.mouse_y >= screen_height - TOOLBAR_HEIGHT - HEIGHT_MARGIN and self.mouse_x <= WIDTH_MARGIN:
                self._master._state = LOWER_LEFT
                self._master.geometry("{}x{}+0+{}".format(screen_width//2, screen_height//2, screen_height - screen_height//2 - TOOLBAR_HEIGHT))
            
            elif self.mouse_y >= screen_height - TOOLBAR_HEIGHT - HEIGHT_MARGIN and self.mouse_x >= screen_width - WIDTH_MARGIN:
                self._master._state = UPPER_RIGHT
                self._master.geometry("{}x{}+{}+{}".format(screen_width//2, screen_height//2, screen_width - screen_width//2, screen_height - screen_height//2 - TOOLBAR_HEIGHT))

            elif self.mouse_x <= WIDTH_MARGIN:
                self._master._state = RIGHT
                self._master.geometry("{}x{}+0+0".format(screen_width//2, screen_height - TOOLBAR_HEIGHT))

            elif self.mouse_x >= screen_width - WIDTH_MARGIN:
                self._master._state = RIGHT
                self._master.geometry("{}x{}+{}+0".format(screen_width//2, screen_height - TOOLBAR_HEIGHT, screen_width - screen_width//2))

        # Refresh the window preview after 1 second
        change_window_preview_thread = threading.Thread(target=self._master._change_window_preview)
        self._master.after(1000, lambda: change_window_preview_thread.start())

        self.x = None
        self.y = None

    def moving(self, event=None):
        """ The widget is moving. """
        self.mouse_x, self.mouse_y = event.x_root, event.y_root

        x = (event.x_root - self.x - self._widget.winfo_x() + self._widget.winfo_x())
        y = (event.y_root - self.y - self._widget.winfo_y() + self._widget.winfo_y())

        self._master.geometry("+%s+%s" % (x, y))

    def disable_winbehaviours(self):
        self._border_events = False

    def enable_winbehaviours(self):
        self._border_events = True
