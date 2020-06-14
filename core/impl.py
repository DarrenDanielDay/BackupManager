from core.basic_implementations import *
T = TypeVar("T")

key_provider_impl: KeyProvider = HashKeyProvider()
image_provider_impl: ImageProvider = PILImageProvider()
config_impl: Configuration = JSONConfig.load('config.json')