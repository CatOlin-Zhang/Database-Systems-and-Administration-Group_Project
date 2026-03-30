from __future__ import annotations

from copy import deepcopy
from datetime import datetime


class DemoStore:
    # 定义运行模式名称，用于界面显示
    mode_name = "演示数据"

    def __init__(self):
        # 初始化演示数据
        self.customer = {"id": 1, "name": "演示用户"}
        # 模拟供应商列表
        self.suppliers = [
            {"id": 1, "name": "晨光数码", "region": "深圳", "avg_rating": 4.7},
            {"id": 2, "name": "北辰家居", "region": "上海", "avg_rating": 4.4},
        ]
        # 模拟商品列表
        self.products = [
            {
                "id": 1,
                "name": "机械键盘",
                "price": 299.0,
                "stock": 18,
                "tags": ["键盘", "办公", "电竞"],
                "supplier_id": 1,
            },
            {
                "id": 2,
                "name": "无线鼠标",
                "price": 89.0,
                "stock": 35,
                "tags": ["鼠标", "办公", "便携"],
                "supplier_id": 1,
            },
            {
                "id": 3,
                "name": "书桌台灯",
                "price": 129.0,
                "stock": 22,
                "tags": ["灯具", "家居", "护眼"],
                "supplier_id": 2,
            },
        ]
        # 初始化购物车、订单列表及自增ID计数器
        self.cart = []
        self.orders = []
        self.next_supplier_id = 3
        self.next_product_id = 4
        self.next_order_id = 1

    def get_all_suppliers(self):
        # 获取所有供应商的深拷贝副本，防止外部修改内部数据
        return deepcopy(self.suppliers)

    def add_supplier(self, name, region, contact_info=None):
        # 添加新供应商
        supplier = {
            "id": self.next_supplier_id,
            "name": name,
            "region": region,
            "avg_rating": 0,
        }
        self.next_supplier_id += 1
        self.suppliers.append(supplier)
        return deepcopy(supplier)

    def get_products_by_supplier(self, supplier_id=None):
        # 根据供应商ID获取商品列表，若无ID则返回所有商品
        rows = []
        for product in self.products:
            if supplier_id and product["supplier_id"] != supplier_id:
                continue
            rows.append(self._product_view(product))
        return rows

    def add_product(self, name, price, stock, tags_list, supplier_id):
        # 添加新商品
        product = {
            "id": self.next_product_id,
            "name": name,
            "price": float(price),
            "stock": int(stock),
            "tags": tags_list,
            "supplier_id": supplier_id,
        }
        self.next_product_id += 1
        self.products.append(product)
        return self._product_view(product)

    def search_products(self, keyword="", selected_tags=None):
        # 根据关键词和标签搜索商品
        keyword = keyword.strip().lower()
        selected_tags = [tag.strip().lower() for tag in (selected_tags or []) if tag.strip()]

        results = []
        for product in self.products:
            name_text = product["name"].lower()
            tags_text = [tag.lower() for tag in product["tags"]]
            # 检查关键词是否匹配商品名或标签
            keyword_ok = not keyword or keyword in name_text or any(keyword in tag for tag in tags_text)
            # 检查是否包含所有选中的标签
            tags_ok = not selected_tags or any(tag in tags_text for tag in selected_tags)
            if keyword_ok and tags_ok:
                results.append(self._product_view(product))
        return results

    def add_to_cart(self, product_id, quantity):
        # 添加商品到购物车
        quantity = int(quantity)
        product = self._find_product(product_id)
        if not product:
            raise ValueError("商品不存在")
        if quantity <= 0:
            raise ValueError("数量必须大于 0")
        if product["stock"] < quantity:
            raise ValueError("库存不足")

        # 如果商品已在购物车中，更新数量和总价
        for item in self.cart:
            if item["product_id"] == product_id:
                if product["stock"] < item["quantity"] + quantity:
                    raise ValueError("库存不足")
                item["quantity"] += quantity
                item["subtotal"] = round(item["quantity"] * item["price"], 2)
                return deepcopy(item)

        # 否则添加新购物车项
        cart_item = {
            "product_id": product["id"],
            "name": product["name"],
            "price": product["price"],
            "quantity": quantity,
            "subtotal": round(product["price"] * quantity, 2),
        }
        self.cart.append(cart_item)
        return deepcopy(cart_item)

    def get_cart_items(self):
        # 获取购物车所有项的深拷贝
        return deepcopy(self.cart)

    def remove_cart_item(self, product_id):
        # 从购物车中移除指定商品
        self.cart = [item for item in self.cart if item["product_id"] != product_id]

    def clear_cart(self):
        # 清空购物车
        self.cart.clear()

    def get_cart_total(self):
        # 计算购物车总价
        return round(sum(item["subtotal"] for item in self.cart), 2)

    def place_order(self, customer_id, cart_items=None):
        # 提交订单
        if customer_id != self.customer["id"]:
            raise ValueError("客户不存在")
        # 使用传入的购物车项或当前购物车
        items = deepcopy(cart_items if cart_items is not None else self.cart)
        if not items:
            raise ValueError("购物车为空")

        # 校验库存
        for item in items:
            product = self._find_product(item["product_id"])
            if not product or product["stock"] < item["quantity"]:
                raise ValueError(f"{item['name']} 库存不足")

        # 扣减库存并构建订单项
        order_items = []
        for item in items:
            product = self._find_product(item["product_id"])
            product["stock"] -= item["quantity"]
            order_items.append(
                {
                    "item_id": len(order_items) + 1,
                    "product_id": item["product_id"],
                    "name": item["name"],
                    "quantity": item["quantity"],
                    "price_at_purchase": item["price"],
                    "subtotal": round(item["price"] * item["quantity"], 2),
                }
            )

        # 创建订单对象
        order = {
            "id": self.next_order_id,
            "customer_id": customer_id,
            "order_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "待发货",
            "total_price": round(sum(item["subtotal"] for item in order_items), 2),
            "items": order_items,
        }
        self.next_order_id += 1
        # 将新订单插入列表头部（最新订单在前）
        self.orders.insert(0, order)
        # 下单成功后清空购物车
        self.clear_cart()
        return deepcopy(order)

    def get_orders_by_customer(self, customer_id):
        # 获取指定客户的所有订单
        rows = [order for order in self.orders if order["customer_id"] == customer_id]
        return deepcopy(rows)

    def get_order_details(self, order_id):
        # 获取订单的详细信息（订单项列表）
        order = self._find_order(order_id)
        if not order:
            return []
        return deepcopy(order["items"])

    def modify_order_action(self, order_id, action_type, item_id=None):
        # 修改订单（取消或移除商品）
        order = self._find_order(order_id)
        if not order:
            raise ValueError("订单不存在")
        if order["status"] != "待发货":
            raise ValueError("当前订单不可修改")

        if action_type == "cancel":
            # 取消订单：恢复库存
            for item in order["items"]:
                product = self._find_product(item["product_id"])
                if product:
                    product["stock"] += item["quantity"]
            order["status"] = "已取消"
            return deepcopy(order)

        if action_type == "remove":
            # 移除订单项
            if item_id is None:
                raise ValueError("缺少订单项")
            target = None
            for item in order["items"]:
                if item["item_id"] == item_id:
                    target = item
                    break
            if not target:
                raise ValueError("订单项不存在")

            # 恢复被移除商品的库存
            product = self._find_product(target["product_id"])
            if product:
                product["stock"] += target["quantity"]
            # 从订单项列表中移除
            order["items"] = [item for item in order["items"] if item["item_id"] != item_id]
            # 重新计算订单总价
            order["total_price"] = round(sum(item["subtotal"] for item in order["items"]), 2)
            if order["items"]:
                # 重置订单项ID以保持连续
                self._reset_item_ids(order)
            else:
                # 如果订单项为空，将订单状态设为已取消
                order["status"] = "已取消"
            return deepcopy(order)

        raise ValueError("未知操作")

    def _product_view(self, product):
        # 将商品数据转换为视图模型，添加供应商名称和标签文本
        supplier = self._find_supplier(product["supplier_id"])
        row = deepcopy(product)
        row["supplier_name"] = supplier["name"] if supplier else "未知供应商"
        row["tags_text"] = ", ".join(product["tags"])
        return row

    def _find_supplier(self, supplier_id):
        # 根据ID查找供应商
        for supplier in self.suppliers:
            if supplier["id"] == supplier_id:
                return supplier
        return None

    def _find_product(self, product_id):
        # 根据ID查找商品
        for product in self.products:
            if product["id"] == product_id:
                return product
        return None

    def _find_order(self, order_id):
        # 根据ID查找订单
        for order in self.orders:
            if order["id"] == order_id:
                return order
        return None

    @staticmethod
    def _reset_item_ids(order):
        # 重置订单项的ID，使其从1开始连续递增
        for index, item in enumerate(order["items"], start=1):
            item["item_id"] = index