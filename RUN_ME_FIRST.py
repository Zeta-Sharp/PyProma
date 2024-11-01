import os
import subprocess
import venv


def create_virtual_environment(package_path):
    if not os.path.isdir(os.path.join(package_path, ".venv")):
        venv.create(venv_path)
        subprocess.run(
            [os.path.join(package_path, get_venv_path()), "-m", "ensurepip"],
            cwd=package_path)


def install_poetry(package_path, install_poetry=True):
    if install_poetry:
        command = [
            os.path.join(package_path, get_venv_path()), "-m",
            "pip", "install", "poetry"
        ]
        subprocess.run(command, cwd=package_path)


def poetry_install(package_path):
    command = [
        os.path.join(package_path, get_venv_path()), "-m",
        "poetry", "install"]
    subprocess.run(command, cwd=package_path)


def add_to_site_packages(package_path):
    site_packages_dir = os.path.join(
        package_path, ".venv", "lib", "site-packages")
    pth_file_path = os.path.join(site_packages_dir, "PyProma_GUI.pth")
    with open(pth_file_path, "w") as f:
        f.write(os.path.join(package_path, "PyProma_GUI"))

def get_venv_path():
    match os.name:
        case "nt":
            return ".venv/Scripts/python.exe"
        case "posix":
            return ".venv/bin/python.exe"

if __name__ == "__main__":
    project_root = os.path.abspath(os.path.dirname(__file__))
    print(project_root)
    create_virtual_environment(project_root)
    install_poetry(project_root)
    poetry_install(project_root)
    add_to_site_packages(project_root)
