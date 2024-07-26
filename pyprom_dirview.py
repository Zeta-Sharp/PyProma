import os
import re
import shutil
import subprocess
import time
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import tkinter.simpledialog
import tkinter.ttk as ttk
from textwrap import dedent
from tkinter import scrolledtext

import git
import pyperclip


class dirview:

    def __init__(self, dirpath: str = ""):
        """this constructor sets _dirpath and create GUI.

        Args:
            dirpath (str, optional): path to directory. Defaults to "".
        """
        self.dirview_window = tk.Tk()
        self.dirview_window.geometry("1000x600")
        self.dirview_window.title("Python project manager")

        self.main_menu = tk.Menu(self.dirview_window)
        self.dirview_window.config(menu=self.main_menu)

        self.file_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(
            label="Open directory",
            command=self.set_dirpath)

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

        self.dirframe = tk.Frame(self.dirview_window, width=200, height=600)
        self.dirframe.propagate(False)
        self.dirtree = ttk.Treeview(self.dirframe, show=["tree", "headings"])
        self.dirtree.heading(
            "#0",
            text="directory",
            anchor=tk.CENTER,
            command=lambda: self.open_directory(self._dirpath))
        self.dir_menu = tk.Menu(self.dirframe, tearoff=False)
        self.dir_menu.add_command(
            label="Open File",
            command=lambda: self.open_directory(self.dirtree.selection()))
        self.dir_menu.add_command(
            label="Remove",
            command=lambda: self.remove_directory(self.dirtree.selection()))
        self.dir_menu.add_command(
            label="Copy path",
            command=lambda: self.copy_path(self.dirtree.selection()))
        self.dir_menu.add_command(
            label="Copy relative path",
            command=lambda: self.copy_relative_path(self.dirtree.selection()))
        self.dirtree.bind("<Button-3>", self.dir_menu_on_right_click)
        self.dirtree.pack(fill=tk.BOTH, expand=True)
        self.dirframe.grid(row=0, column=0, sticky=tk.NSEW)

        self.tabframe = tk.Frame(self.dirview_window, width=800, height=600)
        self.tabframe.propagate(False)
        self.tabframe.grid(row=0, column=1, sticky=tk.NSEW)
        self.tab = ttk.Notebook(self.tabframe)

        self.todo_tab = tk.Frame(self.tab, width=800, height=600)
        self.todo_tab.propagate(False)
        self.todotree = ttk.Treeview(self.todo_tab, show=["tree", "headings"])
        self.todotree.heading("#0", text="ToDo", anchor=tk.CENTER)
        self.todotree.pack(fill=tk.BOTH, expand=True)
        self.tab.add(self.todo_tab, text="ToDo", padding=3)

        self.readme_tab = tk.Frame(self.tab, width=800, height=600)
        self.readme_tab.propagate(False)
        self.readmetext = scrolledtext.ScrolledText(self.readme_tab)
        text = "There is no README.md in this directory."
        self.readmetext.insert(tk.END, text)
        self.readmetext.pack(fill=tk.BOTH, expand=True)
        self.tab.add(self.readme_tab, text="README", padding="3")

        self.git_tab = tk.Frame(self.tab, width=800, height=600)
        self.git_tab.propagate(False)
        self.git_committree = ttk.Treeview(
            self.git_tab, show="headings",
            columns=("hash", "author", "date", "message"))
        self.git_committree.heading("hash", text="hash", anchor=tk.CENTER)
        self.git_committree.heading("author", text="author", anchor=tk.CENTER)
        self.git_committree.heading("date", text="date", anchor=tk.CENTER)
        self.git_committree.heading(
            "message", text="message", anchor=tk.CENTER)
        self.git_committree.pack(fill=tk.BOTH, expand=True)
        self.tab.add(self.git_tab, text="Git", padding=3)

        self.tab.pack(anchor=tk.NW)

        if os.path.isdir(dirpath):
            self._dirpath = os.path.normpath(dirpath.replace("/", "\\"))
            self.prepare_make_dirtree()
        else:
            self._dirpath = ""

        self.dirview_window.mainloop()

    def set_dirpath(self):
        """this func asks directory and sets _dirpath.
        after this func -> prepare_make_dirtree().
        """
        path = os.path.normpath(
            tkinter.filedialog.askdirectory().replace("/", "\\"))
        if os.path.isdir(path):
            self._dirpath = path
            self.prepare_make_dirtree()

    def prepare_make_dirtree(self):
        """this func initialize tree.
        after this func -> make_dirtree(dirpath), read_README(), read_git().
        """
        if os.path.isdir(self._dirpath):
            self.dirtree.delete(*self.dirtree.get_children())
            self.todotree.delete(*self.todotree.get_children())
            self.git_committree.delete(*self.git_committree.get_children())
            self.dirtree.heading(
                "#0",
                text=os.path.basename(self._dirpath),
                anchor=tk.CENTER,
                command=lambda: self.open_directory(self._dirpath))
            self.make_dirtree(self._dirpath)
            self.read_README()
            self.read_git()

    def make_dirtree(self, path: str, parenttree: str = None):
        """this func makes tree.

        Args:
            path (str): path which you want to make tree from
            parenttree (str, optional): parent tree. Defaults to None.
        """
        if os.path.exists(path):
            dirs = os.listdir(path)
            for d in dirs:
                full_path = os.path.join(path, d)
                full_path = os.path.normpath(full_path)
                if os.path.isfile(full_path):
                    self.dirtree.insert(
                        "" if parenttree is None else parenttree,
                        tk.END,
                        text=d)
                    if os.path.splitext(full_path)[1] == ".py":
                        self.find_todo(full_path)
                else:
                    child = self.dirtree.insert(
                        "" if parenttree is None else parenttree,
                        tk.END,
                        text=d)
                    self.make_dirtree(full_path, child)

    def read_README(self):
        """this func reads REAADME.md and writes on readmetext.
        """
        readme_path = os.path.join(self._dirpath, "README.md")
        if os.path.isfile(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            text = "There is no README.md in this directory."
        self.readmetext.delete("1.0", tk.END)
        self.readmetext.insert(tk.END, text)

    def git_init(self):
        if os.path.isdir(self._dirpath):
            try:
                git.Repo.init(self._dirpath)
            except git.exc.GitError as e:
                tkinter.messagebox.showerror(message=e)

    def read_git(self):
        """this func reads git commit log and makes git tree.
        """
        if os.path.isdir(git_path := os.path.join(self._dirpath, ".git")):
            repo = git.Repo(git_path)
            for commit in repo.iter_commits():
                self.git_committree.insert(
                    "",
                    tk.END,
                    values=(
                        commit.hexsha,
                        commit.author.name,
                        commit.authored_datetime,
                        commit.message))
        else:
            self.git_committree.insert(
                    "",
                    tk.END,
                    values=(
                        "this directory",
                        "is not",
                        "a git",
                        "repository"))

    def getpath(self, targetpath: str):
        """this func generates path from treeview node.

        Args:
            targetpath (string): target node

        Returns:
            string: path in tree
        """
        if targetpath:
            pathlist = []
            item_id = self.dirtree.parent(targetpath)
            while item_id:
                pathlist.insert(0, self.dirtree.item(item_id, "text"))
                item_id = self.dirtree.parent(item_id)
            path = "\\".join(pathlist)
            return path

    def find_todo(self, filename: str):
        """this func finds "# TODO" and add node to todotree.

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
                        (filename, i + 1, match.group(1).strip()))

            if len(todo_items) > 0:
                parent = self.todotree.insert(
                    "",
                    tk.END,
                    text=filename.replace(self._dirpath+"\\", ""))
                for filename, line_no, todo_text in todo_items:
                    self.todotree.insert(
                        parent,
                        tk.END,
                        text=f"(line {line_no}) {todo_text}")

    def open_directory(self, targetpath: str):
        """this func opens selected file or directory in explorer.

        Args:
            targetpath (string): target node
        """
        path = targetpath
        if path != self._dirpath:
            if path:
                path = os.path.join(
                    self._dirpath,
                    self.getpath(targetpath),
                    self.dirtree.item(targetpath, "text"))
        path = os.path.normpath(path)
        subprocess.Popen(
            ["explorer", "/root,", path] if targetpath else ["explorer"])

    def remove_directory(self, targetpath: str):
        """this func removes selected file or directory from device.

        Args:
            targetpath (string): target node
        """
        if targetpath:
            path = os.path.join(
                self._dirpath,
                self.getpath(targetpath),
                self.dirtree.item(targetpath, "text"))
            path = os.path.normpath(path)
            message = f"""\
            Remove {path} ?
            This action cannot be undone!"""
            if tkinter.messagebox.askokcancel(
                    "Confirm",
                    dedent(message)):
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path)
                self.dirtree.delete(targetpath)

    def copy_path(self, targetpath: str):
        """this func copies path.

        Args:
            targetpath (str): target node
        """
        if targetpath:
            path = os.path.join(
                self._dirpath,
                self.getpath(targetpath),
                self.dirtree.item(targetpath, "text"))
            path = os.path.normpath(path)
            pyperclip.copy(path)

    def copy_relative_path(self, targetpath: str):
        """this func copies relative path.

        Args:
            targetpath (str): target node
        """
        if targetpath:
            path = os.path.join(
                self.getpath(targetpath),
                self.dirtree.item(targetpath, "text"))
            path = os.path.normpath(path)
            pyperclip.copy(path)

    def code_runner(self, command):
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
        if os.path.isdir(self._dirpath):
            package = tkinter.simpledialog.askstring(
                "install package", "type pip package name here")
            if package:
                venv_path = os.path.join(
                    self._dirpath, r".venv\Scripts\python.exe")
                command = [
                    venv_path if os.path.isfile(venv_path) else "python",
                    "-m", "pip", "install", package]
                try:
                    self.code_runner(command)
                except subprocess.CalledProcessError as e:
                    tkinter.messagebox.showerror(message=e)
                else:
                    tkinter.messagebox.showinfo(
                        message=f"sucsessfully installed {package}")

    def pip_freeze(self):
        if os.path.isdir(self._dirpath):
            venv_path = os.path.join(
                self._dirpath, r".venv\Scripts\python.exe")
            command = [
                venv_path if os.path.isfile(venv_path) else "python",
                "-m", "pip", "freeze", ">", "requirements.txt"]
            try:
                subprocess.run(command, shell=True)
            except subprocess.CalledProcessError as e:
                tkinter.messagebox.showerror(message=e)

    def dir_menu_on_right_click(self, event: tkinter.Event):
        """this func shows right-clicked menu.

        Args:
            event (tkinter.Event): information about event
        """
        flag = len(self.dirtree.selection()) > 0
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
    window = dirview()
