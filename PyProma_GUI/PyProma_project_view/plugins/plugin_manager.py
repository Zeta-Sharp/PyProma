import importlib.util
import inspect
import os
import tkinter as tk
from functools import wraps
from textwrap import dedent
from tkinter import messagebox
from typing import TYPE_CHECKING, Any, Callable, TypeVar

import inflection
from PyProma_common.PyProma_templates.menu_template import MenuTemplate
from PyProma_common.PyProma_templates.tab_template import TabTemplate

if TYPE_CHECKING:
    from PyProma_project_view.PyProma_project_view_script import ProjectView

SelfType = TypeVar("SelfType", bound=TabTemplate)


def RefreshMethod(
        method: Callable[[SelfType], Any]) -> Callable[[SelfType], Any]:
    """This wrapper adds flag "__is_refresh_method__".
    The method wrapped by this func will be called
    when "main.refresh_trees()" was called.

    Args:
        method (Callable[[SelfType], Any]): The method you wrapped.

    Returns:
        Callable[[SelfType], Any]: The returns of your method.
    """
    setattr(method, "__is_refresh_method__", True)

    @wraps(method)
    def wrapper(self: SelfType):
        return method(self)
    return wrapper


class PluginManager:
    def __init__(self, main: "ProjectView"):
        """this func loads and adds tabs, menus from tabs directory.
        """
        self.tabs = {}
        self.menus = {}
        self.main = main
        for filename in os.listdir(os.path.dirname(__file__)):
            if not filename.endswith("_plugin.py"):
                continue
            module_name = filename[:-3]
            module_path = os.path.join(os.path.dirname(__file__), filename)
            spec = importlib.util.spec_from_file_location(
                module_name, module_path)
            if spec is None:
                message = f"""Failed to find module spec
                    for '{module_name}'
                    at '{module_path}'"""
                messagebox.showerror(
                    title="ModuleSpec Error", message=dedent(message))
                continue
            module = importlib.util.module_from_spec(spec)
            if spec.loader is None:
                message = f"""Failed to load module '{module_name}'
                    from '{module_path}'"""
                messagebox.showerror(
                    title="ModuleLoad Error", message=dedent(message))
                continue
            try:
                spec.loader.exec_module(module)
            except ImportError as e:
                message = f"Failed to import module '{module_name}': {e}"
                messagebox.showerror(title="ImportError", message=message)
                continue
            self._load_tab(module_name, module)
            self._load_menu(module_name, module)

    def _load_tab(self, module_name, module):
        tab_class_name = inflection.camelize(module_name[:-7])+"Tab"
        if hasattr(module, tab_class_name):
            tab_class = getattr(module, tab_class_name)
            if issubclass(tab_class, TabTemplate):
                tab = tab_class(self.main.tab, self)
                tab_name = getattr(tab_class, "NAME", tab_class_name)
                self.main.tab.add(tab, text=tab_name, padding=3)
                self.tabs[tab_name] = tab
            elif issubclass(tab_class, tk.Frame):
                tab = tab_class(self.main.tab)
                tab_name = getattr(tab_class, "NAME", tab_class_name)
                message = f"""\
                {tab_name} is a tkinter frame but might not a tab.
                do you want to load anyway?"""
                confirm = messagebox.askyesno(
                    title="confirm", message=dedent(message))
                if confirm:
                    self.main.tab.add(tab, text=tab_name, padding=3)
                    self.tabs[tab_name] = tab

    def _load_menu(self, module_name, module):
        menu_class_name = inflection.camelize(module_name[:-7])+"Menu"
        if hasattr(module, menu_class_name):
            menu_class = getattr(module, menu_class_name)
            if issubclass(menu_class, MenuTemplate):
                menu = menu_class(self.main.main_menu, self)
                menu_name = getattr(
                    menu_class, "NAME", menu_class_name)
                self.main.main_menu.add_cascade(label=menu_name, menu=menu)
                self.menus[menu_name] = menu

    def refresh_plugins(self):
        """This method calls all tab plugin's method wrapped by RefreshMethod.
        """
        for plugin in self.tabs.values():
            members = inspect.getmembers(plugin, predicate=inspect.ismethod)
            for name, method in members:
                if getattr(method, "__is_refresh_method__", False):
                    method()

    def __getitem__(self, key: str) -> dict:
        if key == "tab":
            return self.tabs
        elif key == "menu":
            return self.menus
        else:
            raise KeyError(f"Invalid key: {key}. Use 'tab' or 'menu'.")

    def refresh_main(self):
        """This method calls main loop's refresh method.
        """
        self.main.refresh_trees()
