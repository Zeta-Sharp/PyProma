import os
from tkinter import Menu, filedialog


class FileMenu(Menu):
    NAME = "File"

    def __init__(self, master=None, main=None):
        self.main = main
        super().__init__(master, tearoff=False)
        self.add_command(
            label="Open directory", command=self.set_dir_path)

    def set_dir_path(self):
        """this func asks directory and sets dir_path.
        after this func -> refresh_trees().
        """
        path = os.path.normpath(
            filedialog.askdirectory().replace("\\", "/"))
        if os.path.isdir(path) and path != ".":
            self.main.dir_path = path
            self.main.refresh_trees()
