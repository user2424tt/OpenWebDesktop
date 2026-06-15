from tkinter import *
from child_window import ChildWindow

class Window:
    def __init__(self, width, height, title="WebDesktop", resizable=(False, False), icon=None):
        self.root = Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(resizable[0], resizable[1])

        if icon:
            self.root.iconphoto(False, PhotoImage(file=icon))

    def run(self):
        self.root.mainloop()

    def createChild(self, width, height, title="WebDesktop", resizable=(False, False), icon=None):
        return ChildWindow(self.root, width, height, title, resizable, icon)