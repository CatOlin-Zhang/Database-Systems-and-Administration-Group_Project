import tkinter as tk
from tkinter import messagebox, ttk


class CartView(ttk.Frame):
    def __init__(self, parent, app):
        # 初始化购物车视图框架
        super().__init__(parent, padding=16)
        self.app = app

        # 配置网格布局权重，使购物车表格可以自适应拉伸
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # 用于显示购物车总价的变量
        self.total_var = tk.StringVar(value="总价：0.00")
        # 构建界面布局并获取表格控件
        self.tree = self._build_layout()

    def _build_layout(self):
        # 创建购物车主容器
        wrapper = ttk.LabelFrame(self, text="购物车", padding=12)
        wrapper.grid(row=0, column=0, sticky="nsew")
        wrapper.columnconfigure(0, weight=1)
        wrapper.rowconfigure(0, weight=1)

        # 定义表格列
        columns = ("id", "name", "price", "quantity", "subtotal")
        tree = ttk.Treeview(wrapper, columns=columns, show="headings")

        # 设置表头文本
        tree.heading("id", text="商品ID")
        tree.heading("name", text="商品名")
        tree.heading("price", text="单价")
        tree.heading("quantity", text="数量")
        tree.heading("subtotal", text="小计")

        # 设置列宽和对齐方式
        tree.column("id", width=90, anchor="center")
        tree.column("name", width=220)
        tree.column("price", width=120, anchor="e")
        tree.column("quantity", width=100, anchor="center")
        tree.column("subtotal", width=120, anchor="e")
        tree.grid(row=0, column=0, sticky="nsew")

        # 添加垂直滚动条
        scrollbar = ttk.Scrollbar(wrapper, orient="vertical", command=tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=scrollbar.set)

        # 创建底部操作栏
        bottom = ttk.Frame(wrapper, padding=(0, 12, 0, 0))
        bottom.grid(row=1, column=0, columnspan=2, sticky="ew")

        # 显示总价标签
        ttk.Label(bottom, textvariable=self.total_var, font=("Microsoft YaHei UI", 11, "bold")).pack(
            side="left"
        )
        # 添加操作按钮
        ttk.Button(bottom, text="删除选中", command=self.remove_selected).pack(side="right", padx=(8, 0))
        ttk.Button(bottom, text="清空购物车", command=self.clear_cart).pack(side="right", padx=(8, 0))
        ttk.Button(bottom, text="提交订单", command=self.checkout).pack(side="right")
        return tree

    def refresh(self):
        # 刷新购物车视图
        # 清空现有表格内容
        for item in self.tree.get_children():
            self.tree.delete(item)
        # 从数据存储中获取购物车项并填充表格
        for cart_item in self.app.store.get_cart_items():
            self.tree.insert(
                "",
                "end",
                values=(
                    cart_item["product_id"],
                    cart_item["name"],
                    f'{cart_item["price"]:.2f}',
                    cart_item["quantity"],
                    f'{cart_item["subtotal"]:.2f}',
                ),
            )
        # 更新总价显示
        self.total_var.set(f'总价：{self.app.store.get_cart_total():.2f}')

    def remove_selected(self):
        # 删除选中的购物车项
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择商品")
            return
        # 获取选中项的商品ID
        product_id = int(self.tree.item(selected[0], "values")[0])
        # 从数据存储中移除该项
        self.app.store.remove_cart_item(product_id)
        # 刷新所有视图
        self.app.refresh_views("已移出购物车")

    def clear_cart(self):
        # 清空整个购物车
        self.app.store.clear_cart()
        self.app.refresh_views("购物车已清空")

    def checkout(self):
        # 提交订单
        try:
            # 调用数据存储的下单方法
            self.app.store.place_order(self.app.store.customer["id"])
        except Exception as exc:
            # 捕获异常并显示错误信息
            messagebox.showerror("错误", str(exc))
            return
        # 下单成功后刷新视图
        self.app.refresh_views("订单已创建")