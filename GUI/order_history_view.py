from tkinter import messagebox, ttk


class OrderHistoryView(ttk.Frame):
    def __init__(self, parent, app):
        # 初始化订单历史视图框架
        super().__init__(parent, padding=16)
        self.app = app
        # 当前选中的订单ID
        self.current_order_id = None

        # 配置网格布局权重：左侧订单列表占2份，右侧明细占3份
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)

        # 构建左右两个表格
        self.order_tree = self._build_order_table()
        self.detail_tree = self._build_detail_table()

    def _build_order_table(self):
        # 构建左侧订单列表表格
        left = ttk.LabelFrame(self, text="订单列表", padding=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)

        # 定义表格列
        columns = ("id", "date", "status", "total")
        tree = ttk.Treeview(left, columns=columns, show="headings", height=18)
        # 设置表头
        tree.heading("id", text="订单ID")
        tree.heading("date", text="下单时间")
        tree.heading("status", text="状态")
        tree.heading("total", text="总价")
        # 设置列宽和对齐方式
        tree.column("id", width=90, anchor="center")
        tree.column("date", width=150, anchor="center")
        tree.column("status", width=100, anchor="center")
        tree.column("total", width=100, anchor="e")
        tree.grid(row=0, column=0, sticky="nsew")
        # 绑定选择事件，点击订单行时刷新右侧明细
        tree.bind("<<TreeviewSelect>>", self.on_order_select)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(left, orient="vertical", command=tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=scrollbar.set)
        return tree

    def _build_detail_table(self):
        # 构建右侧订单明细表格
        right = ttk.LabelFrame(self, text="订单明细", padding=12)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        # 定义明细表格列
        columns = ("item_id", "name", "quantity", "price", "subtotal")
        tree = ttk.Treeview(right, columns=columns, show="headings", height=18)
        tree.heading("item_id", text="项ID")
        tree.heading("name", text="商品名")
        tree.heading("quantity", text="数量")
        tree.heading("price", text="成交价")
        tree.heading("subtotal", text="小计")
        tree.column("item_id", width=70, anchor="center")
        tree.column("name", width=180)
        tree.column("quantity", width=70, anchor="center")
        tree.column("price", width=90, anchor="e")
        tree.column("subtotal", width=90, anchor="e")
        tree.grid(row=0, column=0, sticky="nsew")

        # 添加滚动条
        scrollbar = ttk.Scrollbar(right, orient="vertical", command=tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=scrollbar.set)

        # 底部操作按钮区域
        actions = ttk.Frame(right, padding=(0, 12, 0, 0))
        actions.grid(row=1, column=0, columnspan=2, sticky="ew")
        ttk.Button(actions, text="删除选中商品", command=self.remove_selected_item).pack(side="left")
        ttk.Button(actions, text="取消整个订单", command=self.cancel_order).pack(side="left", padx=8)
        return tree

    def refresh(self):
        # 刷新订单列表
        # 获取当前客户的所有订单
        orders = self.app.store.get_orders_by_customer(self.app.store.customer["id"])

        # 清空现有列表
        for item in self.order_tree.get_children():
            self.order_tree.delete(item)
        # 填充订单数据
        for order in orders:
            self.order_tree.insert(
                "",
                "end",
                values=(
                    order["id"],
                    order["order_date"],
                    order["status"],
                    f'{order["total_price"]:.2f}',
                ),
            )

        # 检查当前选中的订单是否仍然有效
        if self.current_order_id:
            order_ids = [order["id"] for order in orders]
            if self.current_order_id not in order_ids:
                self.current_order_id = None
        # 刷新右侧明细
        self.refresh_details()

    def on_order_select(self, _event=None):
        # 处理订单列表的选择事件
        selected = self.order_tree.selection()
        if not selected:
            self.current_order_id = None
        else:
            # 获取选中行的订单ID
            self.current_order_id = int(self.order_tree.item(selected[0], "values")[0])
        # 刷新明细视图
        self.refresh_details()

    def refresh_details(self):
        # 刷新订单明细表格
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)
        if not self.current_order_id:
            return

        # 获取订单详情并填充表格
        details = self.app.store.get_order_details(self.current_order_id)
        for detail in details:
            self.detail_tree.insert(
                "",
                "end",
                values=(
                    detail["item_id"],
                    detail["name"],
                    detail["quantity"],
                    f'{detail["price_at_purchase"]:.2f}',
                    f'{detail["subtotal"]:.2f}',
                ),
            )

    def remove_selected_item(self):
        # 删除选中的订单项
        if not self.current_order_id:
            messagebox.showwarning("提示", "请先选择订单")
            return
        selected = self.detail_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择订单项")
            return

        # 获取选中项的ID
        item_id = int(self.detail_tree.item(selected[0], "values")[0])
        try:
            # 调用业务逻辑移除商品
            self.app.store.modify_order_action(self.current_order_id, "remove", item_id)
        except Exception as exc:
            messagebox.showerror("错误", str(exc))
            return
        # 刷新视图
        self.app.refresh_views("订单已更新")

    def cancel_order(self):
        # 取消整个订单
        if not self.current_order_id:
            messagebox.showwarning("提示", "请先选择订单")
            return
        try:
            # 调用业务逻辑取消订单
            self.app.store.modify_order_action(self.current_order_id, "cancel")
        except Exception as exc:
            messagebox.showerror("错误", str(exc))
            return
        # 刷新视图
        self.app.refresh_views("订单已取消")