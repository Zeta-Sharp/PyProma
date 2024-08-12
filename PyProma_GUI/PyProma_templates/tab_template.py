from abc import ABC, abstractmethod
from tkinter import Frame


class TabTemplate(ABC, Frame):
    def __init__(self, master=None):
        super().__init__(master, width=800, height=575)
        self.propagate(False)

    @abstractmethod
    def refresh(self):
        pass
