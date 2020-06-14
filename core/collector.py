import os
from typing import *
from pathlib import *

from core.interfaces import *
from models import *

def _no_filter(p):
    return True

class Collector:
    def __init__(self):
        self.__pool: List[Path] = []

    @property
    def pool(self) -> List[Path]:
        return self.__pool

    def collect_all(self, folder: Path, where: Callable[[Path], bool] = _no_filter) -> List[Path]:
        targets = []
        if not folder.is_dir():
            print(f"{folder} is not a directory")
            return targets
        return [*self.path_generator(folder, where)]

    def path_generator(self, folder: Path, where: Callable[[Path], bool]) -> Generator[Path, Any, None]:
        for path, dirnames, filenames in os.walk(str(folder)):
            yield from filter(where, map(lambda filename: Path(path) / filename, filenames))
            # equivalent to:
            # for filename in filenames:
            #     file = Path(path) / filename
            #     if where(file):
            #         yield file

    def sliced_generator(self, folder: Path, where: Callable[[Path], bool] = _no_filter) -> Generator[List[Path], int, None]:
        gene = self.path_generator(folder, where)
        max_length = yield
        while True:
            try:
                result = []
                for i in range(max_length):
                    path = next(gene)
                    result.append(path)
            except StopIteration:
                break
            else:
                max_length = yield result
        yield result
    
    def add(self, file: Path):
        self.__pool.append(file)

    def add_range(self, files: Iterable[Path]):
        for file in files: self.add(file)

    