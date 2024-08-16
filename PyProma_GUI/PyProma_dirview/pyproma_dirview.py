import importlib
import os
import shutil
import subprocess
import sys
import tkinter as tk
import tkinter.ttk as ttk
import venv
from pathlib import Path
from textwrap import dedent
from tkinter import filedialog, messagebox, simpledialog

import git
import git.exc
import git.repo
import inflection
import pyperclip
import toml
from PyProma_templates import tab_template


class DirView:

    def __init__(self, project_name: str = "", dir_path: str = ""):
        """this constructor sets dir_path and create GUI.

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
            label="Git Init", command=self.git_init)

        self.pip_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="pip", menu=self.pip_menu)
        self.pip_menu.add_command(
            label="install package", command=self.pip_install)
        self.pip_menu.add_command(label="freeze", command=self.pip_freeze)

        self.venv_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="venv", menu=self.venv_menu)
        self.venv_menu.add_command(label="venv", command=self.venv_create)

        self.help_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(
            label="Version information", command=self.show_version)

        self.dir_frame = tk.Frame(self.dir_view_window, width=200, height=600)
        self.dir_frame.propagate(False)
        self.dir_tree = ttk.Treeview(self.dir_frame, show=["tree", "headings"])
        self.dir_tree.heading(
            "#0",
            text="directory",
            anchor=tk.CENTER,
            command=lambda: self.open_directory(self.dir_path))
        self.dir_menu = tk.Menu(self.dir_frame, tearoff=False)
        self.dir_menu.add_command(
            label="Open File",
            command=lambda: self.open_directory(self.dir_tree.selection()[0]))
        self.dir_menu.add_command(
            label="Remove",
            command=lambda:
                self.remove_directory(self.dir_tree.selection()[0]))
        self.dir_menu.add_command(
            label="Copy path",
            command=lambda: self.copy_path(self.dir_tree.selection()[0]))
        self.dir_menu.add_command(
            label="Copy relative path",
            command=lambda:
                self.copy_relative_path(self.dir_tree.selection()[0]))
        self.dir_tree.bind("<Button-3>", self.dir_menu_on_right_click)
        self.dir_tree.pack(fill=tk.BOTH, expand=True)
        self.dir_frame.grid(row=0, column=0, sticky=tk.NSEW)

        self.tab_frame = tk.Frame(self.dir_view_window, width=800, height=600)
        self.tab_frame.propagate(False)
        self.tab_frame.grid(row=0, column=1, sticky=tk.NSEW)
        self.tab = ttk.Notebook(self.tab_frame)
        self.tabs = {}
        self.add_tabs()
        self.tab.pack(anchor=tk.NW)

        if os.path.isdir(dir_path):
            self.dir_path = os.path.normpath(dir_path.replace("\\", "/"))
            self.refresh_trees()
        else:
            self.dir_path = ""

        self.dir_view_window.mainloop()

    def set_dir_path(self):
        """this func asks directory and sets dir_path.
        after this func -> refresh_trees().
        """
        path = os.path.normpath(
            filedialog.askdirectory().replace("\\", "/"))
        if os.path.isdir(path) and path != ".":
            self.dir_path = path
            self.refresh_trees()

    def add_tabs(self):
        """this func loads and adds tabs from tabs directory.
        """
        for filename in os.listdir("PyProma_GUI/PyProma_dirview/tabs"):
            if filename.endswith(".py"):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f"tabs.{module_name}")
                except ImportError as e:
                    message = f"Failed to import module '{module_name}': {e}"
                    messagebox.showerror(title="ImportError", message=message)
                    continue
                class_name = inflection.camelize(module_name)
                try:
                    class_ = getattr(module, class_name)
                    if issubclass(class_, tab_template.TabTemplate):
                        tab = class_(self.tab, self)
                        tab_name = getattr(class_, "NAME", class_name)
                        self.tab.add(tab, text=tab_name, padding=3)
                        self.tabs[tab_name] = tab
                    elif issubclass(class_, tk.Frame):
                        tab = class_(self.tab)
                        tab_name = getattr(class_, "NAME", class_name)
                        message = f"""\
                        {tab_name} is a tkinter frame but might not a tab.
                        do you want to load anyway?"""
                        confirm = messagebox.askyesno(
                            title="confirm", message=dedent(message))
                        if confirm:
                            self.tab.add(tab, text=tab_name, padding=3)
                            self.tabs[tab_name] = tab

                except AttributeError as e:
                    message = (
                        f"class {class_name} is not in module {module_name}"
                        f": {e}")
                    messagebox.showerror(
                        title="AttributeError",
                        message=message)

    def refresh_trees(self):
        """this func initialize tree.
        after this func
        -> make_dir_tree(dir_path)
        """
        if os.path.isdir(self.dir_path):
            for instance in self.tabs.values():
                instance.refresh()
            self.dir_tree.delete(*self.dir_tree.get_children())
            self.dir_tree.heading(
                "#0",
                text=os.path.basename(self.dir_path),
                anchor=tk.CENTER,
                command=lambda: self.open_directory(self.dir_path))
            self.make_dir_tree(self.dir_path)

    def make_dir_tree(self, path: str, parent_tree: str = None):
        """this func makes directory tree.

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
                        self.tabs["ToDo"].find_todo(full_path)
                else:
                    child = self.dir_tree.insert(
                        "" if parent_tree is None else parent_tree,
                        tk.END,
                        text=d)
                    self.make_dir_tree(full_path, child)

    def show_version(self):
        """This func shows version information.
        """
        version_window = tk.Toplevel(self.dir_view_window)
        version_window.title("version information")
        toml_file = "pyproject.toml"
        with open(toml_file, "r") as f:
            config = toml.load(f)
        app_version = config["tool"]["poetry"]["version"]
        version_text = f"""\
        Tkinter: {tk.TkVersion}
        Python: {sys.version}
        application: {app_version}"""
        version_label = tk.Label(version_window, text=dedent(version_text))
        version_label.pack()
        version_window.mainloop()

    def git_init(self):
        """this func runs git init
        """
        if os.path.isdir(self.dir_path):
            git_path = os.path.join(self.dir_path, ".git")
            if not os.path.isdir(git_path):
                try:
                    git.Repo.init(self.dir_path)
                except git.exc.GitError as e:
                    messagebox.showerror(
                        title="git.exc.GitError", message=str(e))

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

    def open_directory(self, target_path: str):
        """this func opens selected file or directory in explorer.

        Args:
            target_path (string): target node
        """
        path = target_path
        if path != self.dir_path:
            if path:
                path = os.path.join(
                    self.dir_path,
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
                self.dir_path,
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
                self.dir_path,
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
    def code_runner(command: str | list):
        """this func runs bash command and shows outputs to textbox.

        Args:
            command (str): command
        """
        root = tk.Toplevel()
        root.title("code runner")
        text = tk.Text(root)
        text.pack()
        try:
            process = subprocess.Popen(
                command, shell=False, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            while True:
                output = process.stdout.readline()
                if output == "":
                    break
                text.insert(tk.END, output)
                text.see(tk.END)
        except subprocess.CalledProcessError as e:
            messagebox.showerror(
                parent=root,
                title="subprocess.CalledProcessError",
                message=str(e))
        else:
            messagebox.showinfo(parent=root, message="Command succeed.")

        root.destroy()

    def pip_install(self):
        """this func asks pip package and installs.
        """
        if os.path.isdir(self.dir_path):
            package = simpledialog.askstring(
                "install package", "type pip package name here")
            if package:
                venv_path = os.path.join(
                    self.dir_path, r".venv\Scripts\python.exe")
                command = [
                    venv_path if os.path.isfile(venv_path) else "python",
                    "-m", "pip", "install", package]
                self.code_runner(command)

    def pip_freeze(self):
        """this func generates requirements.txt.
        """
        if os.path.isdir(self.dir_path):
            venv_path = os.path.join(
                self.dir_path, r".venv\Scripts\python.exe")
            command = [
                venv_path if os.path.isfile(venv_path) else "python",
                "-m", "pip", "freeze", ">", "requirements.txt"]
            try:
                subprocess.run(command, shell=True)
            except subprocess.CalledProcessError as e:
                messagebox.showerror(
                    title="subprocess.CalledProcessError", message=str(e))

    def venv_create(self):
        """this func creates .venv environment.
        """
        if os.path.isdir(self.dir_path):
            try:
                venv_path = os.path.join(self.dir_path, ".venv")
                venv.create(venv_path)
            except OSError as e:
                messagebox.showerror(
                    title="OSError", message=str(e))
            self.refresh_trees()

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
    script_path = Path(__file__).resolve().parent.parent.parent
    os.chdir(script_path)
    window = DirView()
