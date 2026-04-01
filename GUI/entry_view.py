import tkinter as tk
from tkinter import messagebox, ttk


class EntryView(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=24)
        self.app = app
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        self._build_layout()

    def _build_layout(self):
        card = ttk.Frame(self, padding=24)
        card.grid(row=0, column=0)
        card.columnconfigure(1, weight=1)

        ttk.Label(card, text="系统登录", font=("Microsoft YaHei UI", 20, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(0, 16)
        )

        ttk.Label(card, text="用户名").grid(row=1, column=0, sticky="w", pady=6)
        ttk.Entry(card, textvariable=self.username_var, width=28).grid(row=1, column=1, pady=6)

        ttk.Label(card, text="密码").grid(row=2, column=0, sticky="w", pady=6)
        ttk.Entry(card, textvariable=self.password_var, show="*", width=28).grid(row=2, column=1, pady=6)

        ttk.Button(card, text="登录", command=self.submit_login).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(14, 8)
        )

        tips = (
            "管理员：admin / 123456\n"
            "客户：user1 / 123456\n"
            "供货商：sup1 / 123456"
        )
        ttk.Label(card, text=tips, foreground="#666666", justify="left").grid(
            row=4, column=0, columnspan=2, sticky="w"
        )

    def submit_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if not username or not password:
            messagebox.showwarning("提示", "请输入用户名和密码")
            return

        if not self.app.validate_login(username, password):
            messagebox.showerror("错误", "用户名或密码错误")
            return

        self.reset_form()

    def reset_form(self):
        self.username_var.set("")
        self.password_var.set("")
