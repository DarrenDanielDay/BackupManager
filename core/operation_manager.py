from typing import *
from functools import partial
from pathlib import Path
import os
import datetime

from utils.singletone import Singletone
from utils.task import Task
from models.target_file import TargetFile, TargetFileOperation
import core.impl as impl


class OperationManager(Singletone):
    target_files: List[TargetFile] = []
    done_targets: List[TargetFile] = []
    failed_targets: List[Tuple[TargetFile, BaseException]] = []

    def do_operation(self, target_file: TargetFile):
        suffix = target_file.path.name.split('.')[-1]

        def do_copy():
            key, byte_arr = self.load_key(target_file.path)
            target_path = impl.config_impl.target_path / f'{key}.{suffix}'
            if target_path.exists():
                crashed_byte_arr = self.load_bytes(target_path)
                if byte_arr == crashed_byte_arr:
                    raise FileExistsError(target_path)
                else:
                    unity = datetime.datetime.now().timestamp()
                    target_path = impl.config_impl.target_path / f'{key}{unity}.{suffix}'
                    assert not target_path.exists()
            self.save_file(target_path, byte_arr)
        
        if target_file.operation == TargetFileOperation.backup:
            print('copy!')
            do_copy()
        elif target_file.operation == TargetFileOperation.delete:
            print('delete!')
            self.delete_file(target_file.path)
        elif target_file.operation == TargetFileOperation.move:
            print('move!')
            do_copy()
            self.delete_file(target_file.path)
    
    def do_all(self) -> Task[bool]:
        impl.config_impl.target_path.mkdir(parents=True, exist_ok=True)
        tasks = []
        for target_file in self.target_files:
            task = Task(lambda: self.do_operation(target_file)).then(
                lambda none, f = target_file:  self.done_targets.append(f)
            ).catch(
                lambda exception, f = target_file: self.failed_targets.append((f, exception))
            )
            tasks.append(task)
        return Task.all(tasks)

    def delete_file(self, path: Path):
        os.remove(path)
    
    def load_bytes(self, path: Path) -> bytes:
        with open(path, 'rb') as file:
            byte_arr: bytes = file.read()
        return byte_arr

    def load_key(self, path: Path) -> Tuple[str, bytes]:
        byte_arr = self.load_bytes(path)
        return impl.key_provider_impl.provide(byte_arr), byte_arr
        

    def save_file(self, path: Path, byte_arr: bytes):
        with open(path, 'wb') as file:
            file.write(byte_arr)
