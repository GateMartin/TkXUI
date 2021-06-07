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
    import tkinter.ttk as ttk
    from tkinter import font
except ImportError:
    import Tkinter as tk # For Python 2.x
    import ttk

# internal library imports
from .constants import *
from .behaviors import FramelessDragBehaviour

# external libraries imports
try:
    from PIL import ImageTk, ImageGrab
except ModuleNotFoundError:
    # print("!Tkx::ERROR -> You must install the Pillow library by typing the following command : 'pip install Pillow'.")
    raise ImportError("!Tkx::ERROR -> You must install the Pillow library by typing the following command : 'pip install Pillow'.")

# python built-in libraries imports
import threading


class CoreUI(tk.Tk):

    def __init__(self, *args, **kwargs):
        """
        Parent of the frameless window.
        The CoreUI class is used to display its child (the frameless window) on the taskbar,
        as it is normally ignored by the machine's window manager.
        """
        tk.Tk.__init__(self, **kwargs)
        self.title('tk')

        self.__preview = tk.Label(self)
        self.__preview.pack(fill=tk.BOTH, expand=1)

    def change_preview(self, img):
        """ Set a preview image to the frameless window. """
        self.__preview.config(image=img)
        self.__preview.image = img


class Tk(tk.Tk, tk.Toplevel):

    def __init__(self, display=NATIVE, defaultBorder=True, isResizable=True, **kwargs):
        """
        Create a tkx.Tk window.

        Params:
            display : tkx.NATIVE (normal window) [default] / tkx.FRAMELESS (frameless window, fully customizable)
            defaultBorder : True [default] / False (Wether to instanciate or not a default border for a frameless window)
            isResizable : True [default] / False (Wether to create or not a resizer object so that the frameless window can be resized)
            **kwargs : other tk.Tk parameters
        """
        self._display = display
        self._is_resizable = isResizable
        self._has_default_border = defaultBorder

        self.default_border_attributes = None

        self._state = NORMAL
        
        if self.is_frameless():
            self.__coreUI = CoreUI()
            self.__coreUI.attributes('-alpha', 0.0) #For icon
            self.__coreUI.bind("<Map>", self.deiconify_frameless)
            self.__coreUI.bind("<Unmap>", self.iconify_frameless)
            self.__coreUI.protocol("WM_DELETE_WINDOW", lambda : self.destroy())

            tk.Toplevel.__init__(self, self.__coreUI, **kwargs)

            self.overrideredirect(1) # Removes the border of the TopLevel
            self.attributes('-transparentcolor', TRANSPARENT)

            # Create a FramelessResizeBehaviour object to resize the window associated with a ttk.Sizer
            if self._is_resizable and self.is_frameless():
                self.resizer = ttk.Sizegrip(self)
                self.resizer.place(relx=1.0, rely=1.0, anchor="se")

                self.resizer.bind("<ButtonRelease-1>", self._change_window_preview)
                self.bind('<Map>', lambda a: self.tkraise_frameless())

            generate_preview = threading.Thread(target=self._change_window_preview)
            generate_preview.start()

        else:
            tk.Tk.__init__(self, **kwargs)

        # Make sure the window is on top of the CoreUI
        self.lift()

        if self._has_default_border:
            self.default_border_attributes = {
                    'close' : {
                        'bg': self.cget('bg'),
                        'fg': "black",
                        'hoverbg': "white",
                        'hoverfg': "black"
                        },
                    'minimize' : {
                        'bg': self.cget('bg'),
                        'fg': "black",
                        'hoverbg': "white",
                        'hoverfg': "black"
                    },
                    'maximize' : {
                        'bg': self.cget('bg'),
                        'fg': "black",
                        'hoverbg': "white",
                        'hoverfg': "black"
                    },
                    'border' : {
                        'bg': self.cget('bg')
                    }
                }
        
            self.createDefaultBorder()
    
    def current_state(self):
        return self._state

    def createDefaultBorder(self):
        """ Create a border for a frameless window if its defaultBorder parameter is set to True. """

        self.border = tk.Frame(self)
        self.border.config(bg=self.border.master.cget('bg'))

        self.border.framelessDragBehaviour = FramelessDragBehaviour(self, self.border)

        def on_minhover(event=None):
            self.border.minimize.config(bg=self.default_border_attributes['minimize']['hoverbg'])
            self.border.minimize.config(fg=self.default_border_attributes['minimize']['hoverfg'])

        def on_minunhover(event=None):
            self.border.minimize.config(bg=self.default_border_attributes['minimize']['bg'])
            self.border.minimize.config(fg=self.default_border_attributes['minimize']['fg'])

        def on_maxhover(event=None):
            self.border.maximize.config(bg=self.default_border_attributes['maximize']['hoverbg'])
            self.border.maximize.config(fg=self.default_border_attributes['maximize']['hoverfg'])

        def on_maxunhover(event=None):
            self.border.maximize.config(bg=self.default_border_attributes['maximize']['bg'])
            self.border.maximize.config(fg=self.default_border_attributes['maximize']['fg'])

        def on_closehover(event=None):
            self.border.close.config(bg=self.default_border_attributes['close']['hoverbg'])
            self.border.close.config(fg=self.default_border_attributes['close']['hoverfg'])

        def on_closeunhover(event=None):
            self.border.close.config(bg=self.default_border_attributes['close']['bg'])
            self.border.close.config(fg=self.default_border_attributes['close']['fg'])

        self.border.close = tk.Button(self.border, text = "X", cursor="hand2", bg=self.default_border_attributes['close']['bg'], fg=self.default_border_attributes['close']['fg'], border=0, command = lambda: self.destroy(), font=("Consolas", 15))
        self.border.close.bind("<Enter>", on_closehover)
        self.border.close.bind("<Leave>", on_closeunhover)
        self.border.close.pack(side=tk.RIGHT)

        char = u"\u25A1"
        self.border.maximize = tk.Button(self.border, text = char, cursor="hand2", bg=self.default_border_attributes['maximize']['bg'], fg=self.default_border_attributes['maximize']['fg'], border=0, command = lambda: self.maximize(), font=("Consolas", 15))
        self.border.maximize.bind("<Enter>", on_maxhover)
        self.border.maximize.bind("<Leave>", on_maxunhover)
        self.border.maximize.pack(side=tk.RIGHT, padx=(0, 2))

        self.border.minimize = tk.Button(self.border, text = "_", cursor="hand2", bg=self.default_border_attributes['minimize']['bg'], fg=self.default_border_attributes['minimize']['fg'], border=0, command = lambda: self.withdraw(), font=("Consolas", 15))
        self.border.minimize.bind("<Enter>", on_minhover)
        self.border.minimize.bind("<Leave>", on_minunhover)
        self.border.minimize.pack(side=tk.RIGHT, padx=(0, 2))

        self.border.pack(fill=tk.X, anchor='nw')

    def maximize(self, event=None):
        """ Maximize the window. """
        self.geometry("{}x{}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight() - 40))

    def tkraise_frameless(self, event=None):
        """ Raise the window resizer always on top of other widgets """
        self.resizer.tkraise()

    def resize_core(self, event=None):
        """
        Resize the parent window of the frameless window to fit the size of its child.
        (used to display the window in the taskbar
        despite the overrideredirect flag set to the frameless window)
        """
        self.__coreUI.geometry("{}x{}".format(self.winfo_width(), self.winfo_height()))
        
    def _change_window_preview(self, event=None):
        """
        Generate a preview (displayed in the taskbar) of a frameless window.
        """
        self.resize_core()
  
        bbox = (self.winfo_x(), self.winfo_y(), self.winfo_x() + self.winfo_width(), self.winfo_y() + self.winfo_height())

        img = ImageGrab.grab(bbox)
        self.__coreUI.change_preview(ImageTk.PhotoImage(img))

    def deiconify_frameless(self, event=None):
        """ Internal method to make the frameless window visible when its parent is mapped. """
        self.deiconify()
    
    def iconify_frameless(self, event=None):
        """ Internal method to make the frameless window invisible when its parent is unmapped. """
        self.withdraw()

    def iconbitmap(self, icon):
        """ Change the icon of the window. """
        if self.is_frameless():
            self.__coreUI.iconbitmap(icon)
        else:
            tk.Tk.iconbitmap(self, icon)
    
    def title(self, title="tkx"):
        """ Change the title of the window. """
        if self.is_frameless():
            self.__coreUI.title(title)
        else:
            tk.Tk.title(self, title)

    def is_frameless(self):
        """ Check if the window is a frameless window or not. """
        if self._display == FRAMELESS:
            return True
        else:
            return False

    def destroy(self):
        """ Destroy the window. """ 
        if self.is_frameless():
            tk.Toplevel.destroy(self)
            self.__coreUI.destroy()
        else:
            tk.Tk.destroy(self)

    def attributes(self, attr, *value):
        """ Setter:
                Set an attribute to the window.
            Getter:
                Get an attribute of the window.
        """
        if self.is_frameless():
            if attr == '-topmost':
                if value != ():
                    tk.Toplevel.attributes(self, attr, *value)

                    if tk.Toplevel.attributes(self, '-topmost'):
                        self.__coreUI.unbind("<Unmap>")
                    else:
                        self.__coreUI.bind("<Unmap>", self.iconify_frameless)

                else:
                    return tk.Toplevel.attributes(self, attr)

            else:
                if value != ():
                    tk.Toplevel.attributes(self, attr, *value)
                else:
                    return tk.Toplevel.attributes(self, attr)

        else:
            if value != ():
                tk.Tk.attributes(self, attr, *value)
            else:
                return tk.Tk.attributes(self, attr)

    def center(self):
        """ Center the window in the center of the screen. """
        self.update_idletasks()
        # Get the requested values of the height and width.
        windowWidth = self.winfo_width()
        windowHeight = self.winfo_height()
        
        # Get both half the screen width/height and window width/height
        positionRight = int(self.winfo_screenwidth()/2 - windowWidth/2)
        positionDown = int(self.winfo_screenheight()/2 - windowHeight/2)
        
        # Positions the window in the center of the page.
        self.geometry("+{}+{}".format(positionRight, positionDown))

    def disable_winbehaviours(self, event=None):
        """ Disable the Windows borders drag&drop-resize events. """
        if self.is_frameless() and self._has_default_border:
            self.border.framelessDragBehaviour._border_events = False
    
    def enable_winbehaviours(self, event=None):
        """ Enable the Windows borders drag&drop-resize events. """
        if self.is_frameless() and self._has_default_border:
            self.border.framelessDragBehaviour._border_events = True

    def resizer_bg(self, bg="#2A2A2A"):
        """ Change the background color of the frameless window's sizer. """
        style = ttk.Style()
        style.configure("TSizegrip", background=bg)

    def config_border(self, config):
        """
        Configure the attributes of the default border's widgets.

        Example : To make the background color of the close button red and its text color black, the argument must be :
            {
                'close': {'bg':"red", 'fg':"black"}
            }

        You can also pass extra args for the widgets' hover colors, for instance:
            'minimize' : {'hoverbg': "lightblue", 'hoverfg': "white"}


        Widgets you can configure : "close", "minimize", "border" (doesn't support hover colors), "maximize"
        """
        if self._has_default_border:
            for wdgt in config:
                for attr in config[wdgt]:
                    if attr == "hoverbg" or attr == "hoverfg":
                        pass
                    else:
                        if wdgt == 'close':
                            widget = self.border.close
                        if wdgt == 'minimize':
                            widget = self.border.minimize
                        if wdgt == 'border':
                            widget = self.border
                        if wdgt == 'maximize':
                            widget = self.border.maximize
                        
                        temp_attr = {attr: config[wdgt][attr]}
                        widget.config(temp_attr)

                    self.default_border_attributes[wdgt][attr] = config[wdgt][attr]
        else:
            pass


if __name__ == '__main__':
    root = Tk(display=FRAMELESS)
    root.geometry("500x300")
    root.disable_winbehaviours()
    root.center()
    root.mainloop()
