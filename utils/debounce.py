from typing import *
from utils.task import _noop, Task, TaskState

class Debounce:
    def __init__(self, target: Callable[[], Any], on_debounce: Callable[[], Any] = _noop):
        self.__target = target
        self.__task: Optional[Task] = None
        self.__on_debounce: Callable[[], Any] = on_debounce

    def _invoke(self):
        self.__task = Task(self.__target)

    def __call__(self):
        if self.__task is None:
            return self._invoke()
        else:
            if self.__task.finished:
                self._invoke()
            else:
                self.__on_debounce()

def debounce(target: Callable[[], Any], on_debounce: Callable[[], Any] = _noop):
    task = Task(target, auto_start=False)
    def debounced_function():
        nonlocal task
        if task.state == TaskState.pending:
            task.start()
        elif task.finished:
            task = Task(target)
        else:
            on_debounce()
    
    return debounced_function