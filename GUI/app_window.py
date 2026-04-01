import tkinter as tk
from tkinter import ttk, messagebox

# 假设这些是你的其他导入
from config import USE_DEMO_DATA
from GUI.cart_view import CartView
from GUI.mock_service import DemoStore
from GUI.order_history_view import OrderHistoryView
from GUI.product_view import ProductView
from GUI.search_view import SearchView
from GUI.supplier_view import SupplierView
from logic.app_service import DatabaseStore
from GUI.entry_view import EntryView


class AppWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("电商平台演示")
        self.geometry("1180x760")
        self.minsize(1080, 680)

        self.store = self._build_store()
        self.status_var = tk.StringVar(value="就绪")
        self.current_page = None
        self.pages = {}

        # 页面分组定义
        self.management_pages = ["supplier", "product"]
        self.business_pages = ["search", "cart", "order"]

        # 初始化用户数据库
        self.users_db = self.get_user_data()
        self.current_user = None
        self.current_supplier_id = None  # 用于记录当前登录的供货商ID

        self._build_layout()
        self.show_entry_view()

    def get_user_data(self):
        """
        【数据源】包含所有用户、供应商账号密码及角色的字典
        注意：supplier 增加了 'id' 字段，用于数据过滤
        """
        return {
            # --- 管理员账号 ---
            "admin": {
                "password": "123456",
                "role": "admin",
                "name": "系统管理员"
            },
            # --- 普通客户账号 ---
            "user1": {
                "password": "123456",
                "role": "client",
                "name": "普通客户"
            },
            "user2": {
                "password": "123456",
                "role": "client",
                "name": "普通客户"
            },
            # --- 供货商账号 (增加了 id) ---
            "sup1": {
                "password": "123456",
                "role": "supplier",
                "name": "晨光数码",
                "id": 1  # 对应数据库中的 supplier_id = 1
            },
            "sup2": {
                "password": "888888",
                "role": "supplier",
                "name": "北辰家居",
                "id": 2  # 对应数据库中的 supplier_id = 2
            }
        }

    def validate_login(self, username, password):
        """
        【登录验证】验证登录并跳转
        """
        user_info = self.users_db.get(username)

        # 检查用户是否存在且密码正确
        if user_info and user_info["password"] == password:
            self.current_user = user_info
            # 登录成功，根据角色跳转
            self.switch_mode(user_info["role"], user_info)
            return True
        return False

    def _build_layout(self):
        # --- 左侧导航栏 (拆分为三个独立的侧边栏) ---

        # 1. 管理端侧边栏 (Admin)
        self.nav_admin = ttk.Frame(self, padding=16)
        ttk.Label(self.nav_admin, text="后台管理", font=("Microsoft YaHei UI", 18, "bold")).pack(anchor="w", pady=(0, 18))
        ttk.Button(self.nav_admin, text="供应商管理", command=lambda: self.show_page("supplier"), width=18).pack(fill="x", pady=4)
        ttk.Button(self.nav_admin, text="商品目录", command=lambda: self.show_page("product"), width=18).pack(fill="x", pady=4)
        ttk.Button(self.nav_admin, text="退出登录", command=self.logout).pack(side="bottom", fill="x", pady=(20, 0))

        # 2. 业务端侧边栏 (Client)
        self.nav_client = ttk.Frame(self, padding=16)
        ttk.Label(self.nav_client, text="业务前台", font=("Microsoft YaHei UI", 18, "bold")).pack(anchor="w", pady=(0, 18))
        ttk.Button(self.nav_client, text="商品搜索", command=lambda: self.show_page("search"), width=18).pack(fill="x", pady=4)
        ttk.Button(self.nav_client, text="购物车", command=lambda: self.show_page("cart"), width=18).pack(fill="x", pady=4)
        ttk.Button(self.nav_client, text="订单历史", command=lambda: self.show_page("order"), width=18).pack(fill="x", pady=4)
        ttk.Button(self.nav_client, text="退出登录", command=self.logout).pack(side="bottom", fill="x", pady=(20, 0))

        # 3. 供货商侧边栏 (Supplier)
        self.nav_supplier = ttk.Frame(self, padding=16)
        ttk.Label(self.nav_supplier, text="供货商 Portal", font=("Microsoft YaHei UI", 18, "bold"), foreground="#d35400").pack(anchor="w", pady=(0, 18))
        ttk.Button(self.nav_supplier, text="我的商品", command=lambda: self.show_page("product"), width=18).pack(fill="x", pady=4)
        ttk.Button(self.nav_supplier, text="订单处理", command=lambda: self.show_page("order"), width=18).pack(fill="x", pady=4)
        ttk.Button(self.nav_supplier, text="退出登录", command=self.logout).pack(side="bottom", fill="x", pady=(20, 0))

        # --- 右侧内容区域 ---
        content = ttk.Frame(self, padding=(0, 16, 16, 16))
        content.grid(row=0, column=1, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)

        # 容器定义
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

        # --- 底部状态栏 ---
        status = ttk.Label(self, textvariable=self.status_var, anchor="w", padding=(16, 8))
        status.grid(row=1, column=0, columnspan=2, sticky="ew")

        # 初始化视图
        self.pages["supplier"] = SupplierView(self.management_container, self)
        self.pages["product"] = ProductView(self.management_container, self)
        self.pages["search"] = SearchView(self.business_container, self)
        self.pages["cart"] = CartView(self.business_container, self)
        self.pages["order"] = OrderHistoryView(self.business_container, self)

        self.entry_view = EntryView(self.entry_container, self)

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

    def show_entry_view(self):
        """显示登录界面，隐藏所有侧边栏"""
        # 隐藏所有侧边栏
        self.nav_admin.grid_forget()
        self.nav_client.grid_forget()
        self.nav_supplier.grid_forget()

        # 隐藏功能容器
        self.management_container.grid_forget()
        self.business_container.grid_forget()

        # 显示登录容器
        self.entry_container.grid(row=0, column=0, sticky="nsew")
        self.status_var.set("请登录系统")

    def switch_mode(self, role, user_info):
        """根据角色切换界面"""
        # 隐藏登录容器
        self.entry_container.grid_forget()

        # 重置供货商ID
        self.current_supplier_id = None

        # 根据角色显示对应的侧边栏和内容容器
        if role == "admin":
            self.nav_admin.grid(row=0, column=0, sticky="ns")
            self.nav_client.grid_forget()
            self.nav_supplier.grid_forget()
            self.show_page("supplier")  # 管理员默认看供应商管理

        elif role == "client":
            self.nav_admin.grid_forget()
            self.nav_client.grid(row=0, column=0, sticky="ns")
            self.nav_supplier.grid_forget()
            self.show_page("search")  # 客户默认看搜索

        elif role == "supplier":
            self.nav_admin.grid_forget()
            self.nav_client.grid_forget()
            self.nav_supplier.grid(row=0, column=0, sticky="ns")
            # 【关键】记录当前供货商的ID，用于后续数据过滤
            self.current_supplier_id = user_info.get("id")
            self.show_page("product")  # 供货商默认看商品管理

    def logout(self):
        """退出登录"""
        self.current_user = None
        self.current_supplier_id = None
        self.show_entry_view()

    def show_page(self, page_key):
        # 确定页面所属容器
        if page_key in self.management_pages:
            active_container = self.management_container
            inactive_container = self.business_container
        else:
            active_container = self.business_container
            inactive_container = self.management_container

        inactive_container.grid_forget()
        active_container.grid(row=0, column=0, sticky="nsew")

        frame = self.pages[page_key]
        frame.tkraise()

        self.current_page = page_key

        # 【关键逻辑】如果是供货商访问商品页面，强制传入供货商ID进行过滤
        if page_key == "product" and self.current_supplier_id:
            if hasattr(frame, "refresh_by_supplier"):
                # 假设 ProductView 有一个专门按供货商过滤刷新的方法
                frame.refresh_by_supplier(self.current_supplier_id)
            else:
                # 如果没有专门方法，就调用普通刷新（需要在 ProductView 内部处理逻辑）
                frame.refresh()
        elif hasattr(frame, "refresh"):
            frame.refresh()

        # 状态栏显示当前用户和页面
        user_name = self.current_user['name'] if self.current_user else "未知"
        self.status_var.set(f"当前用户：{user_name} | 页面：{self._page_title(page_key)}")

    def refresh_views(self, message="已更新"):
        for frame in self.pages.values():
            if hasattr(frame, "refresh"):
                frame.refresh()
        self.status_var.set(message)

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
            "supplier": "供应商管理", "product": "商品目录",
            "search": "商品搜索", "cart": "购物车", "order": "订单历史",
        }
        return mapping[page_key]