import os
import subprocess
import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path
from textwrap import dedent
from tkinter import filedialog, messagebox

import pyperclip
import send2trash
from PyProma_common.show_version import ShowVersion
from PyProma_dir_view.plugins import plugin_manager

# TODO Add builder function. e.g. pyinstaller, nuitka.
# TODO Add Poetry support.


class DirView(tk.Tk):

    def __init__(self, project_name: str = "", dir_path: str = ""):
        """this constructor sets dir_path and create GUI.

        Args:
            project_name (str, optional): project name. Defaults to "".
            dir_path (str, optional): path to directory. Defaults to "".
        """
        super().__init__()
        self.geometry("1000x600")
        title = (
            "Python project manager"
            + (f" - {project_name}" if project_name else ""))
        self.title(title)

        self.dir_path = (
            os.path.normpath(dir_path.replace("\\", "/"))
            if os.path.isdir(dir_path) else "")
        self.main_menu = tk.Menu(self)
        self.config(menu=self.main_menu)
        self.file_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(
            label="Open directory", command=self.set_dir_path)
        self.help_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(
            label="Version information",
            command=lambda: ShowVersion(self))

        self.dir_frame = tk.Frame(self, width=200, height=600)
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
            label="Move to trash",
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
        self.dir_tree.bind(
            "<Double-1>",
            lambda _: (
                self.open_directory(self.dir_tree.selection()[0])
                if self.dir_tree.selection()
                else None))
        self.dir_tree.pack(fill=tk.BOTH, expand=True)
        self.dir_frame.grid(row=0, column=0, sticky=tk.NSEW)

        self.tab_frame = tk.Frame(self, width=800, height=600)
        self.tab_frame.propagate(False)
        self.tab_frame.grid(row=0, column=1, sticky=tk.NSEW)
        self.tab = ttk.Notebook(self.tab_frame)
        self.tab.enable_traversal()
        self.tab.pack(anchor=tk.NW)
        self.plugins = plugin_manager.PluginManager(self)
        self.bind("<Control-r>", lambda event: self.refresh_trees())
        self.refresh_trees()
        self.mainloop()

    def set_dir_path(self):
        """this func asks directory and sets dir_path.
        after this func -> refresh_trees().
        """
        path = os.path.normpath(
            filedialog.askdirectory().replace("\\", "/"))
        if os.path.isdir(path) and path != ".":
            self.dir_path = path
            self.refresh_trees()

    def refresh_trees(self):
        """this func initialize tree.
        after this func
        -> make_dir_tree(dir_path)
        """
        if os.path.isdir(self.dir_path):
            self.plugins.refresh_plugins()
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
            for directory in dirs:
                full_path = os.path.join(path, directory)
                full_path = os.path.normpath(full_path)
                if os.path.isfile(full_path):
                    self.dir_tree.insert(
                        "" if parent_tree is None else parent_tree,
                        tk.END,
                        text=directory)
                    if os.path.splitext(full_path)[1] == ".py":
                        self.plugins.run_pyfile_plugin(full_path)
                else:
                    child = self.dir_tree.insert(
                        "" if parent_tree is None else parent_tree,
                        tk.END,
                        text=directory)
                    self.make_dir_tree(full_path, child)

    def getpath(self, target_path: str) -> str:
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
            path = "/".join(path_list)
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
            Move {path} to trash?
            """
            if messagebox.askokcancel(
                    "Confirm",
                    dedent(message)):
                try:
                    send2trash.send2trash(path)
                except send2trash.TrashPermissionError as e:
                    messagebox.showerror(
                        title="TrashPermissionError", message=str(e))
                except OSError as e:
                    messagebox.showerror(title="OSError", message=str(e))
                finally:
                    self.refresh_trees()

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
            "Move to trash",
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
