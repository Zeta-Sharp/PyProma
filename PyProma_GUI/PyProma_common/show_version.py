import sys
import tkinter as tk
from textwrap import dedent

import toml


class ShowVersion(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("version information")
        toml_file = "pyproject.toml"
        with open(toml_file, "r") as f:
            config = toml.load(f)
        app_version = config["tool"]["poetry"]["version"]
        version_text = f"""\
        Tkinter: {tk.TkVersion}
        Python: {sys.version}
        application: {app_version}"""
        version_label = tk.Label(self, text=dedent(version_text))
        version_label.pack()
        self.mainloop()
