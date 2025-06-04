"""
name: Linter
version: "1.0.0"
author: rikeidanshi <rikeidanshi@duck.com>
type: Tab
description: Supports automatic execution of linters.
dependencies:
    - flake8: "^7.1.1"
    - pylint: "^3.2.7"
settings: null
"""

import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

from PyProma_common.PyProma_templates import tab_template
from PyProma_dir_view.plugins.plugin_manager import PyFileMethod, RefreshMethod

if TYPE_CHECKING:
    from PyProma_dir_view.plugins.plugin_manager import PluginManager


class LinterTab(tab_template.TabTemplate):
    NAME = "Linter"

    def __init__(self, master: tk.Tk, main: "PluginManager"):
        super().__init__(master, main)
        self.result_tree = ttk.Treeview(self, show=["tree", "headings"])
        self.result_tree.heading(
            "#0",
            text="Linter",
            anchor=tk.CENTER)
        self.result_tree.pack(fill=tk.BOTH, expand=True)

    @RefreshMethod
    def refresh(self):
        self.result_tree.delete(
            *self.result_tree.get_children())

    def start_linter(self, target_path):
        result = subprocess.run(
            ["pylint", target_path], capture_output=True, text=True)
        pylint_results = result.stdout.splitlines()[1:-4]
        result = subprocess.run(
            ["flake8", target_path], capture_output=True, text=True)
        flake8_results = result.stdout.splitlines()
        if len(pylint_results) > 0 or len(flake8_results) > 0:
            parent = self.result_tree.insert(
                "", tk.END, text=target_path)
            for result in flake8_results:
                self.result_tree.insert(parent, tk.END, text=result)
            for result in pylint_results:
                self.result_tree.insert(parent, tk.END, text=result)

    @PyFileMethod
    def run_linter(self, target_path):
        if "venv" not in target_path:
            if os.path.isfile(target_path):
                thread = threading.Thread(
                    target=lambda: self.start_linter(target_path))
                thread.start()
