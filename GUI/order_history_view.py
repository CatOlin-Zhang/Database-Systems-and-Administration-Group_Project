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
        left = ttk.LabelFrame(self, text="Order List", padding=12)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.columnconfigure(0, weight=1)
        left.rowconfigure(0, weight=1)

        columns = ("id", "date", "status", "total")
        tree = ttk.Treeview(left, columns=columns, show="headings", height=18)
        tree.heading("id", text="Order ID")
        tree.heading("date", text="Order Time")
        tree.heading("status", text="State")
        tree.heading("total", text="Total price")
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
        right = ttk.LabelFrame(self, text="Order Details", padding=12)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        columns = ("item_id", "name", "quantity", "price", "subtotal")
        tree = ttk.Treeview(right, columns=columns, show="headings", height=18)
        tree.heading("item_id", text="Order ID")
        tree.heading("name", text="Product Name")
        tree.heading("quantity", text="Quantity")
        tree.heading("price", text="Transaction Price")
        tree.heading("subtotal", text="Total")
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
        self.remove_button = ttk.Button(actions, text="Delete selected items", command=self.remove_selected_item)
        self.remove_button.pack(side="left")
        self.cancel_button = ttk.Button(actions, text="Cancel the entire order", command=self.cancel_order)
        self.cancel_button.pack(side="left", padx=8)
        return tree

    def refresh(self):
        if self.app.is_supplier_mode():
            orders = self.app.store.get_orders_by_supplier(self.app.current_supplier_id)
        else:
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

        self._update_action_state()
        self.refresh_details()

    def on_order_select(self, _event=None):
        selected = self.order_tree.selection()
        if not selected:
            self.current_order_id = None
        else:
            self.current_order_id = int(self.order_tree.item(selected[0], "values")[0])
        self._update_action_state()
        self.refresh_details()

    def refresh_details(self):
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)
        if not self.current_order_id:
            return

        if self.app.is_supplier_mode():
            details = self.app.store.get_order_details_by_supplier(
                self.current_order_id,
                self.app.current_supplier_id,
            )
        else:
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

    def _update_action_state(self):
        enabled = self.app.can_modify_customer_order() and self.current_order_id is not None
        state = "normal" if enabled else "disabled"
        self.remove_button.configure(state=state)
        self.cancel_button.configure(state=state)

    def remove_selected_item(self):
        if not self.app.can_modify_customer_order():
            messagebox.showwarning("Notice", "The current account cannot modify the order")
            return
        if not self.current_order_id:
            messagebox.showwarning("Notice", "Please select an order first")
            return

        selected = self.detail_tree.selection()
        if not selected:
            messagebox.showwarning("Notice", "Please select an order first")
            return

        item_id = int(self.detail_tree.item(selected[0], "values")[0])
        try:
            self.app.store.modify_order_action(self.current_order_id, "remove", item_id)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return

        self.app.refresh_views("The order has been updated")

    def cancel_order(self):
        if not self.app.can_modify_customer_order():
            messagebox.showwarning("Notice", "The current account cannot modify the order")
            return
        if not self.current_order_id:
            messagebox.showwarning("Notice", "Please select an order first")
            return

        try:
            self.app.store.modify_order_action(self.current_order_id, "cancel")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return

        self.app.refresh_views("The order has been canceled")
