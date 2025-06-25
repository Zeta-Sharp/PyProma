"""
name: README
version: "1.2.0"
author: rikeidanshi <rikeidanshi@duck.com>
type: Tab
description: README viewer.
dependencies:
    - markdown: "^3.7"
    - tkhtmlview: "^0.3.1"
settings: null
"""

import os
import tkinter as tk
from typing import TYPE_CHECKING

import markdown
from PyProma_common.PyProma_templates.tab_template import TabTemplate
from tkhtmlview import HTMLLabel

if TYPE_CHECKING:
    from PyProma_dir_view.plugins.plugin_manager import PluginManager


class ReadmeTab(TabTemplate):
    NAME = "README"

    def __init__(self, master: tk.Tk, main: "PluginManager"):
        super().__init__(master, main)
        self.readme_htmlview = HTMLLabel(self)
        self.readme_htmlview.set_html(
            "<p>There is no README.md in this directory.</p>")
        self.readme_htmlview.pack(fill=tk.BOTH, expand=True)

    @TabTemplate.RefreshMethod
    def read_readme(self):
        """this func reads README.md and writes on readme_text.
        """
        readme_path = os.path.join(self.main.dir_path, "README.md")
        if os.path.isfile(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                text = f.read()
            html = markdown.markdown(text)
        else:
            html = "<p>There is no README.md in this directory.</p>"
        self.readme_htmlview.set_html(html)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x575")
    readme_tab = ReadmeTab(root, None)
    readme_tab.pack()
    root.mainloop()
