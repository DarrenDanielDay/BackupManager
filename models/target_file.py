from typing import *
from pathlib import Path
from enum import IntEnum

class TargetFileOperation(IntEnum):
    ignore = 0
    delete = 1
    backup = 2
    move = 3


    def display_of(mode: "TargetFileOperation") -> str:
        displays : Dict["TargetFileOperation", str] = {
            TargetFileOperation.ignore: "忽略",
            TargetFileOperation.delete: "删除",
            TargetFileOperation.backup: "备份",
            TargetFileOperation.move:   "移动",
        }
        return displays[mode]

    @staticmethod
    def from_int(integer: int) -> "TargetFileOperation":
        return TargetFileOperation[next(
            filter(
                lambda p: TargetFileOperation[p].value == integer,
                TargetFileOperation.__members__.keys()
            ), 
            'backup'
        )]


class TargetFile:
    def __init__(self, path: Path):
        self.path: Optional[Path] = path
        self.operation: TargetFileOperation = TargetFileOperation.ignore
