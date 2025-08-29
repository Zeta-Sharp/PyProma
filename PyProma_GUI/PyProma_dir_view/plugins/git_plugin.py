"""
name: Git
version: "1.5.0"
author: rikeidanshi <rikeidanshi@duck.com>
type: Tab Menu
description: Supports Git operations.
dependencies:
    - gitpython: "3.1.43"
settings: null
"""
import os
# import re
import tkinter as tk
import tkinter.ttk as ttk
from textwrap import dedent
from tkinter import messagebox
from typing import TYPE_CHECKING, Union, cast

import git
import git.exc
# from github import Github
from PyProma_common.PyProma_templates.menu_template import MenuTemplate
from PyProma_common.PyProma_templates.tab_template import TabTemplate

if TYPE_CHECKING:
    from PyProma_dir_view.plugins.plugin_manager import PluginManager

json_path = "PyProma_settings.json"

# IDEA Add Git remotes e.g. GitHub, Azure DevOps support.
# However, it is difficult to save access tokens in settings file safely.


class GitTab(TabTemplate):
    NAME = "Git"

    def __init__(
            self, master: Union[tk.Tk, ttk.Notebook], main: "PluginManager"):
        super().__init__(master, main)
        self.git_tabs = ttk.Notebook(self)
        self.git_tabs.enable_traversal()
        self.local = GitLocalTab(self, main)
        self.git_tabs.add(self.local, text="Local", padding=3)
        self.remote = GitRemoteTab(self, main)
        self.git_tabs.add(self.remote, text="Remote", padding=3)
        self.git_tabs.pack(anchor=tk.NW)

    @TabTemplate.RefreshMethod
    def refresh(self):
        self.local.refresh()
        self.remote.refresh()


class GitLocalTab(tk.Frame):
    def __init__(self, master: tk.Frame, main: "PluginManager"):
        self.master, self.main = master, main
        super().__init__(master, width=800, height=550)
        self.propagate(False)
        self.git_log_frame = tk.Frame(self, width=400, height=550)
        self.git_log_frame.propagate(False)
        self.git_commit_tree = ttk.Treeview(
            self.git_log_frame, show="headings",
            columns=("hash", "author", "date", "message"))
        self.git_commit_tree.heading("hash", text="hash", anchor=tk.CENTER)
        self.git_commit_tree.heading("author", text="author", anchor=tk.CENTER)
        self.git_commit_tree.heading("date", text="date", anchor=tk.CENTER)
        self.git_commit_tree.heading(
            "message", text="message", anchor=tk.CENTER)
        self.git_commit_tree_vsb = ttk.Scrollbar(
            self.git_log_frame,
            orient="vertical",
            command=self.git_commit_tree.yview)
        self.git_commit_tree.configure(
            yscrollcommand=self.git_commit_tree_vsb.set)
        self.git_commit_tree_vsb.pack(side="right", fill="y")
        self.git_commit_tree_hsb = ttk.Scrollbar(
            self.git_log_frame,
            orient="horizontal",
            command=self.git_commit_tree.xview)
        self.git_commit_tree.configure(
            xscrollcommand=self.git_commit_tree_hsb.set)
        self.git_commit_tree_hsb.pack(side="bottom", fill="x")
        self.git_commit_tree.pack(fill=tk.BOTH, expand=True)
        self.git_log_frame.grid(row=0, column=0)
        self.git_staging_frame = tk.Frame(self, width=400, height=550)
        self.git_staging_frame.propagate(False)
        self.git_staged_txt = tk.Label(
            self.git_staging_frame, text="Staged Changes")
        self.git_staged_txt.place(x=5, y=0)
        self.git_staged_changes = ttk.Treeview(
            self.git_staging_frame, show="headings", height=8,
            columns=("file", "changes"))
        self.git_staged_changes.heading(
            "file", text="file", anchor=tk.CENTER)
        self.git_staged_changes.heading(
            "changes", text="changes", anchor=tk.CENTER)
        self.git_staged_changes.place(x=0, y=20)
        self.git_staged_changes.bind("<<TreeviewSelect>>", self.git_stage)
        self.git_unstaged_txt = tk.Label(
            self.git_staging_frame, text="Changes")
        self.git_unstaged_txt.place(x=5, y=210)
        self.git_unstaged_changes = ttk.Treeview(
            self.git_staging_frame, show="headings", height=8,
            columns=("file", "changes"))
        self.git_unstaged_changes.heading(
            "file", text="file", anchor=tk.CENTER)
        self.git_unstaged_changes.heading(
            "changes", text="changes", anchor=tk.CENTER)
        self.git_unstaged_changes.place(x=0, y=230)
        self.git_unstaged_changes.bind("<<TreeviewSelect>>", self.git_stage)
        self.commit_message = tk.Text(
            self.git_staging_frame, width=55, height=5)
        self.commit_message.insert(tk.END, "Commit message")
        self.commit_message.place(x=0, y=420)
        self.git_branches = ttk.Combobox(
            self.git_staging_frame, state=tk.DISABLED)
        self.git_branches.place(x=5, y=500)
        self.commit_button = tk.Button(
            self.git_staging_frame,
            text="Commit",
            command=self.git_commit,
            state=tk.DISABLED)
        self.commit_button.place(x=250, y=500)
        self.git_staging_frame.grid(row=0, column=1)

    def refresh(self):
        self.git_commit_tree.delete(*self.git_commit_tree.get_children())
        self.git_staged_changes.delete(
            *self.git_staged_changes.get_children())
        self.git_unstaged_changes.delete(
            *self.git_unstaged_changes.get_children())
        self.git_branches["values"] = []
        self.git_branches["state"] = tk.DISABLED
        self.git_branches.unbind("<<ComboboxSelected>>")
        self.commit_button["state"] = tk.DISABLED
        self.git_read_commits()
        self.git_read_diffs()
        if not os.path.isdir(os.path.join(self.main.dir_path, ".git")):
            return
        git_path = os.path.join(self.main.dir_path, ".git")
        repo = git.Repo(git_path)
        branches = [branch.name for branch in repo.branches]
        self.git_branches["values"] = branches
        self.git_branches["state"] = "readonly"
        self.git_branches.set(repo.active_branch)
        self.git_branches.bind(
            "<<ComboboxSelected>>", self.git_switch_branch)
        self.commit_button["state"] = tk.ACTIVE

    def git_read_commits(self):
        """this func reads git commit log and makes git tree.
        """
        if os.path.isdir(git_path := os.path.join(self.main.dir_path, ".git")):
            repo = git.Repo(git_path)
            for commit in repo.iter_commits():
                self.git_commit_tree.insert(
                    "",
                    tk.END,
                    values=(
                        commit.hexsha,
                        commit.author.name,
                        commit.authored_datetime,
                        commit.message))
        else:
            self.git_commit_tree.insert(
                "",
                tk.END,
                values=(
                    "this directory",
                    "is not",
                    "a git",
                    "repository"))

    def git_read_diffs(self):
        """this func reads git diffs and inserts into git_unstaged_changes.
        """
        if not os.path.isdir(os.path.join(self.main.dir_path, ".git")):
            return
        git_path = os.path.join(self.main.dir_path, ".git")
        repo = git.Repo(git_path)
        diffs = repo.index.diff(None)
        for diff in diffs:
            a = diff.a_path
            change_type = diff.change_type
            self.git_unstaged_changes.insert(
                "", tk.END, values=(a, change_type))
        diffs = repo.index.diff("HEAD")
        for diff in diffs:
            a = diff.a_path
            change_type = diff.change_type
            self.git_staged_changes.insert(
                "", tk.END, values=(a, change_type))

    def git_switch_branch(self, _: tk.Event):
        """this func switches local git branch

        Args:
            _ (tk.Event): tk.Event(ignored)
        """
        if not os.path.isdir(os.path.join(self.main.dir_path, ".git")):
            return
        git_path = os.path.join(self.main.dir_path, ".git")
        repo = git.Repo(git_path)
        try:
            repo.git.checkout(self.git_branches.get())
        except git.exc.GitCommandError as e:
            messagebox.showerror(
                title="git.exc.GitCommandError", message=str(e))
        else:
            self.main.refresh_main()
        finally:
            self.git_branches.set(repo.active_branch)

    def git_stage(self, event: tk.Event):
        """this func stage(unstage)s files.

        Args:
            event (tk.Event): tkinter event object
        """
        if not os.path.isdir(os.path.join(self.main.dir_path, ".git")):
            return
        git_path = os.path.join(self.main.dir_path, ".git")
        repo = git.Repo(git_path)
        widget: ttk.Treeview = cast(ttk.Treeview, event.widget)
        selected_item = widget.selection()
        if not selected_item:
            return
        item_values = widget.item(selected_item[0])["values"]
        if not item_values:
            return
        if widget == self.git_staged_changes:
            try:
                repo.index.reset(
                    paths=[item_values[0]])
            except git.exc.GitCommandError as e:
                messagebox.showerror(
                    title="git.exc.GitCommandError",
                    message=str(e))
            else:
                self.git_unstaged_changes.insert(
                    "", tk.END,
                    values=item_values)
                widget.delete(selected_item[0])
        elif widget == self.git_unstaged_changes:
            try:
                repo.git.add(item_values[0])
            except git.exc.GitCommandError as e:
                messagebox.showerror(
                    title="git.exc.GitCommandError",
                    message=str(e))
            else:
                self.git_staged_changes.insert(
                    "", tk.END,
                    values=item_values)
                widget.delete(selected_item[0])

    def git_commit(self):
        """this func commits staged diffs
        """
        if not os.path.isdir(os.path.join(self.main.dir_path, ".git")):
            return
        git_path = os.path.join(self.main.dir_path, ".git")
        repo = git.Repo(git_path)
        commit_message = self.commit_message.get(1., tk.END)
        staged_changes = repo.index.diff("HEAD")
        literal_message = commit_message.replace(" ", "").replace("\n", "")
        if (len(literal_message) > 0
                and commit_message != "Commit message\n"):
            if len(staged_changes) == 0:
                message = """\
                There are no staged changes and so you cannot commit.
                Would you like to stage all changes and commit directly?
                """
                if messagebox.askokcancel(
                        title="Confirm", message=dedent(message)):
                    repo.git.add(".")
                else:
                    return
            try:
                repo.index.commit(message=commit_message)
            except git.exc.CommandError as e:
                messagebox.showerror(
                    title="git.exc.CommandError",
                    message=str(e))
            finally:
                self.main.refresh_main()
        else:
            messagebox.showerror(
                title="Commit message is Empty",
                message="Please write commit message in entry box.")


class GitRemoteTab(tk.Frame):
    def __init__(self, master: tk.Frame, main: "PluginManager"):
        self.master, self.main = master, main
        super().__init__(master, width=800, height=550)
#        self.access_tokens = self.main.load_settings(
#            self, "access_tokens", value={"github": ""}, mode="set", initialize=True)
        self.propagate(False)
        self.remotes_label = tk.Label(self, text="remote:")
        self.remotes_label.pack()
        self.remotes_combo = ttk.Combobox(self, state=tk.DISABLED)
        self.remotes_combo.pack()
        self.branches_label = tk.Label(self, text="branch:")
        self.branches_label.pack()
        self.local_branches_combo = ttk.Combobox(self, state=tk.DISABLED)
        self.local_branches_combo.pack()
        self.pull_button = tk.Button(
            self, text="pull", state=tk.DISABLED, command=self.remote_pull)
        self.pull_button.pack()
        self.push_button = tk.Button(
            self, text="push", state=tk.DISABLED, command=self.remote_push)
        self.push_button.pack()
        self.fetch_button = tk.Button(
            self, text="fetch", state=tk.DISABLED, command=self.remote_fetch)
        self.fetch_button.pack()

    def refresh(self):
        self.remotes_combo["values"] = []
        self.remotes_combo["state"] = tk.DISABLED
        self.local_branches_combo["values"] = []
        self.local_branches_combo["state"] = tk.DISABLED
        self.pull_button["state"] = tk.DISABLED
        self.push_button["state"] = tk.DISABLED

        if not os.path.isdir(os.path.join(self.main.dir_path, ".git")):
            return
        git_path = os.path.join(self.main.dir_path, ".git")
        repo = git.Repo(git_path)
        branches = [branch.name for branch in repo.branches]
        self.local_branches_combo["values"] = branches
        self.local_branches_combo.set(repo.active_branch)
        self.local_branches_combo["state"] = "readonly"
        remote_name = [remote.name for remote in repo.remotes]
        if remote_name:
            if len(remote_name) > 1:
                remote_name.append("ALL")
            self.remotes_combo["values"] = remote_name
            self.remotes_combo.set(remote_name[0])
            self.remotes_combo["state"] = "readonly"
            self.pull_button["state"] = tk.ACTIVE
            self.push_button["state"] = tk.ACTIVE
            r"""
            remotes = repo.remote().urls
            github_pattern = r"https://github\.com/[^/]+/[^/]"
            github_remotes = [
                url.removeprefix("https://github.com/")
                for url in remotes if re.match(github_pattern, url)]
            if github_remotes and self.access_tokens["github"]:
                github = Github(self.access_tokens["github"])
                self.github_remotes = [
                    github.get_repo(remote_name)
                    for remote_name in github_remotes]
            """

    def remote_pull(self):
        if not os.path.isdir(os.path.join(self.main.dir_path, ".git")):
            return
        git_path = os.path.join(self.main.dir_path, ".git")
        repo = git.Repo(git_path)
        if self.remotes_combo.get() == "ALL":
            remote_names = [remote.name for remote in repo.remotes]
        else:
            remote_names = [self.remotes_combo.get()]
        for remote_name in remote_names:
            remote = repo.remote(remote_name)
            remote.pull(self.local_branches_combo.get())

    def remote_push(self):
        if not os.path.isdir(os.path.join(self.main.dir_path, ".git")):
            return
        git_path = os.path.join(self.main.dir_path, ".git")
        repo = git.Repo(git_path)
        if self.remotes_combo.get() == "ALL":
            remote_names = [remote.name for remote in repo.remotes]
        else:
            remote_names = [self.remotes_combo.get()]
        for remote_name in remote_names:
            remote = repo.remote(remote_name)
            remote.push(self.local_branches_combo.get())

    def remote_fetch(self):
        if not os.path.isdir(os.path.join(self.main.dir_path, ".git")):
            return
        git_path = os.path.join(self.main.dir_path, ".git")
        repo = git.Repo(git_path)
        if self.remotes_combo.get() == "ALL":
            remote_names = [remote.name for remote in repo.remotes]
        else:
            remote_names = [self.remotes_combo.get()]
        for remote_name in remote_names:
            remote = repo.remote(remote_name)
            remote.fetch()


class GitMenu(MenuTemplate):
    NAME = "Git"

    def __init__(self, master: tk.Menu, main: "PluginManager"):
        super().__init__(master, main)
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


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x575")
    git_tab = GitTab(root, None)
    git_tab.pack()
    root.mainloop()
