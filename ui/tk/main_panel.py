from tkinter import *
from typing import *
from tkinter.messagebox import showinfo

import core.impl as impl
from ui.tk.select_panel import SelectPanel
from models.target_file import TargetFile
from core.operation_manager import OperationManager
from core.collector import Collector
from core.filters import image_filter
from utils.debounce import debounce

class MainPanel(Frame):
    def __init__(self, parent=None, cnf={}, **kw):
        super().__init__(master=parent, cnf=cnf, **kw)
        self.manager = OperationManager()
        self.collector = Collector()
        self.gene = self.generator()
        self.gene.send(None)
        self.select_panel: Optional[SelectPanel] = None
        self.button_panel = Frame(self)
        self.next_button = Button(self.button_panel, text='next', command=debounce(self.next_select,  lambda: showinfo('提示','请等待图片加载完成')))
        self.next_button.pack(side=LEFT)
        self.start_button = Button(self.button_panel, text='start', command=self.start_operations)
        self.start_button.pack(side=RIGHT)
        self.button_panel.grid(row=1, column=0)
    
    def generator(self) -> Generator[List[TargetFile], int, None]:
        yield
        for path in impl.config_impl.search_paths:            
            gene = self.collector.sliced_generator(path, image_filter)
            gene.send(None)
            while True:
                try:
                    result = gene.send(impl.config_impl.x_count * impl.config_impl.y_count)
                    targets: List[TargetFile] = []
                    for item in result:
                        targets.append(TargetFile(item.absolute()))
                    yield targets
                except StopIteration:
                    break

    def next_select(self):
        if self.select_panel:
            self.select_panel: SelectPanel
            self.manager.target_files.extend(self.select_panel.targets)
            self.select_panel.destroy()
        try:
            result = self.gene.send(None)
        except StopIteration:
            showinfo('提示', '没有更多的文件了')
        else:
            self.select_panel = SelectPanel(result, (impl.config_impl.x_count, impl.config_impl.y_count), parent=self)
            self.select_panel.grid(row=0, column=0)


    def start_operations(self):
        if self.select_panel:
            self.manager.target_files.extend(self.select_panel.targets)
        self.manager.do_all().then(lambda all_done: showinfo('提示', f'操作完成 {"全部成功" if all_done else "部分失败"}'))