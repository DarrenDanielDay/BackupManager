# from core.collector import Collector, Path
# from core.operation_manager import OperationManager
# import core.impl as impl
# from models.target_file import TargetFile, TargetFileOperation
from utils.debounce import debounce
from tkinter import *
import time
r = Tk()
def s():
    time.sleep(2)
    Button(r).pack()
    time.sleep(2)
Button(r, command=debounce(s, print), text="click").pack()
r.mainloop()

# c = Collector()

# gene = c.sliced_generator(impl.config_impl.search_paths[0])

# gene.send(None)

# while True:
#     try:
#         count = int(input('count = '))
#         results = gene.send(count)
#         for item in results:
#             print(item)
#     except:
#         break

# impl.config_impl.save()

# om = OperationManager()
# ps = c.collect_all(Path('assets'))
# ls = []
# for p in ps:
#     t = TargetFile(p)
#     t.operation = TargetFileOperation.move
#     ls.append(t)
# om.target_files.extend(ls)
# om.do_all()
# while len(om.done_targets) + len(om.failed_targets) != len(om.target_files):    ...
# print(om.failed_targets)
# t = TargetFile(Path('assets/image_icon.jpg').absolute())
# t.operation = TargetFileOperation.move
# OperationManager().do_operation(t)