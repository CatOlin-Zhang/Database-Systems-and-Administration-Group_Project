from config import DEFAULT_CUSTOMER_ID
from DataBase import customer_dao, order_dao, product_dao, supplier_dao
from logic import order_manager, search_engine


# 订单状态码与中文标签的映射字典
STATUS_LABELS = {
    "PENDING_PAY": "待支付",
    "PENDING_SHIP": "待发货",
    "SHIPPED": "已发货",
    "COMPLETED": "已完成",
    "CANCELLED": "已取消",
}


class DatabaseStore:
    # 定义运行模式名称，用于界面显示
    mode_name = "MySQL"

    def __init__(self):
        # 初始化数据库存储层
        # 尝试获取默认客户，如果不存在则获取第一个客户
        customer = customer_dao.get_customer_by_id(DEFAULT_CUSTOMER_ID) or customer_dao.get_first_customer()
        if not customer:
            raise RuntimeError("数据库中没有客户数据")

        # 构建当前客户的信息字典
        self.customer = {
            "id": customer["customer_id"],
            "name": f'客户 {customer["customer_id"]}',
            "contact_num": customer["contact_num"],
            "shipping_address": customer["shipping_address"],
        }
        # 初始化内存中的购物车列表
        self.cart = []

    def get_all_suppliers(self):
        # 获取所有供应商
        rows = supplier_dao.get_all_suppliers()
        # 将数据库行数据映射为前端所需的字典格式
        return [self._map_supplier(row) for row in rows]

    def add_supplier(self, name, region, contact_info=None):
        # 添加新供应商
        row = supplier_dao.add_supplier(name, region, contact_info)
        return self._map_supplier(row)

    def get_products_by_supplier(self, supplier_id=None):
        # 根据供应商ID获取商品列表
        rows = product_dao.get_products_by_supplier(supplier_id)
        return [self._map_product(row) for row in rows]

    def add_product(self, name, price, stock, tags_list, supplier_id):
        # 添加新商品
        row = product_dao.add_product(name, price, stock, tags_list, supplier_id)
        return self._map_product(row)

    def search_products(self, keyword="", selected_tags=None):
        # 执行商品搜索
        rows = search_engine.perform_search(keyword, selected_tags or [])
        return [self._map_product(row) for row in rows]

    def add_to_cart(self, product_id, quantity):
        # 添加商品到购物车
        quantity = int(quantity)
        if quantity <= 0:
            raise ValueError("数量必须大于 0")

        # 获取商品信息
        product = self._get_product(product_id)
        if not product:
            raise ValueError("商品不存在")

        # 检查商品是否已在购物车中
        for item in self.cart:
            if item["product_id"] == product_id:
                new_quantity = item["quantity"] + quantity
                if new_quantity > product["stock"]:
                    raise ValueError("库存不足")
                item["quantity"] = new_quantity
                item["subtotal"] = round(item["quantity"] * item["price"], 2)
                return item

        # 检查新添加的商品数量是否超过库存
        if quantity > product["stock"]:
            raise ValueError("库存不足")

        # 创建新的购物车项
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
        # 获取购物车所有项的副本
        return [item.copy() for item in self.cart]

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
        payload = cart_items or self.cart
        # 调用订单管理器处理下单逻辑
        order_manager.place_order(customer_id, payload)
        # 下单成功后清空购物车
        self.clear_cart()
        # 获取并返回最新的订单列表中的第一个订单
        orders = self.get_orders_by_customer(customer_id)
        return orders[0] if orders else None

    def get_orders_by_customer(self, customer_id):
        # 获取指定客户的所有订单
        rows = order_dao.get_orders_by_customer(customer_id)
        return [self._map_order(row) for row in rows]

    def get_order_details(self, order_id):
        # 获取订单的详细信息
        rows = order_dao.get_order_details(order_id)
        return [self._map_order_item(row) for row in rows]

    def modify_order_action(self, order_id, action_type, item_id=None):
        # 修改订单（取消或移除商品）
        # 调用订单管理器处理修改逻辑
        order_manager.modify_order_action(order_id, action_type, item_id)
        # 获取更新后的订单列表
        rows = self.get_orders_by_customer(self.customer["id"])
        # 找到并返回被修改的订单
        for row in rows:
            if row["id"] == order_id:
                return row
        return None

    def _get_product(self, product_id):
        # 内部方法：根据ID获取商品
        row = product_dao.get_product_by_id(product_id)
        return self._map_product(row) if row else None

    @staticmethod
    def _map_supplier(row):
        # 将供应商数据库行数据映射为标准字典格式
        return {
            "id": row["vendor_id"],
            "name": row["business_name"],
            "region": row["geo_location"],
            "avg_rating": float(row["avg_rating"] or 0),
        }

    @staticmethod
    def _map_product(row):
        # 将商品数据库行数据映射为标准字典格式
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
        # 将订单数据库行数据映射为标准字典格式
        return {
            "id": row["order_id"],
            "customer_id": row["customer_id"],
            "order_date": row["order_date"].strftime("%Y-%m-%d %H:%M"),
            "total_price": float(row["total_price"]),
            "status": STATUS_LABELS.get(row["order_status"], row["order_status"]),
        }

    @staticmethod
    def _map_order_item(row):
        # 将订单项数据库行数据映射为标准字典格式
        return {
            "item_id": row["item_id"],
            "product_id": row["product_id"],
            "name": row["name"],
            "quantity": row["quantity"],
            "price_at_purchase": float(row["price_at_purchase"]),
            "subtotal": float(row["subtotal"]),
        }