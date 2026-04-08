import tkinter as tk
from tkinter import messagebox, ttk

from config import USE_DEMO_DATA
from GUI.cart_view import CartView
from GUI.entry_view import EntryView
from GUI.mock_service import DemoStore
from GUI.order_history_view import OrderHistoryView
from GUI.product_view import ProductView
from GUI.search_view import SearchView
from GUI.supplier_view import SupplierView
from logic.app_service import DatabaseStore


class AppWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("E-commerce platform demonstration")
        self.geometry("1180x760")
        self.minsize(1080, 680)

        self.store = self._build_store()
        self.status_var = tk.StringVar(value="Ready")
        self.current_page = None
        self.current_user = None
        self.current_supplier_id = None
        self.pages = {}

        self.management_pages = {"supplier", "product"}
        self.business_pages = {"search", "cart", "order"}
        self.users_db = self.get_user_data()

        self._build_layout()
        self.show_entry_view()

    def get_user_data(self):
        return {
            "admin": {
                "password": "123456",
                "role": "admin",
                "name": "admin",
            },
            "user1": {
                "password": "123456",
                "role": "client",
                "name": "user1",
                "customer_id": 1,
            },
            "user2": {
                "password": "123456",
                "role": "client",
                "name": "user2",
                "customer_id": 2,
            },
            "sup1": {
                "password": "123456",
                "role": "supplier",
                "name": "Chenguang Digital",
                "supplier_id": 1,
            },
            "sup2": {
                "password": "123456",
                "role": "supplier",
                "name": "Beichen Home",
                "supplier_id": 2,
            },
        }

    def validate_login(self, username, password):
        user_info = self.users_db.get(username)
        if not user_info or user_info["password"] != password:
            return False

        self.current_user = user_info | {"username": username}
        self.current_supplier_id = user_info.get("supplier_id")

        if user_info["role"] == "client" and hasattr(self.store, "set_active_customer"):
            self.store.set_active_customer(user_info.get("customer_id"), user_info["name"])

        self.switch_mode(user_info["role"])
        return True

    def _build_layout(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self.nav_admin = ttk.Frame(self, padding=16)
        ttk.Label(self.nav_admin, text="Back-end Management", font=("Microsoft YaHei UI", 18, "bold")).pack(
            anchor="w", pady=(0, 18)
        )
        ttk.Button(
            self.nav_admin, text="Supplier Management", command=lambda: self.show_page("supplier"), width=18
        ).pack(fill="x", pady=4)
        ttk.Button(
            self.nav_admin, text="Product Catalog", command=lambda: self.show_page("product"), width=18
        ).pack(fill="x", pady=4)
        ttk.Button(self.nav_admin, text="Log out", command=self.logout).pack(
            side="bottom", fill="x", pady=(20, 0)
        )

        self.nav_client = ttk.Frame(self, padding=16)
        ttk.Label(self.nav_client, text="Customer Center", font=("Microsoft YaHei UI", 18, "bold")).pack(
            anchor="w", pady=(0, 18)
        )
        ttk.Button(
            self.nav_client, text="Product Search", command=lambda: self.show_page("search"), width=18
        ).pack(fill="x", pady=4)
        ttk.Button(
            self.nav_client, text="Shopping Cart", command=lambda: self.show_page("cart"), width=18
        ).pack(fill="x", pady=4)
        ttk.Button(
            self.nav_client, text="Order History", command=lambda: self.show_page("order"), width=18
        ).pack(fill="x", pady=4)
        ttk.Button(self.nav_client, text="Log out", command=self.logout).pack(
            side="bottom", fill="x", pady=(20, 0)
        )

        self.nav_supplier = ttk.Frame(self, padding=16)
        ttk.Label(
            self.nav_supplier,
            text="Supplier Center",
            font=("Microsoft YaHei UI", 18, "bold"),
            foreground="#d35400",
        ).pack(anchor="w", pady=(0, 18))
        ttk.Button(
            self.nav_supplier, text="My products", command=lambda: self.show_page("product"), width=18
        ).pack(fill="x", pady=4)
        ttk.Button(
            self.nav_supplier, text="Related orders", command=lambda: self.show_page("order"), width=18
        ).pack(fill="x", pady=4)
        ttk.Button(self.nav_supplier, text="Log out", command=self.logout).pack(
            side="bottom", fill="x", pady=(20, 0)
        )

        content = ttk.Frame(self, padding=(0, 16, 16, 16))
        content.grid(row=0, column=1, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)

        self.management_container = ttk.Frame(content)
        self.management_container.grid(row=0, column=0, sticky="nsew")
        self.management_container.columnconfigure(0, weight=1)
        self.management_container.rowconfigure(0, weight=1)

        self.business_container = ttk.Frame(content)
        self.business_container.grid(row=0, column=0, sticky="nsew")
        self.business_container.columnconfigure(0, weight=1)
        self.business_container.rowconfigure(0, weight=1)

        self.entry_container = ttk.Frame(content)
        self.entry_container.grid(row=0, column=0, sticky="nsew")
        self.entry_container.columnconfigure(0, weight=1)
        self.entry_container.rowconfigure(0, weight=1)

        status = ttk.Label(self, textvariable=self.status_var, anchor="w", padding=(16, 8))
        status.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.pages["supplier"] = SupplierView(self.management_container, self)
        self.pages["product"] = ProductView(self.management_container, self)
        self.pages["search"] = SearchView(self.business_container, self)
        self.pages["cart"] = CartView(self.business_container, self)
        self.pages["order"] = OrderHistoryView(self.business_container, self)

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        self.entry_view = EntryView(self.entry_container, self)
        self.entry_view.grid(row=0, column=0, sticky="nsew")

    def show_entry_view(self):
        self.current_page = None
        self.nav_admin.grid_forget()
        self.nav_client.grid_forget()
        self.nav_supplier.grid_forget()
        self.management_container.grid_forget()
        self.business_container.grid_forget()
        self.entry_container.grid(row=0, column=0, sticky="nsew")
        if hasattr(self.entry_view, "reset_form"):
            self.entry_view.reset_form()
        self.status_var.set("Please log in to the system first")

    def switch_mode(self, role):
        self.entry_container.grid_forget()

        if role == "admin":
            self.nav_admin.grid(row=0, column=0, sticky="ns")
            self.nav_client.grid_forget()
            self.nav_supplier.grid_forget()
            self.show_page("supplier")
            return

        if role == "client":
            self.nav_admin.grid_forget()
            self.nav_client.grid(row=0, column=0, sticky="ns")
            self.nav_supplier.grid_forget()
            self.show_page("search")
            return

        if role == "supplier":
            self.nav_admin.grid_forget()
            self.nav_client.grid_forget()
            self.nav_supplier.grid(row=0, column=0, sticky="ns")
            self.show_page("product")
            return

        messagebox.showerror("Error", "Unknown character")
        self.logout()

    def logout(self):
        self.current_user = None
        self.current_supplier_id = None
        if hasattr(self.store, "reset_session"):
            self.store.reset_session()
        self.show_entry_view()

    def show_page(self, page_key):
        if not self.current_user:
            self.show_entry_view()
            return

        if not self.can_access_page(page_key):
            messagebox.showwarning("Notice", "The current role does not have permission to access this page")
            return

        if page_key in self.management_pages:
            self.business_container.grid_forget()
            self.management_container.grid(row=0, column=0, sticky="nsew")
        else:
            self.management_container.grid_forget()
            self.business_container.grid(row=0, column=0, sticky="nsew")

        frame = self.pages[page_key]
        frame.tkraise()
        self.current_page = page_key

        if page_key == "product" and hasattr(frame, "refresh"):
            frame.refresh()
        elif page_key == "order" and hasattr(frame, "refresh"):
            frame.refresh()
        elif hasattr(frame, "refresh"):
            frame.refresh()

        user_name = self.current_user.get("name", "Unknown")
        self.status_var.set(f"Current User：{user_name} | Page：{self._page_title(page_key)}")

    def refresh_views(self, message="Updated"):
        for key, frame in self.pages.items():
            if not self.current_user or not self.can_access_page(key):
                continue
            if hasattr(frame, "refresh"):
                frame.refresh()
        self.status_var.set(message)

    def get_current_role(self):
        return self.current_user.get("role") if self.current_user else None

    def can_access_page(self, page_key):
        role = self.get_current_role()
        allowed_pages = {
            "admin": {"supplier", "product"},
            "client": {"search", "cart", "order"},
            "supplier": {"product", "order"},
        }
        return page_key in allowed_pages.get(role, set())

    def can_add_supplier(self):
        return self.get_current_role() == "admin"

    def can_add_product(self):
        return self.get_current_role() in {"admin", "supplier"}

    def can_purchase(self):
        return self.get_current_role() == "client"

    def can_modify_customer_order(self):
        return self.get_current_role() == "client"

    def is_supplier_mode(self):
        return self.get_current_role() == "supplier" and self.current_supplier_id is not None

    @staticmethod
    def _build_store():
        if USE_DEMO_DATA:
            return DemoStore()
        try:
            return DatabaseStore()
        except Exception:
            return DemoStore()

    @staticmethod
    def _page_title(page_key):
        mapping = {
            "supplier": "Supplier Management",
            "product": "Product Catalog",
            "search": "Product Search",
            "cart": "Shopping Cart",
            "order": "Order History",
        }
        return mapping[page_key]
