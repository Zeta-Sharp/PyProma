import subprocess

from PyProma_common.PyProma_templates import tab_template


class LinterTab(tab_template.TabTemplate):
    NAME = "Linter"

    def __init__(self, master=None, main=None):
        super().__init__(master, main)

    def refresh(self):
        return super().refresh()
