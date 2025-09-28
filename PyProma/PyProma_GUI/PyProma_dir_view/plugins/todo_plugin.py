"""
name: ToDo
version: "1.0.0"
author: rikeidanshi <rikeidanshi@duck.com>
type: Tab
description: Scann comments in .py file and display ToDos.
dependencies: null
settings: null
"""

import re
import tkinter as tk
import tkinter.ttk as ttk
from typing import TYPE_CHECKING, Union

from PyProma.PyProma_GUI.PyProma_common.PyProma_templates.tab_template import \
    TabTemplate

if TYPE_CHECKING:
    from PyProma.PyProma_GUI.PyProma_dir_view.plugins.plugin_manager import \
        PluginManager


class TodoTab(TabTemplate):
    NAME = "ToDo"

    def __init__(
            self, master: Union[tk.Tk, ttk.Notebook], main: "PluginManager"):
        super().__init__(master, main)
        self.todo_tree = ttk.Treeview(self, show=["tree", "headings"])
        self.todo_tree.heading("#0", text="ToDo", anchor=tk.CENTER)
        self.todo_tree.pack(fill=tk.BOTH, expand=True)

    @TabTemplate.RefreshMethod
    def refresh(self):
        self.todo_tree.delete(*self.todo_tree.get_children())

    @TabTemplate.PyFileMethod
    def find_todo(self, filename: str):
        """this func finds todos and add node to todo_tree.
        this finds "# TODO", "# BUG", "# FIXME", "# HACK".

        Args:
            filename (string): path to .py file
        """
        if "venv" not in filename:
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
            comments = []
            for i, line in enumerate(lines):
                match = re.search(r"#\s*(TODO|BUG|FIXME|HACK)\s+(.*)", line)
                if match:
                    tag, text = match.groups()
                    comments.append(
                        [tag, i + 1, text])

            if len(comments) > 0:
                parent = self.todo_tree.insert(
                    "",
                    tk.END,
                    text=filename.replace(self.main.dir_path + "\\", ""))
                for tag, line_no, todo_text in comments:
                    self.todo_tree.insert(
                        parent,
                        tk.END,
                        text=f"{tag} {todo_text}(line {line_no})")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x575")
    todo_tab = TodoTab(root, None)
    todo_tab.pack()
    root.mainloop()
