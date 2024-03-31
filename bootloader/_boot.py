import gc
import vfs
from flashbdev import bdev

if bdev:
    vfs.mount(bdev, "/")

gc.collect()
