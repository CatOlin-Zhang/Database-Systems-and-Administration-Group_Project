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
        left = ttk.LabelFrame(self, text="供应商列表", padding=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)

        columns = ("id", "name", "region", "rating")
        tree = ttk.Treeview(left, columns=columns, show="headings", height=18)
        tree.heading("id", text="ID")
        tree.heading("name", text="名称")
        tree.heading("region", text="地理位置")
        tree.heading("rating", text="平均评分")
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
        right = ttk.LabelFrame(self, text="添加供应商", padding=12)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(1, weight=1)

        labels = ["名称", "地理位置"]
        self.entries = {}
        for row, label in enumerate(labels):
            ttk.Label(right, text=label).grid(row=row, column=0, sticky="w", pady=6)
            entry = ttk.Entry(right)
            entry.grid(row=row, column=1, sticky="ew", pady=6)
            self.entries[label] = entry

        ttk.Button(right, text="新增供应商", command=self.add_supplier).grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0)
        )

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

    def add_supplier(self):
        name = self.entries["名称"].get().strip()
        region = self.entries["地理位置"].get().strip()
        if not all([name, region]):
            messagebox.showwarning("提示", "请填写完整信息")
            return

        try:
            self.app.store.add_supplier(name, region)
        except Exception as exc:
            messagebox.showerror("错误", str(exc))
            return
        for entry in self.entries.values():
            entry.delete(0, "end")
        self.app.refresh_views("已添加供应商")
