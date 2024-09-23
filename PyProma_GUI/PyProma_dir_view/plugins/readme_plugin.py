import os
import tkinter as tk
from tkinter import scrolledtext

from PyProma_common.PyProma_templates import tab_template
from PyProma_dir_view.plugins.plugin_manager import RefreshMethod


class ReadmeTab(tab_template.TabTemplate):
    NAME = "README"

    def __init__(self, master=None, main=None):
        super().__init__(master, main)
        self.readme_text = scrolledtext.ScrolledText(self)
        text = "There is no README.md in this directory."
        self.readme_text.insert(tk.END, text)
        self.readme_text.pack(fill=tk.BOTH, expand=True)

    @RefreshMethod
    def refresh(self):
        """this func reads README.md and writes on readme_text.
        """
        readme_path = os.path.join(self.main.dir_path, "README.md")
        if os.path.isfile(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            text = "There is no README.md in this directory."
        self.readme_text.delete("1.0", tk.END)
        self.readme_text.insert(tk.END, text)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x575")
    readme_tab = ReadmeTab(root)
    readme_tab.pack()
    root.mainloop()
