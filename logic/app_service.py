from config import DEFAULT_CUSTOMER_ID
from DataBase import customer_dao, order_dao, product_dao, supplier_dao
from logic import order_manager, search_engine


STATUS_LABELS = {
    "PENDING_PAY": "待支付",
    "PENDING_SHIP": "待发货",
    "SHIPPED": "已发货",
    "COMPLETED": "已完成",
    "CANCELLED": "已取消",
}


class DatabaseStore:
    mode_name = "MySQL"

    def __init__(self):
        self.cart = []
        self.default_customer = customer_dao.get_customer_by_id(DEFAULT_CUSTOMER_ID) or customer_dao.get_first_customer()
        if not self.default_customer:
            raise RuntimeError("数据库中没有客户数据")
        self.customer = self._map_customer(self.default_customer, None)

    def reset_session(self):
        self.cart.clear()
        self.customer = self._map_customer(self.default_customer, None)

    def set_active_customer(self, customer_id, customer_name=None):
        customer = customer_dao.get_customer_by_id(customer_id)
        if not customer:
            raise ValueError("客户不存在")
        self.customer = self._map_customer(customer, customer_name)
        self.cart.clear()

    def get_all_suppliers(self):
        rows = supplier_dao.get_all_suppliers()
        return [self._map_supplier(row) for row in rows]

    def add_supplier(self, name, region, contact_info=None):
        row = supplier_dao.add_supplier(name, region, contact_info)
        return self._map_supplier(row)

    def get_products_by_supplier(self, supplier_id=None):
        rows = product_dao.get_products_by_supplier(supplier_id)
        return [self._map_product(row) for row in rows]

    def add_product(self, name, price, stock, tags_list, supplier_id):
        row = product_dao.add_product(name, price, stock, tags_list, supplier_id)
        return self._map_product(row)

    def search_products(self, keyword="", selected_tags=None):
        rows = search_engine.perform_search(keyword, selected_tags or [])
        return [self._map_product(row) for row in rows]

    def add_to_cart(self, product_id, quantity):
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError("数量必须大于 0")

        product = self._get_product(product_id)
        if not product:
            raise ValueError("商品不存在")

        for item in self.cart:
            if item["product_id"] == product_id:
                new_quantity = item["quantity"] + quantity
                if new_quantity > product["stock"]:
                    raise ValueError("库存不足")
                item["quantity"] = new_quantity
                item["subtotal"] = round(item["quantity"] * item["price"], 2)
                return item

        if quantity > product["stock"]:
            raise ValueError("库存不足")

        item = {
            "product_id": product["id"],
            "name": product["name"],
            "price": product["price"],
            "quantity": quantity,
            "subtotal": round(product["price"] * quantity, 2),
        }
        self.cart.append(item)
        return item

    def get_cart_items(self):
        return [item.copy() for item in self.cart]

    def remove_cart_item(self, product_id):
        self.cart = [item for item in self.cart if item["product_id"] != product_id]

    def clear_cart(self):
        self.cart.clear()

    def get_cart_total(self):
        return round(sum(item["subtotal"] for item in self.cart), 2)

    def place_order(self, customer_id, cart_items=None):
        payload = cart_items or self.cart
        order_manager.place_order(customer_id, payload)
        self.clear_cart()
        orders = self.get_orders_by_customer(customer_id)
        return orders[0] if orders else None

    def get_orders_by_customer(self, customer_id):
        rows = order_dao.get_orders_by_customer(customer_id)
        return [self._map_order(row) for row in rows]

    def get_orders_by_supplier(self, supplier_id):
        rows = order_dao.get_orders_by_supplier(supplier_id)
        return [self._map_order(row) for row in rows]

    def get_order_details(self, order_id):
        rows = order_dao.get_order_details(order_id)
        return [self._map_order_item(row) for row in rows]

    def get_order_details_by_supplier(self, order_id, supplier_id):
        rows = order_dao.get_order_details_by_supplier(order_id, supplier_id)
        return [self._map_order_item(row) for row in rows]

    def modify_order_action(self, order_id, action_type, item_id=None):
        order_manager.modify_order_action(order_id, action_type, item_id)
        rows = self.get_orders_by_customer(self.customer["id"])
        for row in rows:
            if row["id"] == order_id:
                return row
        return None

    def _get_product(self, product_id):
        row = product_dao.get_product_by_id(product_id)
        return self._map_product(row) if row else None

    @staticmethod
    def _map_customer(row, customer_name):
        return {
            "id": row["customer_id"],
            "name": customer_name or f'客户 {row["customer_id"]}',
            "contact_num": row["contact_num"],
            "shipping_address": row["shipping_address"],
        }

    @staticmethod
    def _map_supplier(row):
        return {
            "id": row["vendor_id"],
            "name": row["business_name"],
            "region": row["geo_location"],
            "avg_rating": float(row["avg_rating"] or 0),
        }

    @staticmethod
    def _map_product(row):
        return {
            "id": row["product_id"],
            "name": row["product_name"],
            "price": float(row["price"]),
            "stock": row["stock_quantity"],
            "supplier_id": row["vendor_id"],
            "supplier_name": row["supplier_name"],
            "tags_text": row["tags_text"],
        }

    @staticmethod
    def _map_order(row):
        return {
            "id": row["order_id"],
            "customer_id": row["customer_id"],
            "order_date": row["order_date"].strftime("%Y-%m-%d %H:%M"),
            "total_price": float(row["total_price"]),
            "status": STATUS_LABELS.get(row["order_status"], row["order_status"]),
        }

    @staticmethod
    def _map_order_item(row):
        return {
            "item_id": row["item_id"],
            "product_id": row["product_id"],
            "name": row["name"],
            "quantity": row["quantity"],
            "price_at_purchase": float(row["price_at_purchase"]),
            "subtotal": float(row["subtotal"]),
        }
