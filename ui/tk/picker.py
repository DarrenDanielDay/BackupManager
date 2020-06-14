from enum import Enum
from tkinter import *
from typing import Dict, Tuple

from PIL import Image, ImageTk

from models import TargetFile, TargetFileOperation
import core.impl

project_base = 'C:/Users/Darren DanielDay/Documents/Projects/GitHubProjects/BackupManager/'
jpg = project_base + 'assets/image_icon.jpg'
svg = 'assets/folder_type_images.svg'


class Picker(Frame):
    def __init__(self, target: TargetFile, size: Tuple[int, int], *, parent = None, cnf = {}, **kw):
        super().__init__(parent, cnf=cnf, **kw)
        self.target_file = target
        image = core.impl.image_provider_impl.load(target.path)
        self.image = core.impl.image_provider_impl.fix(image, tuple(map(lambda l: l - 10, size)))
        self.image_tk = ImageTk.PhotoImage(self.image)
        self.image_label = Label(master=self,image=self.image_tk)
        self.image_label.config(width=size[0], height=size[1])
        self.image_label.bind('<Button 1>', self.on_click)
        self.image_label.grid(row=0, column=0)
        self.grid(row=0, column=0)
        self.update_state()
    
    @property
    def mode(self):
        return core.impl.config_impl.current_mode
    
    @property
    def state(self) -> TargetFileOperation:
        return self.target_file.operation

    @state.setter
    def state(self, value: TargetFileOperation):
        self.target_file.operation = value
        self.update_state()

    _state_colors: Dict[TargetFileOperation, str] = {
        TargetFileOperation.ignore: "white",
        TargetFileOperation.backup: "lightgreen",
        TargetFileOperation.delete: "#ff8080",
        TargetFileOperation.move:   "skyblue",
    }

    def update_state(self):
        operation = self.target_file.operation
        self.image_label.config(bg=self._state_colors[operation])

    def on_click(self, event: Event):
        if self.state != self.mode:
            self.state = self.mode
        else:
            self.state = core.impl.config_impl.default_operation


def main():
    root = Tk()
    root.geometry("500x500")
    Picker(TargetFile('assets/Darren Daniel Day.jpg'), (100, 200), parent=root)
    root.mainloop()
        

    