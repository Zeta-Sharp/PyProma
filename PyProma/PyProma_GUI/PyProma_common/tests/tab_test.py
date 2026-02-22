import importlib
import importlib.util
import inspect
import os
import time
import tkinter as tk
import traceback

import inflection
import yaml
from PyProma_common.PyProma_templates import tab_template


class TestTab:
    def __init__(self, target: str, target_dir) -> None:
        self.target_dir = os.path.normpath(target_dir.replace("\\", "/"))
        self.root = tk.Tk()
        self.root.geometry("800x575")

        print("INFO: Loading plugin file.")
        spec = importlib.util.spec_from_file_location("module.name", target)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        print("INFO: Loading tab class.")
        module_name = os.path.basename(target)[:-3]
        tab_class_name = inflection.camelize(module_name[:-7])+"Tab"
        if hasattr(module, tab_class_name):
            tab_class = getattr(module, tab_class_name)
            if issubclass(tab_class, tab_template.TabTemplate):
                self.tab = tab_class(self.root, self)
                self.tab.pack()
                print(f"INFO: Tab class {tab_class_name} is loaded successly.")
                print(
                    f"Tab Name is {getattr(self.tab, 'NAME', tab_class_name)}")
                try:
                    metadata = yaml.safe_load(module.__doc__)
                    print("metadata:")
                    print(metadata)
                except AttributeError:
                    print("WARNING: This tab module doesn't have docstrings.")
                except yaml.YAMLError as e:
                    print(f"WARNING: Can't load metadata: {e}")
            else:
                print(
                    f"ERROR: Class {tab_class_name} ",
                    "does not inherit from class TabTemplate.")
        else:
            print(f"ERROR: Class {tab_class_name} not found in {target}")

        self.refresh_plugins()
        print("INFO: Showing GUI.")
        self.root.mainloop()

    def refresh_plugins(self):
        print("INFO: Refreshing GUI.")
        for name, method in inspect.getmembers(self.tab):
            if (
                    inspect.ismethod(method)
                    and hasattr(method, "__is_refresh_method__")
                    and method.__is_refresh_method__):
                print(f"INFO: Calling refresh method '{method.__name__}'")
                try:
                    start_time = time.time()
                    method()
                    end_time = time.time()
                    print(f"Time taken to refresh: {end_time - start_time}")
                except Exception:
                    print("ERROR: An Error occured while refreshing.")
                    traceback.print_exc()

    def refresh_main(self):
        print("INFO: The method 'refresh_main' was called.")
        self.refresh_plugins()

    @property
    def dir_path(self):
        print("INFO: The variable 'dir_path' was referenced.")
        return self.target_dir


if __name__ == "__main__":
    target_file = input("Path to your plugin file:")
    if os.path.isfile(target_file) and target_file.endswith("_plugin.py"):
        target_dir = input("Path to project directory:")
        if os.path.isdir(target_dir):
            TestTab(target_file, target_dir)
        else:
            print("ERROR: Directory not found.")
    else:
        print(
            "ERROR: File not found or Not plugin file.",
            "(Plugin file name must ends with '_plugin.py')")
