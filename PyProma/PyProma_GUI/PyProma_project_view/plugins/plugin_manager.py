import importlib.util
import inspect
import json
import os
import tkinter as tk
from textwrap import dedent
from tkinter import messagebox
from typing import TYPE_CHECKING, Any

import inflection
from PyProma_common.PyProma_templates.menu_template import MenuTemplate
from PyProma_common.PyProma_templates.tab_template import TabTemplate

if TYPE_CHECKING:
    from PyProma_project_view.PyProma_project_view_script import ProjectView

json_path = "PyProma_settings.json"


class PluginManager:
    def __init__(self, main: "ProjectView"):
        """this func loads and adds tabs, menus from tabs directory.
        """
        self.tabs = {}
        self.menus = {}
        self.main = main
        self._settings = None
        self._initialize_settings()
        self._load_plugins()

    def _initialize_settings(self):
        with open(json_path, "r") as file:
            self._settings = json.load(file)

    def _load_plugins(self):
        """This method loads all plugins
        from the PyProma_project_view/plugins directory.
        It searches for files ending with "_plugin.py" and imports them.
        Each plugin should have a class
        that inherits from TabTemplate or MenuTemplate.
        """
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

    @property
    def projects(self) -> dict:
        """This property returns the projects dictionary."""
        return self.main.projects["projects"]

    def load_settings(
            self, instance, key: str, value: Any = None,
            mode: str = "get", initialize: bool = False) -> Any:
        """This method loads or saves settings for a plugin instance.

        Args:
            instance (self): instance of a plugin class.
            key (str): The key to access settings.
            value (Any, optional): Value to set. Defaults to None.
            mode (str, optional): get -> get values. \
                set -> set and save values. Defaults to "get".
            initialize (bool, optional): If True, initializes the key \
                with value if it does not exist. Defaults to False.

        Raises:
            ValueError: If the mode is not 'get' or 'set'.
            ValueError: If the instance is not a valid plugin.

        Returns:
            Union[Any, None]: Returns the value or result.
        """
        _plugins_config_key = "ProjectPlugins"
        _plugin_name = getattr(
            instance.__class__, "NAME", instance.__class__.__name__)

        if self._settings is None:
            with open(json_path, "r") as file:
                self._settings = json.load(file)
        if instance in self.tabs.values():
            if _plugins_config_key not in self._settings.keys():
                self._settings[_plugins_config_key] = {}
            if _plugin_name not in self._settings[_plugins_config_key].keys():
                self._settings[_plugins_config_key][_plugin_name] = {}
            _plugin_settings = \
                self._settings[_plugins_config_key][_plugin_name]
            if mode == "get":
                if initialize and key not in _plugin_settings:
                    _plugin_settings[key] = value
                    with open(json_path, "w") as file:
                        json.dump(
                            self._settings, file, indent=4)
                return _plugin_settings[key]
            elif mode == "set":
                self._settings[_plugins_config_key][_plugin_name][key] = value
                with open(json_path, "w") as file:
                    json.dump(
                        self._settings, file, indent=4)
                return self._settings[_plugins_config_key][_plugin_name][key]
            else:
                raise ValueError(
                    f"Invalid mode: {mode}. Use 'get' or 'set'.")
        else:
            raise ValueError(
                f"Instance {instance} is not a valid plugin. "
                "Use a plugin instance in the PluginManager.")
