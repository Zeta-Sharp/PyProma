import os
import subprocess
import tkinter as tk
from tkinter import ttk

from PyProma_common.PyProma_templates import tab_template


class LinterTab(tab_template.TabTemplate):
    NAME = "Linter"

    def __init__(self, master=None, main=None):
        super().__init__(master, main)
        self.result_tree = ttk.Treeview(self, show=["tree", "headings"])
        self.result_tree.heading(
            "#0",
            text="Linter",
            anchor=tk.CENTER)
        self.result_tree.pack(fill=tk.BOTH, expand=True)

    def refresh(self):
        self.result_tree.delete(
            *self.result_tree.get_children())

    def run_pylint(self, target_path):
        if "venv" not in target_path:
            if os.path.isfile(target_path):
                result = subprocess.run(
                    ["pylint", target_path], capture_output=True, text=True)
                pylint_results = result.stdout.splitlines()[1:-4]
                if len(pylint_results) > 0:
                    parent = self.result_tree.insert(
                        "", tk.END, text=target_path)
                    for result in pylint_results:
                        self.result_tree.insert(parent, tk.END, text=result)
