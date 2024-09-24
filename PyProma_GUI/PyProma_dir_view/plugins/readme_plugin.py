import os
import tkinter as tk

import markdown
from PyProma_common.PyProma_templates import tab_template
from PyProma_dir_view.plugins.plugin_manager import RefreshMethod
from tkhtmlview import HTMLLabel


class ReadmeTab(tab_template.TabTemplate):
    NAME = "README"

    def __init__(self, master=None, main=None):
        super().__init__(master, main)
        self.readme_htmlview = HTMLLabel(self)
        self.readme_htmlview.set_html(
            "<p>There is no README.md in this directory.</p>")
        self.readme_htmlview.pack(fill=tk.BOTH, expand=True)

    @RefreshMethod
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
    readme_tab = ReadmeTab(root)
    readme_tab.pack()
    root.mainloop()
