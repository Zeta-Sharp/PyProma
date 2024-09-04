import tkinter as tk
from tkinter import messagebox
import subprocess


class CodeRunner:
    @staticmethod
    def code_runner(command: str | list):
        """this func runs bash command and shows outputs to textbox.

        Args:
            command (str): command
        """
        root = tk.Toplevel()
        root.title("code runner")
        text = tk.Text(root)
        text.pack()
        try:
            process = subprocess.Popen(
                command, shell=False, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

            while True:
                output = process.stdout.readline()
                if output == "":
                    break
                text.insert(tk.END, output)
                text.see(tk.END)
        except subprocess.CalledProcessError as e:
            messagebox.showerror(
                parent=root,
                title="subprocess.CalledProcessError",
                message=str(e))
        else:
            messagebox.showinfo(parent=root, message="Command succeed.")

        root.destroy()
