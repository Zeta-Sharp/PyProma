from abc import ABC
from tkinter import Menu


class MenuTemplate(ABC, Menu):
    def __init__(self, master=None, main=None):
        self.main = main
        super().__init__(master, tearoff=False)
