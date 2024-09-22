from abc import ABC
from tkinter import Frame


class TabTemplate(ABC, Frame):
    def __init__(self, master=None, main=None):
        self.main = main
        super().__init__(master, width=800, height=575)
        self.propagate(False)
