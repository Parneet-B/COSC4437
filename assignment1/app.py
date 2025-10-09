import tkinter as tk
from tkinter import ttk
from tuple_space import TupleSpace
from coordinator import Coordinator, MQTTConfig
from owner_window import OwnerWindow
from developer_window import DeveloperWindow

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jira Board — Two-Window")
        self.root.geometry("480x120")

        space = TupleSpace()
        cfg = MQTTConfig()
        self.coord = Coordinator(space, cfg)

        self._build_windows()

        if self.coord.local_mode:
            self.coord.create_bug("Login fails intermittently", "High")
            self.coord.create_bug("Typo on pricing page", "Low")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        ttk.Label(self.root, text="Close this window to exit.").pack(pady=8)

    def _build_windows(self):
        owner = tk.Toplevel(self.root)
        owner.title("Product Owner")
        owner.geometry("720x520+40+40")
        OwnerWindow(owner, self.coord).pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        dev = tk.Toplevel(self.root)
        dev.title("Developer")
        dev.geometry("720x520+800+40")
        DeveloperWindow(dev, self.coord).pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def on_close(self):
        try:
            self.coord.stop()
        finally:
            self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    App().run()
