from tkinter import messagebox, ttk


class SupplierView(ttk.Frame):
    def __init__(self, parent, app):
        # 初始化供应商视图框架
        super().__init__(parent, padding=16)
        self.app = app

        # 配置网格布局权重：左侧表格占3份，右侧表单占2份
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)

        # 构建表格和表单
        self.tree = self._build_table()
        self._build_form()

    def _build_table(self):
        # 构建左侧供应商列表表格
        left = ttk.LabelFrame(self, text="供应商列表", padding=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)

        # 定义表格列
        columns = ("id", "name", "region", "rating")
        tree = ttk.Treeview(left, columns=columns, show="headings", height=18)
        # 设置表头
        tree.heading("id", text="ID")
        tree.heading("name", text="名称")
        tree.heading("region", text="地理位置")
        tree.heading("rating", text="平均评分")
        # 设置列宽和对齐方式
        tree.column("id", width=60, anchor="center")
        tree.column("name", width=180)
        tree.column("region", width=150, anchor="center")
        tree.column("rating", width=100, anchor="center")
        tree.grid(row=0, column=0, sticky="nsew")

        # 添加垂直滚动条
        scrollbar = ttk.Scrollbar(left, orient="vertical", command=tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=scrollbar.set)
        return tree

    def _build_form(self):
        # 构建右侧添加供应商表单
        right = ttk.LabelFrame(self, text="添加供应商", padding=12)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(1, weight=1)

        # 动态创建输入字段
        labels = ["名称", "地理位置"]
        self.entries = {}
        for row, label in enumerate(labels):
            ttk.Label(right, text=label).grid(row=row, column=0, sticky="w", pady=6)
            entry = ttk.Entry(right)
            entry.grid(row=row, column=1, sticky="ew", pady=6)
            self.entries[label] = entry

        # 添加供应商按钮
        ttk.Button(right, text="新增供应商", command=self.add_supplier).grid(
            row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0)
        )

    def refresh(self):
        # 刷新供应商列表
        # 清空现有表格内容
        for item in self.tree.get_children():
            self.tree.delete(item)
        # 从数据存储中获取所有供应商并填充表格
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
        # 添加新供应商
        # 获取表单输入数据
        name = self.entries["名称"].get().strip()
        region = self.entries["地理位置"].get().strip()

        # 校验必填字段
        if not all([name, region]):
            messagebox.showwarning("提示", "请填写完整信息")
            return

        try:
            # 调用业务逻辑添加供应商
            self.app.store.add_supplier(name, region)
        except Exception as exc:
            # 捕获并显示异常
            messagebox.showerror("错误", str(exc))
            return
        # 清空表单输入
        for entry in self.entries.values():
            entry.delete(0, "end")
        # 刷新视图并显示成功消息
        self.app.refresh_views("已添加供应商")