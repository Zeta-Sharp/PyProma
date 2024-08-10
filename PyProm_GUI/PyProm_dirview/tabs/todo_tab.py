import re
import tkinter as tk
import tkinter.ttk as ttk

import tabs.tab_template


class ToDoTab(tabs.tab_template.TabTemplate):
    NAME = "ToDo"

    def __init__(self, master=None, main=None):
        self.main = main
        super().__init__(master)
        self.todo_tree = ttk.Treeview(self, show=["tree", "headings"])
        self.todo_tree.heading("#0", text="ToDo", anchor=tk.CENTER)
        self.todo_tree.pack(fill=tk.BOTH, expand=True)

    def refresh(self):
        self.todo_tree.delete(*self.todo_tree.get_children())

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
