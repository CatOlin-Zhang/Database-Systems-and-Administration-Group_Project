import tkinter as tk
from tkinter import messagebox, ttk


class SearchView(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=16)
        self.app = app

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.keyword_var = tk.StringVar()
        self.tags_var = tk.StringVar()
        self.qty_var = tk.StringVar(value="1")

        self.tree = self._build_layout()

    def _build_layout(self):
        top = ttk.LabelFrame(self, text="搜索条件", padding=12)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        ttk.Label(top, text="关键词").grid(row=0, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.keyword_var, width=24).grid(row=0, column=1, padx=8)
        ttk.Label(top, text="标签").grid(row=0, column=2, sticky="w")
        ttk.Entry(top, textvariable=self.tags_var, width=24).grid(row=0, column=3, padx=8)
        ttk.Button(top, text="搜索", command=self.run_search).grid(row=0, column=4, padx=(8, 0))

        middle = ttk.LabelFrame(self, text="搜索结果", padding=12)
        middle.grid(row=1, column=0, sticky="nsew")
        middle.columnconfigure(0, weight=1)
        middle.rowconfigure(0, weight=1)

        columns = ("id", "name", "supplier", "price", "stock", "tags")
        tree = ttk.Treeview(middle, columns=columns, show="headings")
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
        tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(middle, orient="vertical", command=tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=scrollbar.set)

        bottom = ttk.Frame(self, padding=(0, 12, 0, 0))
        bottom.grid(row=2, column=0, sticky="ew")

        ttk.Label(bottom, text="购买数量").pack(side="left")
        ttk.Spinbox(bottom, from_=1, to=99, textvariable=self.qty_var, width=8).pack(side="left", padx=8)
        ttk.Button(bottom, text="加入购物车", command=self.add_to_cart).pack(side="left")
        return tree

    def refresh(self):
        self.run_search()

    def run_search(self):
        keyword = self.keyword_var.get().strip()
        tags = [tag.strip() for tag in self.tags_var.get().split(",") if tag.strip()]
        results = self.app.store.search_products(keyword, tags)

        for item in self.tree.get_children():
            self.tree.delete(item)
        for product in results:
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

    def add_to_cart(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择商品")
            return

        try:
            quantity = int(self.qty_var.get())
            product_id = int(self.tree.item(selected[0], "values")[0])
            self.app.store.add_to_cart(product_id, quantity)
        except Exception as exc:
            messagebox.showerror("错误", str(exc))
            return

        self.app.refresh_views("已加入购物车")
