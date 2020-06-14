from pathlib import Path
from typing import *



def suffix_filter(suffixes: List[str]) -> Callable[[Path], bool]:
    def filter_func(path: Path):
        return any(path.name.lower().endswith(f'.{suffix}') for suffix in suffixes)
    return filter_func

image_suffixes = ['jpg', 'png', 'jpeg', 'gif', 'bmp']
image_filter = suffix_filter(image_suffixes)