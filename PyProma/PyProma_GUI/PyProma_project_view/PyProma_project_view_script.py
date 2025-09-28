import json
import os
import shutil
import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path
from textwrap import dedent
from tkinter import filedialog, messagebox

import git
import git.exc
from cookiecutter.exceptions import CookiecutterException
from cookiecutter.main import cookiecutter
from PyProma.PyProma_GUI.PyProma_common.show_version import ShowVersion
from PyProma.PyProma_GUI.PyProma_dir_view import PyProma_dir_view_script
from PyProma.PyProma_GUI.PyProma_project_view.plugins import plugin_manager

json_path = "PyProma_settings.json"

json_template = {
    "projects": {
        "project_names": [],
        "dir_paths": []
    },
    "schedule": []
}


class ProjectView(tk.Tk):

    def __init__(self):
        if not os.path.isfile(json_path):
            with open(json_path, "w") as f:
                json.dump(json_template, f, indent=4)
        with open(json_path) as f:
            self.projects = json.load(f)

        super().__init__()
        self.title("Python project manager")
        self.geometry("1000x600")
        self.main_menu = tk.Menu(self)
        self.config(menu=self.main_menu)
        self.project_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="Projects", menu=self.project_menu)
        self.project_menu.add_command(
            label="Add Project", command=self.add_project)
        self.help_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(
            label="Version information",
            command=lambda: ShowVersion(self))

        self.project_view_frame = tk.Frame(
            self, width=200, height=600)
        self.propagate(False)
        self.project_tree = ttk.Treeview(
            self.project_view_frame, show=["tree", "headings"])
        self.project_tree.heading(
            "#0", text="Projects", anchor=tk.CENTER)
        self.project_tree.pack(fill=tk.BOTH, expand=True)
        self.project_view_frame.grid(row=0, column=0, sticky=tk.NSEW)
        self.project_tree_menu = tk.Menu(
            self.project_view_frame, tearoff=False)
        self.project_tree_menu.add_command(
            label="Add Project", command=self.add_project)
        self.project_tree_menu.add_command(
            label="Open Project", command=self.open_project)
        self.project_tree_menu.add_command(
            label="Remove Project", command=self.remove_project)
        self.project_tree.bind(
            "<Button-3>", self.project_tree_on_right_click)
        self.project_tree.bind(
            "<Double-1>", self.open_project)

        self.tab_frame = tk.Frame(
            self, width=800, height=600)
        self.tab_frame.propagate(False)
        self.tab_frame.grid(row=0, column=1, sticky=tk.NSEW)
        self.tab = ttk.Notebook(self.tab_frame)
        self.tab.pack(anchor=tk.NW)
        self.tab.enable_traversal()
        self.plugins = plugin_manager.PluginManager(self)
        self.bind("<Control-r>", lambda event: self.refresh_trees())
        self.refresh_trees()
        self.mainloop()

    def refresh_trees(self):
        """this func refresh trees.
        """
        self.project_tree.delete(*self.project_tree.get_children())
        for project in self.projects["projects"]["project_names"]:
            self.project_tree.insert(
                "", tk.END, text=project)
        self.plugins.refresh_plugins()

    def add_project(self):
        """This func makes add_project_window.
        """
        AddProjectWindow(self, self.projects)

    def open_project(self, _=None):
        """this func opens selected project_view.
        """
        if self.project_tree.selection():
            selected_project = self.project_tree.selection()[0]
            index = self.projects["projects"]["project_names"].index(
                self.project_tree.item(selected_project, "text"))
            project_name = self.projects["projects"]["project_names"][index]
            dir_path = self.projects["projects"]["dir_paths"][index]
            self.destroy()
            PyProma_dir_view_script.DirView(project_name, dir_path)

    def remove_project(self):
        """this func removes selected project.
        """
        selected_project = self.project_tree.selection()[0]
        index = self.projects["projects"]["project_names"].index(
            self.project_tree.item(selected_project, "text"))
        self.projects["projects"]["project_names"].pop(index)
        self.projects["projects"]["dir_paths"].pop(index)
        with open(json_path, "w") as f:
            json.dump(self.projects, f, indent=4)
        self.refresh_trees()

    def project_tree_on_right_click(self, event: tk.Event):
        """this func shows right-clicked menu.

        Args:
            event (tkinter.Event): information about event
        """
        flag = len(self.project_tree.selection()) > 0
        self.project_tree_menu.entryconfig(
            "Add Project")
        self.project_tree_menu.entryconfig(
            "Open Project",
            state=tk.NORMAL if flag else tk.DISABLED)
        self.project_tree_menu.entryconfig(
            "Remove Project",
            state=tk.NORMAL if flag else tk.DISABLED)
        self.project_tree_menu.post(event.x_root, event.y_root)


class AddProjectWindow(tk.Toplevel):
    """This func makes add_project_window.
    """

    def __init__(self, parent, projects):
        super().__init__(master=parent)
        self.parent, self.projects = parent, projects
        self.title("Add project")
        self.geometry("300x175")
        self.grab_set()
        options = [
            "Add from directory",
            "Clone GitHub repository",
            "Use CookieCutter template"]
        self.add_project_combobox1 = ttk.Combobox(
            self, state="readonly",
            values=options)
        self.add_project_combobox1.set("Add from directory")
        self.add_project_combobox1.bind(
            "<<ComboboxSelected>>", self._switch_frame)
        self.add_project_combobox1.place(x=10, y=5)
        self.directory_frame = tk.Frame(
            self, width=300, height=60)
        self.directory_frame.propagate(False)
        self.label1 = tk.Label(self.directory_frame, text="project_name:")
        self.label1.place(x=10, y=10)
        self.txt1 = tk.Entry(self.directory_frame, width=32)
        self.txt1.place(x=87, y=10)
        self.label2 = tk.Label(self.directory_frame, text="path:")
        self.label2.place(x=10, y=30)
        self.sv = tk.StringVar()
        self.txt2 = tk.Entry(
            self.directory_frame, width=40, textvariable=self.sv)
        self.txt2.place(x=40, y=30)
        self.directory_frame.place(x=0, y=25)
        self.btn1 = tk.Button(
            self,
            text="View in Explorer",
            command=self._insert_path)
        self.btn1.place(x=40, y=85)
        self.btn2 = tk.Button(
            self,
            text="cancel",
            command=self.destroy)
        self.btn2.place(x=150, y=85)
        self.btn3 = tk.Button(
            self, text="save", command=self._save)
        self.btn3.place(x=200, y=85)

        self.clone_git_repository_frame = tk.Frame(
            self, width=300, height=90)
        self.clone_git_repository_frame.propagate(False)
        self.git_label1 = tk.Label(
            self.clone_git_repository_frame, text="URL to GitHub repository:")
        self.git_label1.place(x=0, y=0)
        self.git_txt1 = tk.Entry(self.clone_git_repository_frame, width=40)
        self.git_txt1.place(x=40, y=20)
        self.clone_git_repository_frame.place(x=0, y=120)
        self.clone_git_repository_frame.place_forget()

        self.cookiecutter_template_frame = tk.Frame(
            self, width=600, height=360)
        self.cookiecutter_template_frame.propagate(False)
        self.cookiecutter_label1 = tk.Label(
            self.cookiecutter_template_frame,
            text="URL to GitHub template repository or template file:")
        self.cookiecutter_label1.place(x=0, y=0)
        self.cookiecutter_txt1 = tk.Entry(
            self.cookiecutter_template_frame, width=40)
        self.cookiecutter_txt1.place(x=40, y=20)
        self.cookiecutter_template_frame.place(x=0, y=120)
        self.cookiecutter_template_frame.place_forget()
        self.mainloop()

    def _insert_path(self):
        path = filedialog.askdirectory(parent=self)
        if path:
            self.sv.set(path)

    def _save(self):
        if not self.txt1.get() or not self.txt2.get():
            return
        target_dir = os.path.normpath(self.txt2.get().replace("\\", "/"))
        combobox_state = self.add_project_combobox1.get()
        if not os.path.isdir(target_dir):
            message = f"""\
                The directory {target_dir} does not exist.
                Make directory and start new project?
                """
            if messagebox.askokcancel(
                    parent=self,
                    message=dedent(message)):
                try:
                    os.mkdir(target_dir)
                except OSError as e:
                    messagebox.showerror(
                        parent=self, message=str(e))
                    return
            else:
                return
        elif combobox_state != "Add from directory":
            if len(os.listdir(target_dir)) > 0:
                message = f"""\
                    The directory {target_dir} is not empty.
                    clear directory and start new project?
                    """
                if messagebox.askokcancel(
                        parent=self,
                        message=dedent(message)):
                    shutil.rmtree(target_dir)
                    os.mkdir(target_dir)
                else:
                    return
        match combobox_state:
            case "Add from directory":
                pass
            case "Clone GitHub repository":
                if not self.git_txt1.get():
                    return
                git_url = self.git_txt1.get()
                try:
                    git.Repo.clone_from(git_url, target_dir)
                except git.exc.GitError as e:
                    messagebox.showerror(
                        parent=self, message=str(e))
                    return
            case "Use CookieCutter template":
                if not self.cookiecutter_txt1.get():
                    return
                cookiecutter_url = self.cookiecutter_txt1.get()
                try:
                    cookiecutter(
                        cookiecutter_url,
                        output_dir=target_dir,
                        skip_if_file_exists=True)
                except CookiecutterException as e:
                    messagebox.showerror(
                        parent=self, message=str(e))
                    return
            case _:
                return
        self.projects["projects"]["project_names"].append(self.txt1.get())
        self.projects["projects"]["dir_paths"].append(target_dir)
        with open(json_path, "w") as f:
            json.dump(self.projects, f, indent=4)
        self.destroy()
        self.parent.refresh_trees()

    def _switch_frame(self, _: tk.Event):
        combobox_state = self.add_project_combobox1.get()
        match combobox_state:
            case "Add from directory":
                self.clone_git_repository_frame.place_forget()
                self.cookiecutter_template_frame.place_forget()
            case "Clone GitHub repository":
                self.clone_git_repository_frame.place(x=0, y=120)
                self.cookiecutter_template_frame.place_forget()
            case "Use CookieCutter template":
                self.clone_git_repository_frame.place_forget()
                self.cookiecutter_template_frame.place(x=0, y=120)


if __name__ == "__main__":
    script_path = Path(__file__).resolve().parent.parent.parent
    os.chdir(script_path)
    window = ProjectView()
