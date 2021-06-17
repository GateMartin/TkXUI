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
except ImportError:
    import Tkinter as tk # For Python 2.x
    import ttk

# internal library imports
from tkinter import TclError, constants
from .constants import *
from .behaviors import FramelessDragBehaviour
from .Tk import Tk

# python built-in modules imports
import json


class JSONLoader():

    def __init__(self, master, json_file=None):
        self.master = master
        self.__ui_elements = {}
        self.__custom_widgets = {}
        self.__classes = {}
        self.__names = {}

        self.generate(json_file)

    def generate(self, json_file=None, master=None):
        if json_file == None:
            return

        # load Json data
        with open(json_file , 'r') as file:
            data = file.read()
            data_list = data.split('"')

            counter = 0

            for i in range(len(data_list)):
                if data_list[i][:2] == "tk" or data_list[i][:3] == "ttk" or data_list[i][0] == "@":
                    data_list[i] = data_list[i] + '#' + str(counter)

                    counter += 1

            data = '"'.join(data_list)
            self.__ui_elements[json_file] = json.loads(data)

        if self.__ui_elements[json_file]['doctype'] == 'ui-definition':
            # Create a queue of to-create widgets
            widget_queue = self.create_widget_queue(self.__ui_elements[json_file])

            # Create each widget
            for zone in widget_queue:
                for widget in zone:
                    if master == None:
                        if widget['zone'] == "border":
                            parent = "self.master.border"
                        elif widget['zone'] == 'main':
                            parent = "self.master"
                        else:
                            # A Custom Widget Handler object is its parent
                            try:
                                parent = "self.master." + widget['zone']
                            except TypeError:
                                parent = "self.master"
                        
                        if widget["parent"] == '':
                            draw_parent = "self.master"
                        else:
                            draw_parent = "self.master." + widget["parent"]

                    else:
                        # Widgets are reparented to another widget than the window
                        if widget['zone'] == "main":
                            parent = "self.master." + master
                        else:
                            # A Custom Widget Handler object is its parent
                            try:
                                parent = "self.master." + master  + "." + widget['zone']
                            except TypeError:
                                parent = "self.master." + master

                        if widget["parent"] == '':
                            draw_parent = "self.master." + master
                        else:
                            draw_parent = "self.master." + master + "." + widget["parent"]

                    widget_type = widget['widget_type'].split('#')[0]
                    config = widget["config"]

                    self.create_widget(parent, widget_type, config.copy(), draw_parent=draw_parent)

        elif self.__ui_elements[json_file]['doctype'] == 'theme':
            self.__applyTheme(self.__ui_elements[json_file])
        
    def create_widget_queue(self, json_data):
        widget_queue = []

        def check_subwidgets(widget_attrs, zone=None):
            sub_widgets = []
            for i in widget_attrs:
                if i[:2] == "tk" or i[:3] == "ttk" or i[0] == "@":
                    try:
                        parent = widget_attrs['name']
                    except KeyError:
                        if zone == 'border':
                            parent = zone
                        else:
                            parent = ''

                    if i[0] != "@":
                        sub_widgets.append({'widget_type':i, 'config':widget_attrs[i], 'parent':parent, 'zone': zone})

                        temp_sub_widgets = check_subwidgets(widget_attrs[i])
                        try:
                            for i in range(len(temp_sub_widgets)):
                                sub_widgets.append(temp_sub_widgets[i])
                        except TypeError:
                            # Object does not have subwidgets
                            pass

                    else:
                        class CustomWidgetHandler(object):
                            def __init__(self):
                                """ Object used to handle a custom widget. """
                                pass

                        # Create a custom widget handler to get access to the subwidgets
                        try:
                            eval(f"self.master.{widget_attrs[i]['name']}")
                        except AttributeError:
                            # Create the custom widget handler
                            try:
                                exec(f"self.master.{widget_attrs[i]['name']} = CustomWidgetHandler()")
                            except Exception:
                                print("!Tkx::ERROR: Unable to create custom widget handler.")

                        # There is a custom widget
                        widget_name = "widget:"+ i.split("@")[1].split("#")[0]

                        for n in range(len(self.__custom_widgets[widget_name])):
                            dict_custom_widget = self.__custom_widgets[widget_name][n].copy()

                            if dict_custom_widget['parent'] != '':
                                dict_custom_widget['parent'] = widget_attrs[i]['name'] + '.' + dict_custom_widget['parent']
                            else:
                                dict_custom_widget['parent'] = parent
                            
                            dict_custom_widget['zone'] = widget_attrs[i]['name']                            
                            sub_widgets.append(dict_custom_widget)
            
            if sub_widgets: 
                return sub_widgets

        # The user is not allowed to put the same zone twice, so we use a for loop
        for zone in json_data:
            # Set the exploring zone
            if zone == 'main' or zone == 'border':
                widget_queue.append(check_subwidgets(json_data[zone], zone=zone))
            elif zone[:6] == 'widget':
                self.__custom_widgets[zone] = check_subwidgets(json_data[zone], zone=zone)

        return widget_queue

    def __applyTheme(self, data):
        def all_children (wid) :
            _list = wid.winfo_children()

            for item in _list :
                if item.winfo_children() :
                    _list.extend(item.winfo_children())

            return _list

        def apply_attr(widget, data):
            try:
                widget.config(data)
            except TclError as e:
                print(f"!Tkx::ERROR: Cannot apply theme to {type(widget).__name__} -->", e)

        children = all_children(self.master)
        
        for i in children:
            for attr in data:
                # Get name attribute
                try:
                    name = attr.split('#')[1]
                except Exception:
                    name = "NONAME"
                
                # Get class attribute
                try:
                    _class = attr.split('.')[1]
                except Exception:
                    _class = 'NOCLASS'

                _attr = attr.split('#')[0]
                    
                if "tk." + type(i).__name__ == _attr:
                    apply_attr(i, data[attr])

                if attr == "doctype":
                    pass
                if attr == "window":
                    apply_attr(self.master, data[attr])
                if attr == "border":
                    try:
                        self.master.config_border(data[attr])
                    except Exception:
                        print("!Tkx:WARNING --> You can't customize the border of a normal tkinter window, you should use a Tkxui window instead.")

                if name in self.__names:
                    apply_attr(self.__names[name], data[attr])
                
                if _class in self.__classes:              
                    for widget in self.__classes[_class]:
                        apply_attr(widget, data[attr])
               
    def create_widget(self, parent_widget, widget_type, widget_dict, draw_parent="self.master"):
        # Remove all sub_widgets
        sub_widgets = []
        for attr in widget_dict:
            if attr[:2] == "tk" or attr[:3] == "ttk" or attr[0] == "@":
                sub_widgets.append(attr)

        for to_remove in sub_widgets:
            del widget_dict[to_remove]
        
        try:
            # Get the given name of the widget 
            widget_name =  widget_dict['name']
            # Delete this non-recognize attribute
            del widget_dict['name']

        except KeyError:
            # if no one is specified, the user won't be able to access it from its parent
            widget_name = "unnamed"

        # Get the pack options of the widget
        try:
            pack_options = widget_dict['pack_options']
            # Retrieve the non-recognize attribute
            del widget_dict['pack_options']

        except KeyError:
            pack_options = ""

        # Get the class of the widget
        try:
            widget_class = widget_dict['class']
            # Retrieve the non-recognize attribute
            del widget_dict['class']
        except KeyError:
            widget_class = None
        
        # Create the widget
        try:
            exec(f"{parent_widget}.{widget_name} = {widget_type}({draw_parent})")
            
            if widget_class != None:
                # Assigning its class
                try:
                    # Get the list of widget that have the same class
                    other_widgets = self.__classes[widget_class]
                except:
                    other_widgets = []

                other_widgets.append(eval(f"{parent_widget}.{widget_name}"))
                self.__classes[widget_class] = other_widgets 

            if widget_name != "unnamed":
                self.__names[widget_name] = eval(f"{parent_widget}.{widget_name}")

            temp_widget = eval(f"{parent_widget}.{widget_name}")
            temp_widget.config(**widget_dict)
        except Exception as e:
            print(f"!Tkx::WARNING: Unable to create {widget_type} ---> " + str(e))

        # Pack the widget
        try:
            for attr in pack_options:
                if pack_options[attr][0] == '(':
                    pack_options[attr] = eval(pack_options[attr])

            exec(f"{parent_widget}.{widget_name}.pack({pack_options})")

        except Exception as e:
            print(f"!Tkx::WARNING: Unable to pack {widget_type} ---> " + str(e))

                
if __name__ in '__main__':
    root = Tk(display=FRAMELESS)
    root.geometry("800x500")
    root.center()
    json_loader = JSONLoader(root)
    json_loader.generate("ui.json")
    json_loader.generate("dark_theme.json")

    # root.disable_winbehaviours()
    root.config_border({
        'close':{
            'hoverbg': 'red',
            'hoverfg': "white"
        }
    })

    # root.label_frame_container.config(bg="red")

    root.mainloop()
        
