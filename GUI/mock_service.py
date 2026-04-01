from __future__ import annotations

from copy import deepcopy
from datetime import datetime


class DemoStore:
    mode_name = "演示数据"

    def __init__(self):
        self.default_customer = {"id": 1, "name": "演示用户1"}
        self.customer = deepcopy(self.default_customer)
        self.suppliers = [
            {"id": 1, "name": "晨光数码", "region": "深圳", "avg_rating": 4.7},
            {"id": 2, "name": "北辰家居", "region": "上海", "avg_rating": 4.4},
        ]
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
        self.cart = []
        self.orders = [
            {
                "id": 1,
                "customer_id": 1,
                "order_date": "2026-03-30 10:30",
                "status": "待发货",
                "total_price": 388.0,
                "items": [
                    {
                        "item_id": 1,
                        "product_id": 1,
                        "name": "机械键盘",
                        "quantity": 1,
                        "price_at_purchase": 299.0,
                        "subtotal": 299.0,
                    },
                    {
                        "item_id": 2,
                        "product_id": 3,
                        "name": "书桌台灯",
                        "quantity": 1,
                        "price_at_purchase": 89.0,
                        "subtotal": 89.0,
                    },
                ],
            }
        ]
        self.next_supplier_id = 3
        self.next_product_id = 4
        self.next_order_id = 2

    def reset_session(self):
        self.cart.clear()
        self.customer = deepcopy(self.default_customer)

    def set_active_customer(self, customer_id, customer_name=None):
        self.customer = {
            "id": customer_id,
            "name": customer_name or f"客户{customer_id}",
        }
        self.cart.clear()

    def get_all_suppliers(self):
        return deepcopy(self.suppliers)

    def add_supplier(self, name, region, contact_info=None):
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
        rows = []
        for product in self.products:
            if supplier_id is not None and product["supplier_id"] != supplier_id:
                continue
            supplier = self._find_supplier(product["supplier_id"])
            row = deepcopy(product)
            row["supplier_name"] = supplier["name"] if supplier else "未知供应商"
            row["tags_text"] = ", ".join(product["tags"])
            rows.append(row)
        return rows

    def add_product(self, name, price, stock, tags_list, supplier_id):
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

        supplier = self._find_supplier(supplier_id)
        row = deepcopy(product)
        row["supplier_name"] = supplier["name"] if supplier else "未知供应商"
        row["tags_text"] = ", ".join(product["tags"])
        return row

    def search_products(self, keyword="", selected_tags=None):
        keyword = keyword.strip().lower()
        selected_tags = [tag.strip().lower() for tag in (selected_tags or []) if tag.strip()]

        results = []
        for product in self.products:
            name_text = product["name"].lower()
            tags_text = [tag.lower() for tag in product["tags"]]
            keyword_ok = not keyword or keyword in name_text or any(keyword in tag for tag in tags_text)
            tags_ok = not selected_tags or any(tag in tags_text for tag in selected_tags)
            if keyword_ok and tags_ok:
                supplier = self._find_supplier(product["supplier_id"])
                row = deepcopy(product)
                row["supplier_name"] = supplier["name"] if supplier else "未知供应商"
                row["tags_text"] = ", ".join(product["tags"])
                results.append(row)
        return results

    def add_to_cart(self, product_id, quantity):
        quantity = int(quantity)
        product = self._find_product(product_id)
        if not product:
            raise ValueError("商品不存在")
        if quantity <= 0:
            raise ValueError("数量必须大于 0")
        if product["stock"] < quantity:
            raise ValueError("库存不足")

        for item in self.cart:
            if item["product_id"] == product_id:
                if product["stock"] < item["quantity"] + quantity:
                    raise ValueError("库存不足")
                item["quantity"] += quantity
                item["subtotal"] = round(item["quantity"] * item["price"], 2)
                return deepcopy(item)

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
        return deepcopy(self.cart)

    def remove_cart_item(self, product_id):
        self.cart = [item for item in self.cart if item["product_id"] != product_id]

    def clear_cart(self):
        self.cart.clear()

    def get_cart_total(self):
        return round(sum(item["subtotal"] for item in self.cart), 2)

    def place_order(self, customer_id, cart_items=None):
        if customer_id != self.customer["id"]:
            raise ValueError("客户不存在")
        items = deepcopy(cart_items if cart_items is not None else self.cart)
        if not items:
            raise ValueError("购物车为空")

        for item in items:
            product = self._find_product(item["product_id"])
            if not product or product["stock"] < item["quantity"]:
                raise ValueError(f"{item['name']} 库存不足")

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

        order = {
            "id": self.next_order_id,
            "customer_id": customer_id,
            "order_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "待发货",
            "total_price": round(sum(item["subtotal"] for item in order_items), 2),
            "items": order_items,
        }
        self.next_order_id += 1
        self.orders.insert(0, order)
        self.clear_cart()
        return deepcopy(order)

    def get_orders_by_customer(self, customer_id):
        rows = [order for order in self.orders if order["customer_id"] == customer_id]
        return deepcopy(rows)

    def get_orders_by_supplier(self, supplier_id):
        rows = []
        for order in self.orders:
            if any(self._find_product(item["product_id"])["supplier_id"] == supplier_id for item in order["items"]):
                rows.append(
                    {
                        "id": order["id"],
                        "customer_id": order["customer_id"],
                        "order_date": order["order_date"],
                        "status": order["status"],
                        "total_price": order["total_price"],
                    }
                )
        return deepcopy(rows)

    def get_order_details(self, order_id):
        order = self._find_order(order_id)
        if not order:
            return []
        return deepcopy(order["items"])

    def get_order_details_by_supplier(self, order_id, supplier_id):
        order = self._find_order(order_id)
        if not order:
            return []
        rows = []
        for item in order["items"]:
            product = self._find_product(item["product_id"])
            if product and product["supplier_id"] == supplier_id:
                rows.append(deepcopy(item))
        return rows

    def modify_order_action(self, order_id, action_type, item_id=None):
        order = self._find_order(order_id)
        if not order:
            raise ValueError("订单不存在")
        if order["status"] != "待发货":
            raise ValueError("当前订单不可修改")

        if action_type == "cancel":
            for item in order["items"]:
                product = self._find_product(item["product_id"])
                if product:
                    product["stock"] += item["quantity"]
            order["status"] = "已取消"
            return deepcopy(order)

        if action_type == "remove":
            if item_id is None:
                raise ValueError("缺少订单项")
            target = None
            for item in order["items"]:
                if item["item_id"] == item_id:
                    target = item
                    break
            if not target:
                raise ValueError("订单项不存在")

            product = self._find_product(target["product_id"])
            if product:
                product["stock"] += target["quantity"]
            order["items"] = [item for item in order["items"] if item["item_id"] != item_id]
            order["total_price"] = round(sum(item["subtotal"] for item in order["items"]), 2)
            if order["items"]:
                self._reset_item_ids(order)
            else:
                order["status"] = "已取消"
            return deepcopy(order)

        raise ValueError("未知操作")

    def _find_supplier(self, supplier_id):
        for supplier in self.suppliers:
            if supplier["id"] == supplier_id:
                return supplier
        return None

    def _find_product(self, product_id):
        for product in self.products:
            if product["id"] == product_id:
                return product
        return None

    def _find_order(self, order_id):
        for order in self.orders:
            if order["id"] == order_id:
                return order
        return None

    @staticmethod
    def _reset_item_ids(order):
        for index, item in enumerate(order["items"], start=1):
            item["item_id"] = index
