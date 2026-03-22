#TODO 处理下单逻辑、库存扣减、总价计算
def place_order(customer_id, cart_items):
    """
        检查库存是否充足。
        开启数据库事务 (conn.begin())。
        调用 create_order。
        循环调用 add_order_item。
        循环调用 update_stock (扣减)。
        提交事务 (conn.commit())。若中间出错则 rollback()。
    """

def modify_order_action(order_id, action_type, item_id=None):
    """
        检查订单状态是否为“待发货/处理中”（未进入物流）。
        若是取消整个订单：调用 cancel_order 并回滚所有相关商品库存。
        若是删除单个商品：调用 remove_item_from_order 并回滚该商品库存，重新计算总价。
    """

