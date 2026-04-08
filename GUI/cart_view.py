import tkinter as tk
from tkinter import messagebox, ttk


class CartView(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=16)
        self.app = app

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.total_var = tk.StringVar(value="Total price：0.00")
        self.tree = self._build_layout()

    def _build_layout(self):
        wrapper = ttk.LabelFrame(self, text="Shopping Cart", padding=12)
        wrapper.grid(row=0, column=0, sticky="nsew")
        wrapper.columnconfigure(0, weight=1)
        wrapper.rowconfigure(0, weight=1)

        columns = ("id", "name", "price", "quantity", "subtotal")
        tree = ttk.Treeview(wrapper, columns=columns, show="headings")
        tree.heading("id", text="Product ID")
        tree.heading("name", text="Product Name")
        tree.heading("price", text="Unit price")
        tree.heading("quantity", text="Amount")
        tree.heading("subtotal", text="Total")
        tree.column("id", width=90, anchor="center")
        tree.column("name", width=220)
        tree.column("price", width=120, anchor="e")
        tree.column("quantity", width=100, anchor="center")
        tree.column("subtotal", width=120, anchor="e")
        tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(wrapper, orient="vertical", command=tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        tree.configure(yscrollcommand=scrollbar.set)

        bottom = ttk.Frame(wrapper, padding=(0, 12, 0, 0))
        bottom.grid(row=1, column=0, columnspan=2, sticky="ew")

        ttk.Label(bottom, textvariable=self.total_var, font=("Microsoft YaHei UI", 11, "bold")).pack(
            side="left"
        )
        self.remove_button = ttk.Button(bottom, text="Delete Selected", command=self.remove_selected)
        self.remove_button.pack(side="right", padx=(8, 0))
        self.clear_button = ttk.Button(bottom, text="Empty the shopping cart", command=self.clear_cart)
        self.clear_button.pack(side="right", padx=(8, 0))
        self.checkout_button = ttk.Button(bottom, text="Submit Order", command=self.checkout)
        self.checkout_button.pack(side="right")
        return tree

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

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

        can_buy = self.app.can_purchase()
        button_state = "normal" if can_buy else "disabled"
        self.remove_button.configure(state=button_state)
        self.clear_button.configure(state=button_state)
        self.checkout_button.configure(state=button_state)
        self.total_var.set(f'Total：{self.app.store.get_cart_total():.2f}')

    def remove_selected(self):
        if not self.app.can_purchase():
            messagebox.showwarning("Notice", "The current account cannot modify the shopping cart")
            return

        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Notice", "Please select a product first")
            return

        product_id = int(self.tree.item(selected[0], "values")[0])
        self.app.store.remove_cart_item(product_id)
        self.app.refresh_views("Removed from cart")

    def clear_cart(self):
        if not self.app.can_purchase():
            messagebox.showwarning("Notice", "The current account cannot modify the shopping cart")
            return

        self.app.store.clear_cart()
        self.app.refresh_views("The shopping cart has been emptied")

    def checkout(self):
        if not self.app.can_purchase():
            messagebox.showwarning("Notice", "The current account cannot place an order")
            return

        try:
            self.app.store.place_order(self.app.store.customer["id"])
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return

        self.app.refresh_views("The order has been created")
