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
2. Set Up Development Environment: `Run RUN_ME_FIRST.py` to configure your local environment for development.
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
from PyProma_common.PyProma_templates import tab_template
from PyProma_dir_view.plugins.plugin_manager import PyFileMethod, RefreshMethod


Class CustomTab(tab_template.TabTemplate):
    # Set the tab name (defaults to the class name if not defined)
    NAME = "Custom"

    def __init__(self, master=None, main=None):
        # master is master frame. main is main instance.
        super().__init__(master, main)

    # Method decorated by RefreshMethod will be called in refresh sequence.
    @RefreshMethod
    def refresh(self):
        pass

    # Method with this decorator will be called with path to `.py` file.
    @PyFileMethod
    def do_something(self, path):
        pass
```
#### Adding menus:
Create a Python module within these directories.  
Inherit the menu class from tkinter.  
Ensure your file name ends with `_plugin.py`, and the class name matches the filename in PascalCase (e.g., `example_plugin.py` -> `ExampleMenu`).  
```Python
from tkinter import Menu

class CustomMenu(Menu):
    # Set the menu name (defaults to the class name if not defined)
    NAME = "Custom"

    def __init__(self, master=None, main=None):
        # master is master frame. main is main instance.
        self.main = main
        super().__init__(master, tearoff=False)
        self.add_command(label="Custom Menu")
```
