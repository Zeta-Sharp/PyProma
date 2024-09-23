import os
import subprocess
import tkinter as tk


class IDEMenu(tk.Menu):
    NAME = "IDE"

    def __init__(self, master=None, main=None):
        self.main = main
        super().__init__(master, tearoff=False)
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
