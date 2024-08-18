import os
from tkinter import Menu, messagebox

import git


class GitMenu(Menu):
    NAME = "Git"

    def __init__(self, master=None, main=None):
        self.main = main
        super().__init__(master, tearoff=False)
        self.add_command(
            label="Git Init", command=self.git_init)

    def git_init(self):
        """this func runs git init
        """
        if os.path.isdir(self.main.dir_path):
            git_path = os.path.join(self.main.dir_path, ".git")
            if not os.path.isdir(git_path):
                try:
                    git.Repo.init(self.main.dir_path)
                except git.exc.GitCommandError as e:
                    messagebox.showerror(
                        title="git.exc.GitError", message=str(e))
