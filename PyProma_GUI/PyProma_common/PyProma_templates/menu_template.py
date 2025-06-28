from abc import ABC
from tkinter import Menu, Tk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PyProma_dir_view.plugins.plugin_manager import PluginManager


class MenuTemplate(ABC, Menu):
    def __init__(self, master: Tk, main: "PluginManager"):
        self.main = main
        super().__init__(master, tearoff=False)
