from core.collector import Collector, Path, TargetFile
from ui.tk.select_panel import SelectPanel, Tk
import core.impl
from ui.tk.main_panel import MainPanel

root = Tk()
main_panel = MainPanel(root)
main_panel.pack()
root.mainloop()

core.impl.config_impl.save()
