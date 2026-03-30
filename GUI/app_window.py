import tkinter as tk
from tkinter import ttk

from config import USE_DEMO_DATA
from GUI.cart_view import CartView
from GUI.mock_service import DemoStore
from GUI.order_history_view import OrderHistoryView
from GUI.product_view import ProductView
from GUI.search_view import SearchView
from GUI.supplier_view import SupplierView
from logic.app_service import DatabaseStore


class AppWindow(tk.Tk):
    def __init__(self):
        # 初始化主窗口
        super().__init__()
        self.title("电商平台演示")
        self.geometry("1180x760")
        self.minsize(1080, 680)

        # 初始化数据存储层（根据配置选择演示模式或数据库模式）
        self.store = self._build_store()
        # 状态栏变量
        self.status_var = tk.StringVar(value="就绪")
        # 当前页面标识
        self.current_page = None
        # 存储所有页面视图的字典
        self.pages = {}

        # 构建界面布局
        self._build_layout()
        # 默认显示供应商管理页面
        self.show_page("supplier")

    def _build_layout(self):
        # 配置主窗口的网格布局权重，使右侧内容区域可自适应拉伸
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # --- 左侧导航栏 ---
        nav = ttk.Frame(self, padding=16)
        nav.grid(row=0, column=0, sticky="ns")

        # 导航栏标题
        title = ttk.Label(nav, text="电商平台", font=("Microsoft YaHei UI", 18, "bold"))
        title.pack(anchor="w", pady=(0, 18))

        # 定义导航按钮列表
        buttons = [
            ("供应商管理", "supplier"),
            ("商品目录", "product"),
            ("商品搜索", "search"),
            ("购物车", "cart"),
            ("订单历史", "order"),
        ]
        # 循环创建导航按钮
        for text, key in buttons:
            ttk.Button(nav, text=text, command=lambda page=key: self.show_page(page), width=18).pack(
                fill="x", pady=6
            )

        # 显示当前客户信息和运行模式
        customer_name = self.store.customer.get("name", "演示用户")
        info = ttk.Label(
            nav,
            text=f"当前客户：{customer_name}\n运行模式：{self.store.mode_name}",
            justify="left",
            foreground="#555555",
        )
        info.pack(anchor="w", pady=(18, 0))

        # --- 右侧内容区域 ---
        content = ttk.Frame(self, padding=(0, 16, 16, 16))
        content.grid(row=0, column=1, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)
        self.content = content

        # --- 底部状态栏 ---
        status = ttk.Label(self, textvariable=self.status_var, anchor="w", padding=(16, 8))
        status.grid(row=1, column=0, columnspan=2, sticky="ew")

        # 初始化所有页面视图并添加到内容区域
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
        # 切换到指定页面
        frame = self.pages[page_key]
        # 将指定页面提升到最上层
        frame.tkraise()
        self.current_page = page_key
        # 如果页面有刷新方法，则调用刷新
        if hasattr(frame, "refresh"):
            frame.refresh()
        # 更新状态栏信息
        self.status_var.set("当前页面：" + self._page_title(page_key))

    def refresh_views(self, message="已更新"):
        # 刷新所有视图（通常在数据变更后调用）
        for frame in self.pages.values():
            if hasattr(frame, "refresh"):
                frame.refresh()
        # 更新状态栏消息
        self.status_var.set(message)

    @staticmethod
    def _build_store():
        # 根据配置构建数据存储对象
        if USE_DEMO_DATA:
            return DemoStore()
        try:
            return DatabaseStore()
        except Exception:
            # 如果数据库连接失败，回退到演示模式
            return DemoStore()

    @staticmethod
    def _page_title(page_key):
        # 将页面键转换为中文标题
        mapping = {
            "supplier": "供应商管理",
            "product": "商品目录",
            "search": "商品搜索",
            "cart": "购物车",
            "order": "订单历史",
        }
        return mapping[page_key]