# Contribution Guide
**First of all, thank you for your desire to contribute.**  
This is a repository for better project management.  
This project's goal is making easier to manage projects.  
## Code of Conduct  
Read [CODE_OF_CONDUCT.md](https://github.com/rikeidanshi/PyProma/blob/main/CODE_OF_CONDUCT.md)  
## How to Contribute  
### Reporting bugs  
Change yourself and Submit a Pull Request. If you just have a suggestion or you don't know your change fits this repository, send Issues.  
Editing in your local environment.
1. Fork this repository.
2. Run RUN_ME_FIRST.py to set up development environment.
3. Make changes locally.
4. Submit a Pull Request with clear information and formatting guidelines.
Style Guide: This repository is under [PEP8 style guide](https://peps.python.org/pep-0008/).

### Extention Points
This project have some extention points.  
1. `PyProma_GUI/PyProma_dirview/tabs`, `PyProma_GUI/PyProma_projectview/tabs`
   To put modules in these directory, you can add tabs easily.
   Tabs are needed to inheritance `TabTemplate` abstruct class in `PyProma_GUI/PyProma_common/PyProma_templates/tab_template.py`.
   File name needed to end with `_tab.py` and class name must be pascal case of file name. (example: file name`example_tab.py` -> class name`ExampleTab`)
   '''Python
   from PyProma_common.PyProma_templates import tab_template

   Class CustomTab(tab_template.TabTemplate):
       # By setting class variable named "NAME", you can set tab's name (default to class name).
       NAME = "Custom"

       def __init__(self, master=None, main=None):
           # master is master frame. main is main instance.
           super().__init__(master, main)
   '''
