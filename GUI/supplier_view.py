from tkinter import messagebox, ttk


class SupplierView(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=16)
        self.app = app

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        self.tree = self._build_table()
        self._build_form()

    def _build_table(self):
        left = ttk.LabelFrame(self, text="Supplier List", padding=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)

        columns = ("id", "name", "region", "rating")
        tree = ttk.Treeview(left, columns=columns, show="headings", height=18)
        tree.heading("id", text="ID")
        tree.heading("name", text="Name")
        tree.heading("region", text="Geographical location")
        tree.heading("rating", text="Average Rating")
        tree.column("id", width=60, anchor="center")
        tree.column("name", width=180)
        tree.column("region", width=150, anchor="center")
        tree.column("rating", width=100, anchor="center")
        tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(left, orient="vertical", command=tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=scrollbar.set)
        return tree

    def _build_form(self):
        right = ttk.LabelFrame(self, text="Add Supplier", padding=12)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(1, weight=1)

        labels = ["Name", "Geographical location"]
        self.entries = {}
        for row, label in enumerate(labels):
            ttk.Label(right, text=label).grid(row=row, column=0, sticky="w", pady=6)
            entry = ttk.Entry(right)
            entry.grid(row=row, column=1, sticky="ew", pady=6)
            self.entries[label] = entry

        self.add_button = ttk.Button(right, text="Add New Supplier", command=self.add_supplier)
        self.add_button.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for supplier in self.app.store.get_all_suppliers():
            self.tree.insert(
                "",
                "end",
                values=(
                    supplier["id"],
                    supplier["name"],
                    supplier["region"],
                    f'{supplier.get("avg_rating", 0):.2f}',
                ),
            )

        enabled = self.app.can_add_supplier()
        for entry in self.entries.values():
            entry.configure(state="normal" if enabled else "disabled")
        self.add_button.configure(state="normal" if enabled else "disabled")

    def add_supplier(self):
        if not self.app.can_add_supplier():
            messagebox.showwarning("Notice", "The current account does not have permission to add suppliers.")
            return

        name = self.entries["Name"].get().strip()
        region = self.entries["Geographical location"].get().strip()
        if not all([name, region]):
            messagebox.showwarning("Notice", "Please fill in complete information")
            return

        try:
            self.app.store.add_supplier(name, region)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return

        for entry in self.entries.values():
            entry.delete(0, "end")
        self.app.refresh_views("Supplier added")
