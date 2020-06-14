from tkinter import *
from typing import *

from models import TargetFile, TargetFileOperation
import core.impl
from ui.tk.picker import Picker
from ui.tk.variable_watcher import VariableWatcher

class SelectPanel(Frame):
    def __init__(self, targets: List[TargetFile], shape: Tuple[int, int], *, parent = None, cnf = {}, **kw):
        super().__init__(master=parent, cnf=cnf, **kw)
        self.mode_radios: List[Radiobutton] = []
        self.pickers: List[Picker] = []
        self.mode_int_var = IntVar(master=self)
        self.mode_int_var.set(core.impl.config_impl.current_mode.value)
        if all(target.operation == TargetFileOperation.ignore for target in targets):
            for target in targets:
                target.operation = core.impl.config_impl.default_operation
        self.targets = targets
        for k, v in TargetFileOperation.__members__.items():
            self.mode_radios.append(
                Radiobutton(
                    master=self,
                    variable=self.mode_int_var,
                    value=v.value, 
                    text=TargetFileOperation.display_of(v)
                )
            )
        self.shape = shape
        self.setup_grid_layout()
        self.mode_int_var.trace("w", VariableWatcher(self.on_var_changed, 0))


    def setup_grid_layout(self):
        index = 0
        size = (core.impl.config_impl.grid_width, core.impl.config_impl.grid_height)
        y, x = self.shape
        for row in range(y):
            enough = False
            for column in range(x):
                if index < len(self.targets):
                    target_file = self.targets[index]
                    picker = Picker(target_file, size, parent=self)
                    self.pickers.append(picker)
                    picker.grid(row=row, column=column)
                    index += 1
                else:
                    break
            else:
                enough = True
            if not enough:
                row += 1
                break
        else:
            row += 1
        for i in range(len(self.mode_radios)):
            self.mode_radios[i].grid(row=row, column=i)

    def on_var_changed(self):
        self.mode = TargetFileOperation.from_int(self.mode_int_var.get())
    
    @property
    def mode(self) -> TargetFileOperation:
        return core.impl.config_impl.current_mode
    
    @mode.setter
    def mode(self, value: TargetFileOperation):
        core.impl.config_impl.current_mode = value
        self.mode_int_var.set(self.mode.value)