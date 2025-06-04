"""
name: Calendar
version: "1.0.0"
author: rikeidanshi <rikeidanshi@duck.com>
type: Tab
description: Supports schedule management related to projects.
dependencies: null
settings: null
"""

import json
import tkinter as tk
import tkinter.ttk as ttk
from calendar import monthrange
from datetime import datetime

from PyProma_common.PyProma_templates import tab_template
from PyProma_project_view.plugins.plugin_manager import (PluginManager,
                                                         RefreshMethod)

json_path = "PyProma_settings.json"


class CalendarTab(tab_template.TabTemplate):
    NAME = "Calendar"

    def __init__(self, master: tk.Tk, main: PluginManager):
        super().__init__(master, main)
        with open(json_path) as f:
            self.projects = json.load(f)
        self.calender_tree = ttk.Treeview(
            self,
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

        self.calendar_menu = tk.Menu(self, tearoff=False)
        self.calendar_menu.add_command(
            label="Add Schedule",
            command=self.add_schedule)
        self.calendar_menu.add_command(
            label="Remove Schedule",
            command=self.remove_schedule)
        self.calender_tree.bind(
            "<Button-3>", self.calendar_tree_on_right_click)

    @RefreshMethod
    def refresh(self):
        self.calender_tree.delete(*self.calender_tree.get_children())
        for schedule in self.projects["schedule"]:
            self.calender_tree.insert(
                "", tk.END,
                values=schedule)

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
                self.main.refresh_main()
            else:
                return

        add_schedule_window = tk.Toplevel()
        add_schedule_window.title("Add Schedule")
        add_schedule_window.geometry("150x220")

        def update_max_day():
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
            values=tuple(map(str, range(2020, 2031))), state="readonly")
        year_combobox.current(0)
        year_combobox.place(x=10, y=20)
        month_combobox = ttk.Combobox(
            add_schedule_window, width=2,
            values=tuple(map(str, range(1, 13))), state="readonly")
        month_combobox.current(0)
        month_combobox.place(x=60, y=20)
        day_combobox = ttk.Combobox(
            add_schedule_window, width=2,
            values=tuple(map(str, range(1, 32))), state="readonly")
        day_combobox.current(0)
        day_combobox.place(x=100, y=20)
        year_combobox.bind(
            "<<ComboboxSelected>>", lambda event: update_max_day())
        month_combobox.bind(
            "<<ComboboxSelected>>", lambda event: update_max_day())

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
        self.main.refresh_main()

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


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x575")
    calendar_tab = CalendarTab(root, None)
    calendar_tab.pack()
    root.mainloop()
