from tkinter import Variable
from typing import Callable, Any

def VariableWatcher(callback: Callable[[str, str, str], Any], callback_argc: int = 3):
    def __call__(var: str, unknown: str, mode: str) -> Any:
        args = (var, mode)[:callback_argc]
        return callback(*args)
    return __call__