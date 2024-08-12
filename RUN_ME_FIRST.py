import os
import subprocess
import venv


def create_virtual_environment(package_path):
    if not os.path.isdir(venv_path := os.path.join(package_path, ".venv")):
        venv.create(venv_path)


def install_poetry(package_path, install_poetry=True):
    if install_poetry:
        command = [
            os.path.join(package_path, ".venv/Scripts/python"), "-m",
            "pip", "install", "poetry"
        ]
        subprocess.run(command)


def poetry_install(package_path):
    command = [
        os.path.join(package_path, ".venv/Scripts/python"), "-m",
        "poetry", "install"]
    subprocess.run(command)


def add_to_site_packages(package_path):
    site_packages_dir = os.path.join(
        package_path, ".venv", "lib", "site-packages")
    pth_file_path = os.path.join(site_packages_dir, "PyProma_GUI.pth")
    with open(pth_file_path, "w") as f:
        f.write(os.path.join(package_path, "PyProma_GUI"))


if __name__ == "__main__":
    project_root = os.path.abspath(os.path.dirname(__file__))
    print(project_root)
    create_virtual_environment(project_root)
    install_poetry(project_root)
    poetry_install(project_root)
    add_to_site_packages(project_root)
