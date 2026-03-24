from tkinter import messagebox, ttk


class OrderHistoryView(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=16)
        self.app = app
        self.current_order_id = None

        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)

        self.order_tree = self._build_order_table()
        self.detail_tree = self._build_detail_table()

    def _build_order_table(self):
        left = ttk.LabelFrame(self, text="订单列表", padding=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)

        columns = ("id", "date", "status", "total")
        tree = ttk.Treeview(left, columns=columns, show="headings", height=18)
        tree.heading("id", text="订单ID")
        tree.heading("date", text="下单时间")
        tree.heading("status", text="状态")
        tree.heading("total", text="总价")
        tree.column("id", width=90, anchor="center")
        tree.column("date", width=150, anchor="center")
        tree.column("status", width=100, anchor="center")
        tree.column("total", width=100, anchor="e")
        tree.grid(row=0, column=0, sticky="nsew")
        tree.bind("<<TreeviewSelect>>", self.on_order_select)

        scrollbar = ttk.Scrollbar(left, orient="vertical", command=tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=scrollbar.set)
        return tree

    def _build_detail_table(self):
        right = ttk.LabelFrame(self, text="订单明细", padding=12)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

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

        scrollbar = ttk.Scrollbar(right, orient="vertical", command=tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=scrollbar.set)

        actions = ttk.Frame(right, padding=(0, 12, 0, 0))
        actions.grid(row=1, column=0, columnspan=2, sticky="ew")
        ttk.Button(actions, text="删除选中商品", command=self.remove_selected_item).pack(side="left")
        ttk.Button(actions, text="取消整个订单", command=self.cancel_order).pack(side="left", padx=8)
        return tree

    def refresh(self):
        orders = self.app.store.get_orders_by_customer(self.app.store.customer["id"])

        for item in self.order_tree.get_children():
            self.order_tree.delete(item)
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

        if self.current_order_id:
            order_ids = [order["id"] for order in orders]
            if self.current_order_id not in order_ids:
                self.current_order_id = None
        self.refresh_details()

    def on_order_select(self, _event=None):
        selected = self.order_tree.selection()
        if not selected:
            self.current_order_id = None
        else:
            self.current_order_id = int(self.order_tree.item(selected[0], "values")[0])
        self.refresh_details()

    def refresh_details(self):
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)
        if not self.current_order_id:
            return

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
        if not self.current_order_id:
            messagebox.showwarning("提示", "请先选择订单")
            return
        selected = self.detail_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择订单项")
            return

        item_id = int(self.detail_tree.item(selected[0], "values")[0])
        try:
            self.app.store.modify_order_action(self.current_order_id, "remove", item_id)
        except ValueError as exc:
            messagebox.showerror("错误", str(exc))
            return
        self.app.refresh_views("订单已更新")

    def cancel_order(self):
        if not self.current_order_id:
            messagebox.showwarning("提示", "请先选择订单")
            return
        try:
            self.app.store.modify_order_action(self.current_order_id, "cancel")
        except ValueError as exc:
            messagebox.showerror("错误", str(exc))
            return
        self.app.refresh_views("订单已取消")
