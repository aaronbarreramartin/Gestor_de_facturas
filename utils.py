import sys
from pathlib import Path
import tkinter as tk

def get_path() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent
    
def nombre_archivo(path_archivo: str) -> str:
    return Path(path_archivo).name

class AutoText(tk.Text):
    DEFAULT_CONFIG = dict(
        width=45,
        wrap="word",
        bg="#2b3e50",
        fg="white",
        insertbackground="white",
        relief="flat",
        font=('Segoe UI', 11),
        padx=6,
        pady=6,
    )

    def __init__(self, master, min_height=1, max_height=20, **kwargs):
        config = {**self.DEFAULT_CONFIG, **kwargs}
        config["height"] = min_height
        super().__init__(master, **config)

        self.min_height = min_height
        self.max_height = max_height

        self.bind("<<Modified>>", self.modificado)

    def modificado(self, event):
        if self.edit_modified():
            self.edit_modified(False)
            self.ajustar_altura()

    def ajustar_altura(self):
        lines = int(self.index("end-1c").split(".")[0])
        new_height = max(self.min_height, min(lines, self.max_height))
        self.configure(height=new_height)