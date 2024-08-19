import os
import subprocess
from tkinter import Menu, messagebox, simpledialog


class PipMenu(Menu):
    NAME = "pip"

    def __init__(self, master=None, main=None):
        self.main = main
        super().__init__(master, tearoff=False)
        self.add_command(
            label="install package", command=self.pip_install)
        self.add_command(label="freeze", command=self.pip_freeze)

    def pip_install(self):
        """this func asks pip package and installs.
        """
        if os.path.isdir(self.main.dir_path):
            package = simpledialog.askstring(
                "install package", "type pip package name here")
            if package:
                venv_path = os.path.join(
                    self.main.dir_path, r".venv\Scripts\python.exe")
                command = [
                    venv_path if os.path.isfile(venv_path) else "python",
                    "-m", "pip", "install", package]
                self.code_runner(command)

    def pip_freeze(self):
        """this func generates requirements.txt.
        """
        if os.path.isdir(self.main.dir_path):
            venv_path = os.path.join(
                self.main.dir_path, r".venv\Scripts\python.exe")
            command = [
                venv_path if os.path.isfile(venv_path) else "python",
                "-m", "pip", "freeze", ">", "requirements.txt"]
            try:
                subprocess.run(command, shell=True)
            except subprocess.CalledProcessError as e:
                messagebox.showerror(
                    title="subprocess.CalledProcessError", message=str(e))
