import tkinter as tk
from tkinter import ttk

from GUI.cart_view import CartView
from GUI.mock_service import DemoStore
from GUI.order_history_view import OrderHistoryView
from GUI.product_view import ProductView
from GUI.search_view import SearchView
from GUI.supplier_view import SupplierView


class AppWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("电商平台演示")
        self.geometry("1180x760")
        self.minsize(1080, 680)

        self.store = DemoStore()
        self.status_var = tk.StringVar(value="就绪")
        self.current_page = None
        self.pages = {}

        self._build_layout()
        self.show_page("supplier")

    def _build_layout(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        nav = ttk.Frame(self, padding=16)
        nav.grid(row=0, column=0, sticky="ns")

        title = ttk.Label(nav, text="电商平台", font=("Microsoft YaHei UI", 18, "bold"))
        title.pack(anchor="w", pady=(0, 18))

        buttons = [
            ("供应商管理", "supplier"),
            ("商品目录", "product"),
            ("商品搜索", "search"),
            ("购物车", "cart"),
            ("订单历史", "order"),
        ]
        for text, key in buttons:
            ttk.Button(nav, text=text, command=lambda page=key: self.show_page(page), width=18).pack(
                fill="x", pady=6
            )

        info = ttk.Label(
            nav,
            text="当前客户：演示用户\n数据来源：本地内存",
            justify="left",
            foreground="#555555",
        )
        info.pack(anchor="w", pady=(18, 0))

        content = ttk.Frame(self, padding=(0, 16, 16, 16))
        content.grid(row=0, column=1, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)
        self.content = content

        status = ttk.Label(self, textvariable=self.status_var, anchor="w", padding=(16, 8))
        status.grid(row=1, column=0, columnspan=2, sticky="ew")

        page_builders = {
            "supplier": SupplierView,
            "product": ProductView,
            "search": SearchView,
            "cart": CartView,
            "order": OrderHistoryView,
        }
        for key, builder in page_builders.items():
            frame = builder(content, self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.pages[key] = frame

    def show_page(self, page_key):
        frame = self.pages[page_key]
        frame.tkraise()
        self.current_page = page_key
        if hasattr(frame, "refresh"):
            frame.refresh()
        self.status_var.set("当前页面：" + self._page_title(page_key))

    def refresh_views(self, message="已更新"):
        for frame in self.pages.values():
            if hasattr(frame, "refresh"):
                frame.refresh()
        self.status_var.set(message)

    @staticmethod
    def _page_title(page_key):
        mapping = {
            "supplier": "供应商管理",
            "product": "商品目录",
            "search": "商品搜索",
            "cart": "购物车",
            "order": "订单历史",
        }
        return mapping[page_key]
