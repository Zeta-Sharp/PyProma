import os
import re
import shutil
import subprocess
import time
import tkinter as tk
import tkinter.ttk as ttk
import venv
from textwrap import dedent
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
from typing import Union

import git
import pyperclip


class DirView:

    def __init__(self, project_name: str = "", dir_path: str = ""):
        """this constructor sets _dir_path and create GUI.

        Args:
            project_name (str, optional): project name. Defaults to "".
            dir_path (str, optional): path to directory. Defaults to "".
        """
        self.dir_view_window = tk.Tk()
        self.dir_view_window.geometry("1000x600")
        title = (
            "Python project manager"
            + (f" - {project_name}" if project_name else ""))
        self.dir_view_window.title(title)

        self.main_menu = tk.Menu(self.dir_view_window)
        self.dir_view_window.config(menu=self.main_menu)

        self.file_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(
            label="Open directory",
            command=self.set_dir_path)

        self.git_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="Git", menu=self.git_menu)
        self.git_menu.add_command(
            label="Git Init",
            command=self.git_init)

        self.pip_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="pip", menu=self.pip_menu)
        self.pip_menu.add_command(
            label="install package", command=self.pip_install)
        self.pip_menu.add_command(label="freeze", command=self.pip_freeze)

        self.venv_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="venv", menu=self.venv_menu)
        self.venv_menu.add_command(label="venv")

        self.help_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="Version information")

        self.dir_frame = tk.Frame(self.dir_view_window, width=200, height=600)
        self.dir_frame.propagate(False)
        self.dir_tree = ttk.Treeview(self.dir_frame, show=["tree", "headings"])
        self.dir_tree.heading(
            "#0",
            text="directory",
            anchor=tk.CENTER,
            command=lambda: self.open_directory(self._dir_path))
        self.dir_menu = tk.Menu(self.dir_frame, tearoff=False)
        self.dir_menu.add_command(
            label="Open File",
            command=lambda: self.open_directory(self.dir_tree.selection()[0]))
        self.dir_menu.add_command(
            label="Remove",
            command=lambda: self.remove_directory(self.dir_tree.selection()[0]))
        self.dir_menu.add_command(
            label="Copy path",
            command=lambda: self.copy_path(self.dir_tree.selection()[0]))
        self.dir_menu.add_command(
            label="Copy relative path",
            command=lambda: self.copy_relative_path(self.dir_tree.selection()[0]))
        self.dir_tree.bind("<Button-3>", self.dir_menu_on_right_click)
        self.dir_tree.pack(fill=tk.BOTH, expand=True)
        self.dir_frame.grid(row=0, column=0, sticky=tk.NSEW)

        self.tab_frame = tk.Frame(self.dir_view_window, width=800, height=600)
        self.tab_frame.propagate(False)
        self.tab_frame.grid(row=0, column=1, sticky=tk.NSEW)
        self.tab = ttk.Notebook(self.tab_frame)

        self.todo_tab = tk.Frame(self.tab, width=800, height=600)
        self.todo_tab.propagate(False)
        self.todo_tree = ttk.Treeview(self.todo_tab, show=["tree", "headings"])
        self.todo_tree.heading("#0", text="ToDo", anchor=tk.CENTER)
        self.todo_tree.pack(fill=tk.BOTH, expand=True)
        self.tab.add(self.todo_tab, text="ToDo", padding=3)

        self.readme_tab = tk.Frame(self.tab, width=800, height=600)
        self.readme_tab.propagate(False)
        self.readme_text = scrolledtext.ScrolledText(self.readme_tab)
        text = "There is no README.md in this directory."
        self.readme_text.insert(tk.END, text)
        self.readme_text.pack(fill=tk.BOTH, expand=True)
        self.tab.add(self.readme_tab, text="README", padding="3")

        self.git_tab = tk.Frame(self.tab, width=800, height=600)
        self.git_tab.propagate(False)
        self.git_commit_tree = ttk.Treeview(
            self.git_tab, show="headings",
            columns=("hash", "author", "date", "message"))
        self.git_commit_tree.heading("hash", text="hash", anchor=tk.CENTER)
        self.git_commit_tree.heading("author", text="author", anchor=tk.CENTER)
        self.git_commit_tree.heading("date", text="date", anchor=tk.CENTER)
        self.git_commit_tree.heading(
            "message", text="message", anchor=tk.CENTER)
        self.git_commit_tree.pack(fill=tk.BOTH, expand=True)
        self.tab.add(self.git_tab, text="Git", padding=3)

        self.tab.pack(anchor=tk.NW)

        if os.path.isdir(dir_path):
            self._dir_path = os.path.normpath(dir_path.replace("/", "\\"))
            self.refresh_trees()
        else:
            self._dir_path = ""

        self.dir_view_window.mainloop()

    def set_dir_path(self):
        """this func asks directory and sets _dir_path.
        after this func -> refresh_trees().
        """
        path = os.path.normpath(
            filedialog.askdirectory().replace("/", "\\"))
        if os.path.isdir(path):
            self._dir_path = path
            self.refresh_trees()

    def refresh_trees(self):
        """this func initialize tree.
        after this func -> make_dir_tree(dir_path), read_readme(), read_git().
        """
        if os.path.isdir(self._dir_path):
            self.dir_tree.delete(*self.dir_tree.get_children())
            self.todo_tree.delete(*self.todo_tree.get_children())
            self.git_commit_tree.delete(*self.git_commit_tree.get_children())
            self.dir_tree.heading(
                "#0",
                text=os.path.basename(self._dir_path),
                anchor=tk.CENTER,
                command=lambda: self.open_directory(self._dir_path))
            self.make_dir_tree(self._dir_path)
            self.read_readme()
            self.read_git()

    def make_dir_tree(self, path: str, parent_tree: str = None):
        """this func makes tree.

        Args:
            path (str): path which you want to make tree from
            parent_tree (str, optional): parent tree. Defaults to None.
        """
        if os.path.exists(path):
            dirs = os.listdir(path)
            for d in dirs:
                full_path = os.path.join(path, d)
                full_path = os.path.normpath(full_path)
                if os.path.isfile(full_path):
                    self.dir_tree.insert(
                        "" if parent_tree is None else parent_tree,
                        tk.END,
                        text=d)
                    if os.path.splitext(full_path)[1] == ".py":
                        self.find_todo(full_path)
                else:
                    child = self.dir_tree.insert(
                        "" if parent_tree is None else parent_tree,
                        tk.END,
                        text=d)
                    self.make_dir_tree(full_path, child)

    def read_readme(self):
        """this func reads README.md and writes on readme_text.
        """
        readme_path = os.path.join(self._dir_path, "README.md")
        if os.path.isfile(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            text = "There is no README.md in this directory."
        self.readme_text.delete("1.0", tk.END)
        self.readme_text.insert(tk.END, text)

    def git_init(self):
        if os.path.isdir(self._dir_path):
            try:
                git.Repo.init(self._dir_path)
            except git.exc.GitError as e:
                messagebox.showerror(message=str(e))

    def read_git(self):
        """this func reads git commit log and makes git tree.
        """
        if os.path.isdir(git_path := os.path.join(self._dir_path, ".git")):
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

    def getpath(self, target_path: str):
        """this func generates path from treeview node.

        Args:
            target_path (string): target node

        Returns:
            string: path in tree
        """
        if target_path:
            path_list = []
            item_id = self.dir_tree.parent(target_path)
            while item_id:
                path_list.insert(0, self.dir_tree.item(item_id, "text"))
                item_id = self.dir_tree.parent(item_id)
            path = "\\".join(path_list)
            return path

    def find_todo(self, filename: str):
        """this func finds "# TODO" and add node to todo_tree.

        Args:
            filename (string): path to .py file
        """
        if "venv" not in filename:
            with open(filename, "r", encoding="utf-8") as f:
                lines = f.readlines()
            todo_items = []
            for i, line in enumerate(lines):
                match = re.search(r"# TODO (.*)", line)
                if match:
                    todo_items.append(
                        [filename, i + 1, match.group(1).strip()])

            if len(todo_items) > 0:
                parent = self.todo_tree.insert(
                    "",
                    tk.END,
                    text=filename.replace(self._dir_path + "\\", ""))
                for filename, line_no, todo_text in todo_items:
                    self.todo_tree.insert(
                        parent,
                        tk.END,
                        text=f"(line {line_no}) {todo_text}")

    def open_directory(self, target_path: str):
        """this func opens selected file or directory in explorer.

        Args:
            target_path (string): target node
        """
        path = target_path
        if path != self._dir_path:
            if path:
                path = os.path.join(
                    self._dir_path,
                    self.getpath(target_path),
                    self.dir_tree.item(target_path, "text"))
        path = os.path.normpath(path)
        subprocess.Popen(
            ["explorer", f"/select,{path}"] if target_path else ["explorer"],
            shell=False)

    def remove_directory(self, target_path: str):
        """this func removes selected file or directory from device.

        Args:
            target_path (string): target node
        """
        if target_path:
            path = os.path.join(
                self._dir_path,
                self.getpath(target_path),
                self.dir_tree.item(target_path, "text"))
            path = os.path.normpath(path)
            message = f"""\
            Remove {path} ?
            This action cannot be undone!"""
            if messagebox.askokcancel(
                    "Confirm",
                    dedent(message)):
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path)
                self.dir_tree.delete(target_path)

    def copy_path(self, target_path: str):
        """this func copies path.

        Args:
            target_path (str): target node
        """
        if target_path:
            path = os.path.join(
                self._dir_path,
                self.getpath(target_path),
                self.dir_tree.item(target_path, "text"))
            path = os.path.normpath(path)
            pyperclip.copy(path)

    def copy_relative_path(self, target_path: str):
        """this func copies relative path.

        Args:
            target_path (str): target node
        """
        if target_path:
            path = os.path.join(
                self.getpath(target_path),
                self.dir_tree.item(target_path, "text"))
            path = os.path.normpath(path)
            pyperclip.copy(path)

    @staticmethod
    def code_runner(command: Union[str, list]):
        """this func runs bash command and shows outputs to textbox.

        Args:
            command (str): command
        """
        root = tk.Toplevel()
        root.title("code runner")
        text = tk.Text(root)
        text.pack()
        process = subprocess.Popen(
            command, shell=False,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        while True:
            output = process.stdout.readline().decode()
            if output == '':
                break
            text.insert(tk.END, output)
            text.see(tk.END)
            root.update()
            time.sleep(0.1)

        root.destroy()

    def pip_install(self):
        """this func asks pip package and installs.
        """
        if os.path.isdir(self._dir_path):
            package = simpledialog.askstring(
                "install package", "type pip package name here")
            if package:
                venv_path = os.path.join(
                    self._dir_path, r".venv\Scripts\python.exe")
                command = [
                    venv_path if os.path.isfile(venv_path) else "python",
                    "-m", "pip", "install", package]
                try:
                    self.code_runner(command)
                except subprocess.CalledProcessError as e:
                    messagebox.showerror(message=str(e))
                else:
                    messagebox.showinfo(
                        message=f"successfully installed {package}")

    def pip_freeze(self):
        """this func generates requirements.txt.
        """
        if os.path.isdir(self._dir_path):
            venv_path = os.path.join(
                self._dir_path, r".venv\Scripts\python.exe")
            command = [
                venv_path if os.path.isfile(venv_path) else "python",
                "-m", "pip", "freeze", ">", "requirements.txt"]
            try:
                subprocess.run(command, shell=True)
            except subprocess.CalledProcessError as e:
                messagebox.showerror(message=str(e))

    def venv_create(self):
        if os.path.isdir(self._dir_path):
            try:
                venv.create(self._dir_path)
            except OSError as e:
                messagebox.showerror(message=str(e))

    def dir_menu_on_right_click(self, event: tk.Event):
        """this func shows right-clicked menu.

        Args:
            event (tkinter.Event): information about event
        """
        flag = len(self.dir_tree.selection()) > 0
        self.dir_menu.entryconfig(
            "Open File",
            state=tk.NORMAL if flag else tk.DISABLED)
        self.dir_menu.entryconfig(
            "Remove",
            state=tk.NORMAL if flag else tk.DISABLED)
        self.dir_menu.entryconfig(
            "Copy path",
            state=tk.NORMAL if flag else tk.DISABLED)
        self.dir_menu.entryconfig(
            "Copy relative path",
            state=tk.NORMAL if flag else tk.DISABLED)
        self.dir_menu.post(event.x_root, event.y_root)


if __name__ == "__main__":
    window = DirView()
