import tkinter as tk
from tkinter import ttk, messagebox
from typing import Tuple, List
from coordinator import Coordinator

TupleType = Tuple[int, str, str, str, str]

class OwnerWindow(ttk.Frame):
    def __init__(self, master, coordinator: "Coordinator"):
        super().__init__(master)
        self.coordinator = coordinator

        ttk.Label(self, text="Product Owner — Create Bug").grid(row=0, column=0, columnspan=3, pady=(0,8))
        ttk.Label(self, text="Title").grid(row=1, column=0, sticky=tk.E)
        self.title_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.title_var, width=40).grid(row=1, column=1, padx=6, pady=4, sticky=tk.W)

        ttk.Label(self, text="Priority").grid(row=2, column=0, sticky=tk.E)
        self.prio_var = tk.StringVar(value="Medium")
        ttk.Combobox(self, textvariable=self.prio_var, values=["Low","Medium","High"], state="readonly", width=12).grid(row=2, column=1, padx=6, pady=4, sticky=tk.W)

        ttk.Button(self, text="Create Bug", command=self._create).grid(row=3, column=0, columnspan=2, pady=8)

        ttk.Label(self, text="All Bugs (live)").grid(row=4, column=0, columnspan=3, pady=(10,4))
        self.tree = ttk.Treeview(self, columns=("id","title","priority","status","assigned"), show="headings", height=10)
        for c, w in zip(("id","title","priority","status","assigned"), (60, 260, 90, 110, 140)):
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=w)
        self.tree.grid(row=5, column=0, columnspan=3, sticky="nsew")
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.after(400, self._refresh_board)

    def _create(self):
        title = self.title_var.get().strip()
        prio = self.prio_var.get()
        if not title:
            messagebox.showwarning("Validation", "Please enter a title")
            return
        self.coordinator.create_bug(title, prio)
        self.title_var.set("")
        self.prio_var.set("Medium")

    def _refresh_board(self):
        bugs: List[TupleType] = self.coordinator.space.list_all()
        self.tree.delete(*self.tree.get_children())
        for b in bugs:
            self.tree.insert("", tk.END, values=b)
        self.after(900, self._refresh_board)
