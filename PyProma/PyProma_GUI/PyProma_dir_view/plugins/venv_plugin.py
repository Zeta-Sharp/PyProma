"""
name: venv
version: "1.1.0"
author: rikeidanshi <rikeidanshi@duck.com>
type: Menu
description: Supports venv operations.
dependencies: null
settings: null
"""

import os
import subprocess
import tkinter as tk
import venv
from tkinter import messagebox
from typing import TYPE_CHECKING

from PyProma.PyProma_GUI.PyProma_common.PyProma_templates.menu_template import \
    MenuTemplate

if TYPE_CHECKING:
    from PyProma.PyProma_GUI.PyProma_dir_view.plugins.plugin_manager import \
        PluginManager


class VenvMenu(MenuTemplate):
    NAME = "venv"

    def __init__(self, master: tk.Menu, main: "PluginManager"):
        super().__init__(master, main)
        self.add_command(label="create", command=self.venv_create)

    def venv_create(self):
        """this func creates .venv environment.
        """
        if os.path.isdir(self.main.dir_path):
            try:
                venv_path = os.path.join(self.main.dir_path, ".venv")
                venv.create(venv_path)
                python_path = os.path.join(venv_path, "Scripts/python")
                subprocess.run([python_path, "-m", "ensurepip"])
            except OSError as e:
                messagebox.showerror(
                    title="OSError", message=str(e))
            self.main.refresh_main()
