from abc import ABC
from tkinter import Menu
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from PyProma.PyProma_GUI.PyProma_dir_view.plugins.plugin_manager import \
        PluginManager as DirPluginManager
    from PyProma.PyProma_GUI.PyProma_project_view.plugins.plugin_manager import \
        PluginManager as ProjectPluginManager


class MenuTemplate(ABC, Menu):
    def __init__(
            self,
            master: Menu,
            main: Union["DirPluginManager", "ProjectPluginManager"]):
        self.main = main
        super().__init__(master, tearoff=False)
