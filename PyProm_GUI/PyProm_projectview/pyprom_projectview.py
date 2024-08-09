import json
import os
import shutil
import tkinter as tk
import tkinter.ttk as ttk
from calendar import monthrange
from datetime import datetime
from textwrap import dedent
from tkinter import filedialog, messagebox

import git
from cookiecutter.exceptions import CookiecutterException
from cookiecutter.main import cookiecutter

from PyProm_GUI.PyProm_dirview import pyprom_dirview

json_path = "PyProm_settings.json"

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
        self.help_menu.add_command(label="Version information")

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

        self.calendar_tab = tk.Frame(
            self.tab,
            width=800, height=600)
        self.calendar_tab.propagate(False)
        self.calender_tree = ttk.Treeview(
            self.calendar_tab,
            show="headings",
            columns=("date", "related_to", "subject", "detail"))
        self.calender_tree.heading(
            "date", text="date", anchor=tk.CENTER)
        self.calender_tree.heading(
            "related_to", text="related to", anchor=tk.CENTER)
        self.calender_tree.heading(
            "subject", text="subject", anchor=tk.CENTER)
        self.calender_tree.heading(
            "detail", text="detail", anchor=tk.CENTER)
        self.calender_tree.pack(fill=tk.BOTH, expand=True)
        self.tab.add(self.calendar_tab, text="Calendar", padding=3)
        self.calendar_menu = tk.Menu(self.calendar_tab, tearoff=False)
        self.calendar_menu.add_command(
            label="Add Schedule",
            command=self.add_schedule)
        self.calendar_menu.add_command(
            label="Remove Schedule",
            command=self.remove_schedule)
        self.calender_tree.bind(
            "<Button-3>", self.calendar_tree_on_right_click)

        self.tab.pack(anchor=tk.NW)
        self.refresh_trees()
        self.project_view_window.mainloop()

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
        pyprom_dirview.DirView(project_name, dir_path)

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

    def add_schedule(self):
        """this func adds schedule.
        """

        def save():
            date = get_date()
            project = add_schedule_combobox2.get()
            subject = add_schedule_text3.get()
            if date and project and subject:
                date = date.strftime("%Y-%m-%d")
                detail = add_schedule_text4.get()
                schedule = [date, project, subject, detail]
                projects = self.projects["schedule"]
                projects.append(schedule)
                projects = sorted(projects, key=sort_by_date, reverse=True)
                self.projects["schedule"] = projects
                with open(json_path, "w") as f:
                    json.dump(self.projects, f, indent=4)
                add_schedule_window.destroy()
                self.refresh_trees()
            else:
                return

        add_schedule_window = tk.Toplevel()
        add_schedule_window.title("Add Schedule")
        add_schedule_window.geometry("150x220")

        def update_max_day(_: tk.Event):
            year = int(year_combobox.get())
            month = int(month_combobox.get())
            max_day = monthrange(year, month)[1]
            day_combobox["values"] = tuple(range(1, max_day + 1))
            day_combobox.current(0)

        def get_date():
            year = int(year_combobox.get())
            month = int(month_combobox.get())
            day = int(day_combobox.get())
            try:
                selected_date = datetime(year, month, day)
            except ValueError:
                return
            else:
                return selected_date

        def sort_by_date(data):
            date = datetime.strptime(data[0], "%Y-%m-%d")
            return date

        add_schedule_label1 = tk.Label(
            add_schedule_window, text="date")
        add_schedule_label1.place(x=10, y=0)
        year_combobox = ttk.Combobox(
            add_schedule_window, width=4,
            values=tuple(range(2020, 2031)), state="readonly")
        year_combobox.current(0)
        year_combobox.place(x=10, y=20)
        month_combobox = ttk.Combobox(
            add_schedule_window, width=2,
            values=tuple(range(1, 13)), state="readonly")
        month_combobox.current(0)
        month_combobox.place(x=60, y=20)
        day_combobox = ttk.Combobox(
            add_schedule_window, width=2,
            values=tuple(range(1, 32)), state="readonly")
        day_combobox.current(0)
        day_combobox.place(x=100, y=20)
        year_combobox.bind("<<ComboboxSelected>>", update_max_day)
        month_combobox.bind("<<ComboboxSelected>>", update_max_day)

        add_schedule_label2 = tk.Label(
            add_schedule_window, text="project")
        add_schedule_label2.place(x=10, y=45)
        add_schedule_combobox2 = ttk.Combobox(
            add_schedule_window,
            width=5,
            state="readonly",
            values=self.projects["projects"]["project_names"])
        add_schedule_combobox2.set("None")
        add_schedule_combobox2.place(x=10, y=70)
        add_schedule_label3 = tk.Label(
            add_schedule_window, text="subject")
        add_schedule_label3.place(x=10, y=95)
        add_schedule_text3 = tk.Entry(
            add_schedule_window, width=20)
        add_schedule_text3.place(x=10, y=115)
        add_schedule_label4 = tk.Label(
            add_schedule_window, text="detail")
        add_schedule_label4.place(x=10, y=135)
        add_schedule_text4 = tk.Entry(
            add_schedule_window, width=20)
        add_schedule_text4.place(x=10, y=155)
        add_schedule_button1 = tk.Button(
            add_schedule_window,
            text="cancel",
            command=add_schedule_window.destroy)
        add_schedule_button1.place(x=10, y=185)
        add_schedule_button2 = tk.Button(
            add_schedule_window,
            text="save", command=save)
        add_schedule_button2.place(x=100, y=185)
        add_schedule_window.mainloop()

    def remove_schedule(self):
        """this func removes selected schedule.
        """
        selected_schedule = self.calender_tree.selection()[0]
        self.projects["schedule"].remove(
            list(self.calender_tree.item(selected_schedule, "values")))
        with open(json_path, "w") as f:
            json.dump(self.projects, f, indent=4)
        self.refresh_trees()

    def calendar_tree_on_right_click(self, event: tk.Event):
        """this func shows right-clicked menu.

        Args:
            event (tkinter.Event): information about event
        """
        flag = len(self.calender_tree.selection()) > 0
        self.calendar_menu.entryconfig(
            "Add Schedule",
            state=tk.NORMAL)
        self.calendar_menu.entryconfig(
            "Remove Schedule",
            state=tk.NORMAL if flag else tk.DISABLED)
        self.calendar_menu.post(event.x_root, event.y_root)

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

    def refresh_trees(self):
        """this func refresh trees.
        """
        self.project_tree.delete(*self.project_tree.get_children())
        self.calender_tree.delete(*self.calender_tree.get_children())
        for project in self.projects["projects"]["project_names"]:
            self.project_tree.insert(
                "", tk.END, text=project)
        for schedule in self.projects["schedule"]:
            self.calender_tree.insert(
                "", tk.END,
                values=schedule)


if __name__ == "__main__":
    window = ProjectView()
