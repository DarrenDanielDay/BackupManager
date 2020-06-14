import hashlib
import json

from PIL import Image, ImageTk

from utils.singletone import Singletone
from core.interfaces import *
from utils.json_object import JSONItem, JSONConverter, JSONObject, ListJSONConverter

class HashKeyProvider(KeyProvider, Singletone):
    def provide(self, byte_arr: bytes) -> str:
        return hashlib.sha256(byte_arr).hexdigest()


class TargetFileOperationConverter(JSONConverter, Singletone):
    def to_json(self, value: TargetFileOperation) -> int:
        return value.value

    def from_json(self, value: int) -> TargetFileOperation:
        return TargetFileOperation.from_int(value)

class PathConverter(JSONConverter, Singletone):
    def to_json(self, value: Path) -> str:
        return str(value.absolute())
    
    def from_json(self, value: str) -> Path:
        return Path(value)

class JSONConfig(Configuration, JSONObject):
    search_paths = JSONItem('searchPaths', [Path('assets')], converter=ListJSONConverter(PathConverter()))
    target_path = JSONItem('targetPath', Path(r'C:\Backups'), converter=PathConverter())
    current_mode = JSONItem('currentMode', TargetFileOperation.backup)
    grid_height = JSONItem('gridHeight', 100)
    grid_width = JSONItem('gridWidth', 100)
    default_operation = JSONItem('defaultOperation', TargetFileOperation.backup, converter=TargetFileOperationConverter())
    db_file = JSONItem('dbFile', None, expected_type=Optional[Path])
    x_count = JSONItem('xCount', 4)
    y_count = JSONItem('yCount', 4)

    @staticmethod
    def load(src: str) -> "JSONConfig":
        with open(src) as file:
            json_string = file.read()
        try:
            result = JSONConfig().load_from_dict(json.loads(json_string))
        except BaseException as e:
            print(f"failed to load Configuration from {src}: {e}")
            result = JSONConfig()
        return result

    def save(self, path: Union[Path, str] = Path('./config.json')):
        json_dict = self.to_json_dict(self)
        json_string = json.dumps(json_dict, sort_keys=True, indent=4)
        with open(path, 'w+') as f:
            f.write(json_string)


class PILImageProvider(ImageProvider, Singletone):
    not_found_image = Image.open('assets/image_icon.jpg')
    not_supported_image = not_found_image

    def load(self, path: Union[Path, str]) -> Image.Image:
        try:
            image = Image.open(path)
        except FileNotFoundError:
            image = self.not_found_image
        except BaseException as e:
            print(
                f'Cannot make PhotoImage with given path: {path}, due to Exception: {e}')
            image = self.not_supported_image
        return image

    def fix(self, image: Image.Image, size: Tuple[int, int]) -> Image.Image:
        original: Tuple[int, int] = image.size
        if original[0] < size[0] and original[1] < size[1]:
            return image
        else:
            percent = min(size[0]/original[0], size[1]/original[1])
            width = int(original[0] * percent)
            height = int(original[1] * percent)
            return image.resize((width, height))
