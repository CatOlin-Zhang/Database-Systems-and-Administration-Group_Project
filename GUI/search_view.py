import tkinter as tk
from tkinter import messagebox, ttk


class SearchView(ttk.Frame):
    def __init__(self, parent, app):
        # 初始化商品搜索视图框架
        super().__init__(parent, padding=16)
        self.app = app

        # 配置网格布局权重，使搜索结果区域可自适应拉伸
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # 搜索关键词变量
        self.keyword_var = tk.StringVar()
        # 标签过滤变量（逗号分隔）
        self.tags_var = tk.StringVar()
        # 购买数量变量
        self.qty_var = tk.StringVar(value="1")

        # 构建界面布局并获取表格控件
        self.tree = self._build_layout()

    def _build_layout(self):
        # --- 顶部搜索条件区域 ---
        top = ttk.LabelFrame(self, text="搜索条件", padding=12)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        # 关键词输入框
        ttk.Label(top, text="关键词").grid(row=0, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.keyword_var, width=24).grid(row=0, column=1, padx=8)

        # 标签输入框
        ttk.Label(top, text="标签").grid(row=0, column=2, sticky="w")
        ttk.Entry(top, textvariable=self.tags_var, width=24).grid(row=0, column=3, padx=8)

        # 搜索按钮
        ttk.Button(top, text="搜索", command=self.run_search).grid(row=0, column=4, padx=(8, 0))

        # --- 中间搜索结果表格 ---
        middle = ttk.LabelFrame(self, text="搜索结果", padding=12)
        middle.grid(row=1, column=0, sticky="nsew")
        middle.columnconfigure(0, weight=1)
        middle.rowconfigure(0, weight=1)

        # 定义表格列
        columns = ("id", "name", "supplier", "price", "stock", "tags")
        tree = ttk.Treeview(middle, columns=columns, show="headings")
        tree.heading("id", text="ID")
        tree.heading("name", text="商品名")
        tree.heading("supplier", text="供应商")
        tree.heading("price", text="价格")
        tree.heading("stock", text="库存")
        tree.heading("tags", text="标签")
        # 设置列宽和对齐方式
        tree.column("id", width=60, anchor="center")
        tree.column("name", width=180)
        tree.column("supplier", width=150)
        tree.column("price", width=100, anchor="e")
        tree.column("stock", width=80, anchor="center")
        tree.column("tags", width=220)
        tree.grid(row=0, column=0, sticky="nsew")

        # 添加垂直滚动条
        scrollbar = ttk.Scrollbar(middle, orient="vertical", command=tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=scrollbar.set)

        # --- 底部操作区域 ---
        bottom = ttk.Frame(self, padding=(0, 12, 0, 0))
        bottom.grid(row=2, column=0, sticky="ew")

        ttk.Label(bottom, text="购买数量").pack(side="left")
        # 数量选择器
        ttk.Spinbox(bottom, from_=1, to=99, textvariable=self.qty_var, width=8).pack(side="left", padx=8)
        # 加入购物车按钮
        ttk.Button(bottom, text="加入购物车", command=self.add_to_cart).pack(side="left")
        return tree

    def refresh(self):
        # 刷新视图时自动执行搜索
        self.run_search()

    def run_search(self):
        # 执行搜索逻辑
        # 获取并清理关键词
        keyword = self.keyword_var.get().strip()
        # 解析标签列表（逗号分隔）
        tags = [tag.strip() for tag in self.tags_var.get().split(",") if tag.strip()]
        # 调用业务逻辑搜索商品
        results = self.app.store.search_products(keyword, tags)

        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        # 填充搜索结果
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
        # 将选中商品加入购物车
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择商品")
            return

        try:
            # 获取数量和商品ID
            quantity = int(self.qty_var.get())
            product_id = int(self.tree.item(selected[0], "values")[0])
            # 调用业务逻辑添加到购物车
            self.app.store.add_to_cart(product_id, quantity)
        except Exception as exc:
            # 捕获异常（如库存不足、数量无效等）
            messagebox.showerror("错误", str(exc))
            return

        # 刷新视图并显示成功消息
        self.app.refresh_views("已加入购物车")