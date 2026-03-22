#TODO 订单与交易记录的操作
def create_order(customer_id, total_price, status):
    """创建订单头信息，返回 order_id。"""

def add_order_item(order_id, product_id, quantity, price_at_purchase):
    """添加订单明细。"""

def get_orders_by_customer(customer_id):
    """获取客户历史订单。"""

def get_order_details(order_id):
    """获取订单包含的具体商品列表。"""

def cancel_order(order_id):
    """修改订单状态为“已取消”，并触发库存回滚逻辑。"""

def remove_item_from_order(order_id, product_id):
    """删除订单中的特定商品项。"""
