from abc import abstractmethod
from typing import *
from pathlib import Path

from PIL import Image

from utils.task import Task
from models.target_file import TargetFile, TargetFileOperation


class KeyProvider:
    @abstractmethod
    def provide(self, byte_arr: bytes) -> str: ...


class Configuration:
    @abstractmethod
    def save(self, *args, **kw) -> Any: ...

    search_paths: List[Path] = ...
    target_path: Path = ...
    current_mode: TargetFileOperation = ...
    default_operation: TargetFileOperation = ...
    grid_height: int = ...
    grid_width: int = ...
    db_file: Optional[Path] = ...
    x_count: int = ...
    y_count: int = ...

class Saver:
    @abstractmethod
    def save(self, file: TargetFile) -> Task[bool]: ...


class ImageProvider:
    @abstractmethod
    def load(self, path: Union[str, Path]) -> Image.Image: ...

    @abstractmethod
    def fix(self, image: Image.Image,
            size: Tuple[int, int]) -> Image.Image: ...