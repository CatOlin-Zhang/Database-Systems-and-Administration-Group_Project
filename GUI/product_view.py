import tkinter as tk
from tkinter import messagebox, ttk


class ProductView(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=16)
        self.app = app

        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        self.filter_var = tk.StringVar(value="全部供应商")
        self.form_supplier_var = tk.StringVar()

        self.tree = self._build_table()
        self._build_form()

    def _build_table(self):
        left = ttk.LabelFrame(self, text="商品目录", padding=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(1, weight=1)

        top = ttk.Frame(left)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(top, text="供应商筛选").pack(side="left")
        self.filter_box = ttk.Combobox(top, textvariable=self.filter_var, state="readonly", width=18)
        self.filter_box.pack(side="left", padx=8)
        self.filter_box.bind("<<ComboboxSelected>>", lambda _event: self.refresh())

        columns = ("id", "name", "supplier", "price", "stock", "tags")
        tree = ttk.Treeview(left, columns=columns, show="headings", height=18)
        tree.heading("id", text="ID")
        tree.heading("name", text="商品名")
        tree.heading("supplier", text="供应商")
        tree.heading("price", text="价格")
        tree.heading("stock", text="库存")
        tree.heading("tags", text="标签")
        tree.column("id", width=60, anchor="center")
        tree.column("name", width=180)
        tree.column("supplier", width=150)
        tree.column("price", width=100, anchor="e")
        tree.column("stock", width=80, anchor="center")
        tree.column("tags", width=220)
        tree.grid(row=1, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(left, orient="vertical", command=tree.yview)
        scrollbar.grid(row=1, column=1, sticky="ns")
        tree.configure(yscrollcommand=scrollbar.set)
        return tree

    def _build_form(self):
        right = ttk.LabelFrame(self, text="添加商品", padding=12)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(1, weight=1)

        ttk.Label(right, text="供应商").grid(row=0, column=0, sticky="w", pady=6)
        self.form_supplier_box = ttk.Combobox(
            right, textvariable=self.form_supplier_var, state="readonly"
        )
        self.form_supplier_box.grid(row=0, column=1, sticky="ew", pady=6)

        labels = ["商品名", "价格", "库存", "标签"]
        self.entries = {}
        for row, label in enumerate(labels, start=1):
            ttk.Label(right, text=label).grid(row=row, column=0, sticky="w", pady=6)
            entry = ttk.Entry(right)
            entry.grid(row=row, column=1, sticky="ew", pady=6)
            self.entries[label] = entry

        ttk.Label(right, text="标签用英文逗号分隔", foreground="#666666").grid(
            row=5, column=0, columnspan=2, sticky="w", pady=(0, 10)
        )

        ttk.Button(right, text="新增商品", command=self.add_product).grid(
            row=6, column=0, columnspan=2, sticky="ew"
        )

    def refresh(self):
        suppliers = self.app.store.get_all_suppliers()
        options = ["全部供应商"] + [f'{item["id"]} - {item["name"]}' for item in suppliers]
        self.filter_box["values"] = options
        self.form_supplier_box["values"] = options[1:]

        if self.filter_var.get() not in options:
            self.filter_var.set("全部供应商")
        if self.form_supplier_var.get() not in options[1:] and options[1:]:
            self.form_supplier_var.set(options[1])

        supplier_id = None
        if self.filter_var.get() != "全部供应商":
            supplier_id = int(self.filter_var.get().split(" - ", 1)[0])

        for item in self.tree.get_children():
            self.tree.delete(item)
        for product in self.app.store.get_products_by_supplier(supplier_id):
            self.tree.insert(
                "",
                "end",
                values=(
                    product["id"],
                    product["name"],
                    product["supplier_name"],
                    f'{product["price"]:.2f}',
                    product["stock"],
                    product["tags_text"],
                ),
            )

    def add_product(self):
        supplier_text = self.form_supplier_var.get().strip()
        name = self.entries["商品名"].get().strip()
        price = self.entries["价格"].get().strip()
        stock = self.entries["库存"].get().strip()
        tags_text = self.entries["标签"].get().strip()
        if not all([supplier_text, name, price, stock]):
            messagebox.showwarning("提示", "请填写完整信息")
            return

        try:
            supplier_id = int(supplier_text.split(" - ", 1)[0])
            price_value = float(price)
            stock_value = int(stock)
        except ValueError:
            messagebox.showerror("错误", "价格或库存格式不正确")
            return

        tags_list = [tag.strip() for tag in tags_text.split(",") if tag.strip()]
        self.app.store.add_product(name, price_value, stock_value, tags_list, supplier_id)
        for entry in self.entries.values():
            entry.delete(0, "end")
        self.app.refresh_views("已添加商品")
