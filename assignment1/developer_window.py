import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Tuple
from coordinator import Coordinator

TupleType = Tuple[int, str, str, str, str]

class DeveloperWindow(ttk.Frame):
    def __init__(self, master, coordinator: "Coordinator"):
        super().__init__(master)
        self.coordinator = coordinator

        ttk.Label(self, text="Developer").grid(row=0, column=0, columnspan=3, pady=(0,8))
        ttk.Label(self, text="Your name").grid(row=1, column=0, sticky=tk.E)
        self.dev_var = tk.StringVar(value="Dev")
        ttk.Entry(self, textvariable=self.dev_var, width=24).grid(row=1, column=1, pady=4, sticky=tk.W)

        ttk.Label(self, text="Select Open bug").grid(row=2, column=0, sticky=tk.E)
        self.open_bug_var = tk.StringVar()
        self.open_bug_menu = ttk.Combobox(self, textvariable=self.open_bug_var, width=40, state="readonly")
        self.open_bug_menu.grid(row=2, column=1, sticky=tk.W)
        ttk.Button(self, text="Pick", command=self._pick_selected).grid(row=2, column=2, padx=6)

        ttk.Label(self, text="Resolve one of your bugs").grid(row=3, column=0, sticky=tk.E)
        self.resolve_bug_var = tk.StringVar()
        self.resolve_bug_menu = ttk.Combobox(self, textvariable=self.resolve_bug_var, width=40, state="readonly")
        self.resolve_bug_menu.grid(row=3, column=1, sticky=tk.W)
        ttk.Button(self, text="Resolve Selected", command=self._resolve_selected).grid(row=3, column=2, padx=6)

        ttk.Label(self, text="My Bugs").grid(row=5, column=0, columnspan=3, pady=(10,4))
        self.tree = ttk.Treeview(self, columns=("id","title","priority","status","assigned"), show="headings", height=10)
        for c, w in zip(("id","title","priority","status","assigned"), (60, 220, 80, 110, 120)):
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=w)
        self.tree.grid(row=6, column=0, columnspan=3, sticky="nsew")
        self.grid_rowconfigure(6, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.after(500, self._refresh_open_bugs)
        self.after(600, self._refresh_my_bugs)
        self.after(700, self._refresh_resolvable)

    def _refresh_open_bugs(self):
        open_bugs: List[TupleType] = [b for b in self.coordinator.space.list_all() if b[3] == "Open" and b[4] == "Unassigned"]
        values = [f"{b[0]} - {b[1]} [{b[2]}]" for b in open_bugs]
        self.open_bug_menu["values"] = values
        cur = self.open_bug_var.get()
        if cur and cur not in values:
            self.open_bug_var.set("")
        self.after(1200, self._refresh_open_bugs)

    def _refresh_resolvable(self):
        dev = (self.dev_var.get() or "").strip()
        my_inprog: List[TupleType] = [b for b in self.coordinator.space.list_all() if b[4] == dev and b[3] == "In Progress"]
        values = [f"{b[0]} - {b[1]} [{b[2]}]" for b in my_inprog]
        self.resolve_bug_menu["values"] = values
        cur = self.resolve_bug_var.get()
        if cur and cur not in values:
            self.resolve_bug_var.set("")
        self.after(1200, self._refresh_resolvable)

    def _pick_selected(self):
        sel = self.open_bug_var.get().strip()
        if not sel:
            messagebox.showwarning("Pick", "Select a bug from the dropdown.")
            return
        try:
            bug_id = int(sel.split(" - ", 1)[0])
        except Exception:
            messagebox.showwarning("Pick", "Could not parse selected bug.")
            return
        dev = self.dev_var.get().strip() or "Dev"
        self.coordinator.pick_bug(bug_id, dev)

    def _resolve_selected(self):
        sel = self.resolve_bug_var.get().strip()
        if not sel:
            messagebox.showwarning("Resolve", "Select one of your in-progress bugs.")
            return
        try:
            bug_id = int(sel.split(" - ", 1)[0])
        except Exception:
            messagebox.showwarning("Resolve", "Could not parse selected bug.")
            return
        dev = self.dev_var.get().strip() or "Dev"
        self.coordinator.update_status(bug_id, dev, "Resolved")

    def _apply_status_from_table(self):
        sel_item = self.tree.focus()
        if not sel_item:
            messagebox.showwarning("Update", "Select one of *your* bugs from the table below.")
            return
        bug_id = int(self.tree.item(sel_item, "values")[0])
        dev = self.dev_var.get().strip() or "Dev"
        new_status = self.status_var.get()
        self.coordinator.update_status(bug_id, dev, new_status)

    def _refresh_my_bugs(self):
        dev = (self.dev_var.get() or "").strip()
        bugs = self.coordinator.space.list_all()
        my_bugs = [b for b in bugs if b[4] == dev]
        self.tree.delete(*self.tree.get_children())
        for bug in my_bugs:
            self.tree.insert("", tk.END, values=bug)
        self.after(900, self._refresh_my_bugs)
