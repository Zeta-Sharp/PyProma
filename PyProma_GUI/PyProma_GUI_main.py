import os
from pathlib import Path

from PyProma_projectview import pyproma_projectview

if __name__ == "__main__":
    script_path = Path(__file__).resolve().parent.parent
    os.chdir(script_path)
    pyproma_projectview.ProjectView()
