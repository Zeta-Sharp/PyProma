"""
name: pip
version: "1.1.0"
author: rikeidanshi <rikeidanshi@duck.com>
type: Menu
description: Supports pip operations.
dependencies: null
settings: null
"""

import os
import subprocess
import tkinter as tk
from tkinter import messagebox, simpledialog

from PyProma_common.code_runner import CodeRunner


class PipMenu(tk.Menu):
    NAME = "pip"

    def __init__(self, master=None, main=None):
        self.main = main
        super().__init__(master, tearoff=False)
        self.add_command(
            label="install package", command=self.pip_install)
        self.add_command(label="upgrade", command=self.upgrade_pip)
        self.add_command(label="freeze", command=self.pip_freeze)

    def pip_install(self):
        """this func asks pip package and installs.
        """
        if os.path.isdir(self.main.dir_path):
            package = simpledialog.askstring(
                "install package", "type pip package name here")
            if package:
                venv_path = os.path.join(
                    self.main.dir_path,
                    ".venv/Scripts/python.exe" if os.name == "nt"
                    else ".venv/bin/activate")
                command = [
                    venv_path if os.path.isfile(venv_path) else "python",
                    "-m", "pip", "install", package]
                CodeRunner.code_runner(command, cwd=self.main.dir_path)
                self.main.refresh_main()

    def upgrade_pip(self):
        if os.path.isdir(self.main.dir_path):
            venv_path = os.path.join(
                self.main.dir_path, self.get_venv_path())
            command = [
                venv_path if os.path.isfile(venv_path) else "python",
                "-m", "pip", "install", "--upgrade pip"]
            CodeRunner.code_runner(command, cwd=self.main.dir_path)

    def pip_freeze(self):
        """this func generates requirements.txt.
        """
        if os.path.isdir(self.main.dir_path):
            venv_path = os.path.join(
                self.main.dir_path, self.get_venv_path())
            command = [
                venv_path if os.path.isfile(venv_path) else "python",
                "-m", "pip", "freeze", ">", "requirements.txt"]
            try:
                subprocess.run(command, shell=True, cwd=self.main.dir_path)
            except subprocess.CalledProcessError as e:
                messagebox.showerror(
                    title="subprocess.CalledProcessError", message=str(e))
            finally:
                self.main.refresh_main()

    @staticmethod
    def get_venv_path():
        match os.name:
            case "nt":
                return ".venv/Scripts/python.exe"
            case "posix":
                return ".venv/bin/python.exe"
