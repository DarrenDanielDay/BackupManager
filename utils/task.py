from typing import *
import threading
import time
from enum import Enum

T = TypeVar("T")
TResult = TypeVar("TResult")

def _noop():
    pass

def _noop_t(p):
    pass

class TaskState(Enum):
    pending = 0
    running = 1
    done = 2
    failed = 3


class Task(Generic[T]):
    @staticmethod
    def all(tasks: "List[Task]") -> "Task[bool]":
        def target():
            for task in tasks:
                task.start()
            for task in tasks:
                task.blocking_await()
            return all(task.__exception is None for task in tasks)
        
        return Task(target)

    _count = 0
    def __init__(self, target: Callable[[], T], auto_start: bool = True):
        Task._count += 1
        self._id = Task._count
        self.__target = target
        self.__state = TaskState.pending
        self.__result: Optional[T] = None
        self.__exception: Optional[T] = None
        self.__handled: bool = False
        def thread_target():
            try:
                t = target()
            except BaseException as e:
                self.fail(e)
            else:
                self.done(t)
            finally:
                print(f'Task {self.task_id} thread finished.')
                
        self.__thread = threading.Thread(target=thread_target)
        if auto_start:
            self.start()

    @property
    def task_id(self) -> int:
        return self._id

    @property
    def state(self):
        return self.__state

    @property
    def finished(self):
        return self.__state == TaskState.done or self.__state == TaskState.failed

    def done(self, value: T):
        self.__state = TaskState.done
        self.__result = value
    
    def fail(self, exception: BaseException):
        self.__state = TaskState.failed
        self.__exception = exception


    def start(self) -> "Task[T]":
        if self.__state != TaskState.pending:
            return self
        self.__state = TaskState.running
        self.__thread.start()
        return self
    
    def blocking_await(self) -> T:
        if not self.finished:
            self.__thread.join()
        if self.state == TaskState.done:
            return self.__result
        elif self.state == TaskState.failed:
            raise self.__exception


    def then(self, callback: Callable[[T], TResult] = _noop_t) -> "Task[TResult]":
        self.__handled = True
        def new_target():
            return callback(self.blocking_await())

        return Task(new_target)

    def catch(self, callback: Callable[[BaseException], TResult] = _noop_t) -> "Task[Union[T, TResult]]":
        self.__handled = True
        def new_target():
            if not self.finished:
                self.__thread.join()

            if self.state == TaskState.failed:
                result = callback(self.__exception)
                return result

        return Task(new_target)
    
    def __del__(self):
        if self.state != TaskState.pending:
            self.__thread.join()
        if self.state == TaskState.failed and not self.__handled:
            print(f"Uncaught Exception in Task {self.task_id}: {self.__exception}")


        
if __name__ == "__main__":
    Task(lambda : 1).start().then(lambda p: [print(p), print(1/0)]).catch(lambda parameter_list: 0/0).then(lambda p: print(p)).catch(print).then(print)
    