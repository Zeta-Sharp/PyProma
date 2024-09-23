import os
import subprocess
import venv
from tkinter import Menu, messagebox


class VenvMenu(Menu):
    NAME = "venv"

    def __init__(self, master=None, main=None):
        self.main = main
        super().__init__(master, tearoff=False)
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
