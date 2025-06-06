"""
name: IDE
version: "1.0.0"
author: rikeidanshi <rikeidanshi@duck.com>
type: Menu
description: Supports cooperation with IDE.
dependencies: null
settings: null
"""

import os
import subprocess
import tkinter as tk
from typing import TYPE_CHECKING

from PyProma_common.PyProma_templates.menu_template import MenuTemplate

if TYPE_CHECKING:
    from PyProma_dir_view.plugins.plugin_manager import PluginManager


class IDEMenu(MenuTemplate):
    NAME = "IDE"

    def __init__(self, master: tk.Tk, main: "PluginManager"):
        super().__init__(master, main)
        self.add_command(
            label="Open Visual Studio Code",
            command=self.open_vscode,
            state=tk.NORMAL if self.check_vscode_in_path() else tk.DISABLED)
        self.add_command(
            label="Open PyCharm",
            command=self.open_pycharm,
            state=tk.NORMAL if self.check_pycharm_in_path() else tk.DISABLED)

    def check_vscode_in_path(self):
        for path in os.environ["PATH"].split(os.pathsep):
            if "Microsoft VS Code\\bin" in path:
                return True
        return False

    def check_pycharm_in_path(self):
        return "PyCharm Community Edition" in os.environ

    def open_vscode(self):
        if self.main.dir_path:
            subprocess.Popen(["code", "-n", self.main.dir_path], shell=True)

    def open_pycharm(self):
        if self.main.dir_path:
            subprocess.Popen(["pycharm", self.main.dir_path], shell=True)
