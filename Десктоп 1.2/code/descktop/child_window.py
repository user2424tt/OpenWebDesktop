from tkinter import *

class ChildWindow:
    def __init__(self, parent, width, height, title="WebDesktop", resizable=(False, False), icon=None):
        self.root = Toplevel(parent)
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(resizable[0], resizable[1])

        if icon:
            self.root.iconphoto(False, PhotoImage(file=icon))

        self.grab_focus()

    def grab_focus(self):
        self.root.grab_set()
        self.root.focus_set()