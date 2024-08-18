import importlib
import json
import os
import shutil
import sys
import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path
from textwrap import dedent
from tkinter import filedialog, messagebox

import git
import inflection
import toml
from cookiecutter.exceptions import CookiecutterException
from cookiecutter.main import cookiecutter
from PyProma_dirview import pyproma_dirview
from PyProma_templates import tab_template

json_path = "PyProma_settings.json"

json_template = {
    "projects": {
        "project_names": [],
        "dir_paths": []
    },
    "schedule": []
}


class ProjectView:

    def __init__(self):
        if not os.path.isfile(json_path):
            with open(json_path, "w") as f:
                json.dump(json_template, f, indent=4)
        with open(json_path) as f:
            self.projects = json.load(f)

        self.project_view_window = tk.Tk()
        self.project_view_window.title("Python project manager")
        self.project_view_window.geometry("1000x600")
        self.main_menu = tk.Menu(self.project_view_window)
        self.project_view_window.config(menu=self.main_menu)
        self.project_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="Projects", menu=self.project_menu)
        self.project_menu.add_command(
            label="Add Project", command=self.add_project)
        self.help_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(
            label="Version information", command=self.show_version)

        self.project_view_frame = tk.Frame(
            self.project_view_window,
            width=200, height=600)
        self.project_view_window.propagate(False)
        self.project_tree = ttk.Treeview(
            self.project_view_frame,
            show=["tree", "headings"])
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

        self.tab_frame = tk.Frame(
            self.project_view_window, width=800, height=600)
        self.tab_frame.propagate(False)
        self.tab_frame.grid(row=0, column=1, sticky=tk.NSEW)
        self.tab = ttk.Notebook(self.tab_frame)
        self.tabs = {}
        self.add_tabs()
        self.tab.pack(anchor=tk.NW)
        self.refresh_trees()
        self.project_view_window.mainloop()

    def add_tabs(self):
        """this func loads and adds tabs from tabs directory.
        """
        for filename in os.listdir("PyProma_GUI/PyProma_projectview/tabs"):
            if filename.endswith("_tab.py"):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f"tabs.{module_name}")
                except ImportError as e:
                    message = f"Failed to import module '{module_name}': {e}"
                    messagebox.showerror(title="ImportError", message=message)
                    continue
                class_name = inflection.camelize(module_name)
                try:
                    tab_class = getattr(module, class_name)
                    if issubclass(tab_class, tab_template.TabTemplate):
                        tab = tab_class(self.tab, self)
                        tab_name = getattr(tab_class, "NAME", class_name)
                        self.tab.add(tab, text=tab_name, padding=3)
                        self.tabs[tab_name] = tab
                    elif issubclass(tab_class, tk.Frame):
                        tab = tab_class(self.tab)
                        tab_name = getattr(tab_class, "NAME", class_name)
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
                        title="AttributeError", message=message)

    def refresh_trees(self):
        """this func refresh trees.
        """
        self.project_tree.delete(*self.project_tree.get_children())
        for project in self.projects["projects"]["project_names"]:
            self.project_tree.insert(
                "", tk.END, text=project)
        for instance in self.tabs.values():
            instance.refresh()

    def show_version(self):
        """This func shows version information.
        """
        version_window = tk.Toplevel(self.project_view_window)
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

    def add_project(self):
        """This func makes add_project_window.
        """
        add_project_window = tk.Toplevel()
        add_project_window.title("Add project")
        add_project_window.geometry("300x175")

        def insert_path():
            path = filedialog.askdirectory(parent=add_project_window)
            if path:
                sv.set(path)

        def save():
            if txt1.get() and (target_dir := txt2.get()):
                combobox_state = add_project_combobox1.get()
                if not os.path.isdir(target_dir):
                    message = f"""\
                        The directory {target_dir} not exist.
                        Make directory and Start Project?
                        """
                    if messagebox.askokcancel(
                            parent=add_project_window,
                            message=dedent(message)):
                        try:
                            os.mkdir(target_dir)
                        except OSError as e:
                            messagebox.showerror(
                                parent=add_project_window, message=str(e))
                            return
                    else:
                        return
                elif combobox_state != "Add from directory":
                    if len(os.listdir(target_dir)) > 0:
                        message = f"""\
                            The directory {target_dir} is not empty.
                            clear directory and Start Project?
                            """
                        if messagebox.askokcancel(
                                parent=add_project_window,
                                message=dedent(message)):
                            shutil.rmtree(target_dir)
                            os.mkdir(target_dir)
                        else:
                            return
                if combobox_state == "Clone github repository":
                    if git_url := git_txt1.get():
                        try:
                            git.Repo.clone_from(git_url, target_dir)
                        except git.exc.GitError as e:
                            messagebox.showerror(
                                parent=add_project_window, message=str(e))
                            return
                    else:
                        return
                elif combobox_state == "Use CookieCutter template":
                    if cookiecutter_url := cookiecutter_txt1.get():
                        try:
                            cookiecutter(
                                cookiecutter_url,
                                output_dir=target_dir,
                                skip_if_file_exists=True)
                        except CookiecutterException as e:
                            messagebox.showerror(
                                parent=add_project_window, message=str(e))
                            return
                    else:
                        return
                self.projects["projects"]["project_names"].append(txt1.get())
                self.projects["projects"]["dir_paths"].append(target_dir)
                with open(json_path, "w") as f:
                    json.dump(self.projects, f, indent=4)
                add_project_window.destroy()
                self.refresh_trees()

        def switch_frame(_: tk.Event):
            combobox_state = add_project_combobox1.get()
            if combobox_state == "Add from directory":
                clone_git_repository_frame.place_forget()
                cookiecutter_template_frame.place_forget()
            elif combobox_state == "Clone github repository":
                clone_git_repository_frame.place(x=0, y=120)
                cookiecutter_template_frame.place_forget()
            elif combobox_state == "Use CookieCutter template":
                clone_git_repository_frame.place_forget()
                cookiecutter_template_frame.place(x=0, y=120)

        values = [
            "Add from directory",
            "Clone github repository",
            "Use CookieCutter template"]
        add_project_combobox1 = ttk.Combobox(
            add_project_window, state="readonly",
            values=values)
        add_project_combobox1.set("Add from directory")
        add_project_combobox1.bind("<<ComboboxSelected>>", switch_frame)
        add_project_combobox1.place(x=10, y=5)
        directory_frame = tk.Frame(
            add_project_window, width=300, height=60)
        directory_frame.propagate(False)
        label1 = tk.Label(directory_frame, text="project_name:")
        label1.place(x=10, y=10)
        txt1 = tk.Entry(directory_frame, width=32)
        txt1.place(x=87, y=10)
        label2 = tk.Label(directory_frame, text="path:")
        label2.place(x=10, y=30)
        sv = tk.StringVar()
        txt2 = tk.Entry(directory_frame, width=40, textvariable=sv)
        txt2.place(x=40, y=30)
        directory_frame.place(x=0, y=25)
        btn1 = tk.Button(
            add_project_window,
            text="View in Explorer",
            command=insert_path)
        btn1.place(x=40, y=85)
        btn2 = tk.Button(
            add_project_window,
            text="cancel",
            command=add_project_window.destroy)
        btn2.place(x=150, y=85)
        btn3 = tk.Button(
            add_project_window,
            text="save",
            command=save)
        btn3.place(x=200, y=85)

        clone_git_repository_frame = tk.Frame(
            add_project_window, width=300, height=90)
        clone_git_repository_frame.propagate(False)
        git_label1 = tk.Label(
            clone_git_repository_frame, text="URL to github repository:")
        git_label1.place(x=0, y=0)
        git_txt1 = tk.Entry(clone_git_repository_frame, width=40)
        git_txt1.place(x=40, y=20)
        clone_git_repository_frame.place(x=0, y=120)
        clone_git_repository_frame.place_forget()

        cookiecutter_template_frame = tk.Frame(
            add_project_window, width=600, height=360)
        cookiecutter_template_frame.propagate(False)
        cookiecutter_label1 = tk.Label(
            cookiecutter_template_frame,
            text="URL to github template repository or template file:")
        cookiecutter_label1.place(x=0, y=0)
        cookiecutter_txt1 = tk.Entry(cookiecutter_template_frame, width=40)
        cookiecutter_txt1.place(x=40, y=20)
        cookiecutter_template_frame.place(x=0, y=120)
        cookiecutter_template_frame.place_forget()

        add_project_window.mainloop()

    def open_project(self):
        """this func opens selected project_view.
        """
        selected_project = self.project_tree.selection()[0]
        index = self.projects["projects"]["project_names"].index(
            self.project_tree.item(selected_project, "text"))
        project_name = self.projects["projects"]["project_names"][index]
        dir_path = self.projects["projects"]["dir_paths"][index]
        self.project_view_window.destroy()
        pyproma_dirview.DirView(project_name, dir_path)

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


if __name__ == "__main__":
    script_path = Path(__file__).resolve().parent.parent.parent
    os.chdir(script_path)
    window = ProjectView()
