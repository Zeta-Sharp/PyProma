# Welcome Contributors!
We appreciate your interest in contributing to this project, which aims to simplify project management.
## Code of Conduct  
Before diving in, please familiarize yourself with our guidelines for respectful interaction: [CODE_OF_CONDUCT.md](https://github.com/rikeidanshi/PyProma/blob/main/CODE_OF_CONDUCT.md)  
## How to Contribute  
### Reporting bugs  
1. **Fix it yourself**: If you can identify the issue and have a solution, feel free to submit a pull request (PR).
2. **Report issues**: For suggestions or bug reports without a solution, create an issue.

#### Local Development Environment Setup:
1. Fork the Repository: Create your own copy ("fork") of this repository on GitHub.
2. Set Up Development Environment: Run `RUN_ME_FIRST.py` to configure your local environment for development.
3. Make Changes: Edit the code locally according to your contributions.
4. Submit a Pull Request: Once your changes are ready, submit a PR with clear descriptions and adhere to the formatting guidelines below.

#### Style guide:
We follow the [PEP 8 style guide for Python code](https://peps.python.org/pep-0008/)

### Extensibility
This project offers extension points for customization:  
directories: `PyProma_GUI/PyProma_dirview/plugins`, `PyProma_GUI/PyProma_projectview/plugins`  
#### Adding tabs:  
Create a Python module within these directories.  
Inherit the TabTemplate class from `PyProma_GUI/PyProma_common/PyProma_templates/tab_template.py`.  
Ensure your file name ends with `_plugin.py`, and the class name matches the filename in PascalCase (e.g., `example_plugin.py` -> `ExampleTab`).  
You can define method used to refresh GUI with `RefreshMethod` decorator.  
Only in dir view, you can define method used to do something to `.py` file with `PyFileMethod` decorator. Method with this decorator will be called with path to `.py` file.  
```Python
from PyProma_common.PyProma_templates.tab_template import TabTemplate


Class CustomTab(TabTemplate):
    # Set the tab name (defaults to the class name if not defined)
    NAME = "Custom"

    def __init__(self, master=None, main=None):
        # master is master frame. main is main instance.
        super().__init__(master, main)

    # Method decorated by RefreshMethod will be called in refresh sequence.
    @TabTemplate.RefreshMethod
    def refresh(self):
        pass

    # Method with this decorator will be called with path to `.py` file.
    @TabTemplate.PyFileMethod
    def do_something(self, path):
        pass
```
#### Adding menus:
Create a Python module within these directories.  
Inherit the menu class from tkinter.  
Inherit the MenuTemplate class from `PyProma_GUI/PyProma_common/PyProma_templates/menu_template.py`.  
Ensure your file name ends with `_plugin.py`, and the class name matches the filename in PascalCase (e.g., `example_plugin.py` -> `ExampleMenu`).  
```Python
from PyProma_common.PyProma_templates.menu_template import MenuTemplate

class CustomMenu(MenuTemplate):
    # Set the menu name (defaults to the class name if not defined)
    NAME = "Custom"

    def __init__(self, master=None, main=None):
        # master is master frame. main is main instance.
        super().__init__(master, main)
        self.add_command(label="Custom Menu")
```

#### Save or load settings:
If needed, you can save and load settings by `self.main.load_settings`.  
This method takes 5 arguments.
- `instance`: This will be a key to access your settings. Please set `self`.  
- `key` (str): This is the key to value.  
- `value` (Any, Defaults to None): The value you want to set.  
- `mode` (str, Defaults to "get"): This sets mode. Choose from "get" or "set".  
- `initialize` (bool Defaults to False): If `True` and the key doesn't exist, initializes new key with `value`. This works `get` mode only.  
```Python
from PyProma_common.PyProma_templates.tab_template import TabTemplate

class CustomTab(TabTemplate):
    # Set the tab name (defaults to the class name if not defined)
    NAME = "Custom"

    def __init__(self, master=None, main=None):
        # master is master frame. main is main instance.
        super().__init__(master, main)
        settings = self.main.load_settings(self, "settings", mode="get")
```

### **Experimental** Plugin Meta Data
Please write meta data in top of your module on toml format.  
```TOML
"""
name: exampleplugin
version: "1.0.0"
author: your_name <your email address>
type: Please write Tab or Menu or both.
description: Short description of your plugin.
dependencies: write your module's dependencies.
settings: I want to open PyProma_settings.json for everyone to save settings.
"""
```

### Test
You can use `PyProma_GUI\PyProma_common\tests\tab_test.py` to test your tab.  
This is a virtual testing environment for tabs.  

We look forward to your contributions! If you have any questions or need further assistance, feel free to reach out.
