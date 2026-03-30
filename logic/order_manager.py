from DataBase.db_connector import get_managed_connection
from DataBase import order_dao, product_dao

# 定义允许修改的订单状态集合
EDITABLE_STATUSES = {"PENDING_PAY", "PENDING_SHIP"}


def place_order(customer_id, cart_items):
    # 处理下单逻辑
    if not cart_items:
        raise ValueError("购物车为空")

    # 使用上下文管理器获取数据库连接，确保事务自动提交或回滚
    with get_managed_connection() as conn:
        checked_items = []
        total_price = 0

        # 第一阶段：校验库存并计算总价
        for cart_item in cart_items:
            # 获取商品信息并锁定行（for_update=True）
            product = product_dao.get_product_by_id(cart_item["product_id"], conn=conn, for_update=True)
            if not product:
                raise ValueError("商品不存在")
            quantity = int(cart_item["quantity"])
            if quantity <= 0:
                raise ValueError("购买数量必须大于 0")
            if product["stock_quantity"] < quantity:
                raise ValueError(f'{product["product_name"]} 库存不足')

            # 将校验通过的商品信息存入临时列表
            checked_items.append(
                {
                    "product_id": product["product_id"],
                    "name": product["product_name"],
                    "quantity": quantity,
                    "unit_price": float(product["price"]),
                }
            )
            total_price += float(product["price"]) * quantity

        # 第二阶段：创建订单主记录
        order_id = order_dao.create_order(customer_id, total_price, "PENDING_SHIP", conn=conn)

        # 第三阶段：插入订单项并扣减库存
        for item in checked_items:
            order_dao.add_order_item(
                order_id,
                item["product_id"],
                item["quantity"],
                item["unit_price"],
                conn=conn,
            )
            # 扣减库存（传入负数表示减少）
            product_dao.update_stock(item["product_id"], -item["quantity"], conn=conn)

        # 第四阶段：重建交易记录（如评分、销量统计等）
        order_dao.rebuild_transactions_for_order(order_id, conn=conn)
        # 返回完整的订单信息
        return order_dao.get_order_by_id(order_id, conn=conn)


def modify_order_action(order_id, action_type, item_id=None):
    # 处理订单修改逻辑（取消订单或移除商品）
    with get_managed_connection() as conn:
        # 获取订单信息并锁定
        order = order_dao.get_order_by_id(order_id, conn=conn, for_update=True)
        if not order:
            raise ValueError("订单不存在")
        # 检查订单状态是否允许修改
        if order["order_status"] not in EDITABLE_STATUSES:
            raise ValueError("订单已进入配送流程，不能修改")

        if action_type == "cancel":
            # 取消整个订单：恢复所有商品库存
            details = order_dao.get_order_details(order_id, conn=conn)
            for detail in details:
                # 增加库存（传入正数表示增加）
                product_dao.update_stock(detail["product_id"], detail["quantity"], conn=conn)
            # 更新订单状态为已取消
            order_dao.update_order_status(order_id, "CANCELLED", conn=conn)
            # 删除相关的交易记录
            order_dao.delete_transactions_by_order(order_id, conn=conn)
            return order_dao.get_order_by_id(order_id, conn=conn)

        if action_type == "remove":
            # 移除单个订单项
            if item_id is None:
                raise ValueError("缺少订单项")

            # 获取订单项详情并锁定
            detail = order_dao.get_order_item_by_id(order_id, item_id, conn=conn, for_update=True)
            if not detail:
                raise ValueError("订单项不存在")

            # 恢复该商品的库存
            product_dao.update_stock(detail["product_id"], detail["buy_quantity"], conn=conn)
            # 从订单中删除该项
            order_dao.remove_order_item_by_id(order_id, item_id, conn=conn)

            # 获取剩余的订单项
            details = order_dao.get_order_details(order_id, conn=conn)
            if details:
                # 如果订单中还有其他商品，更新总价和交易记录
                order_dao.update_order_total(order_id, conn=conn)
                order_dao.rebuild_transactions_for_order(order_id, conn=conn)
            else:
                # 如果订单变为空，将订单状态设为已取消，并清理交易记录
                order_dao.update_order_status(order_id, "CANCELLED", conn=conn)
                order_dao.update_order_total(order_id, conn=conn)
                order_dao.delete_transactions_by_order(order_id, conn=conn)
            return order_dao.get_order_by_id(order_id, conn=conn)

        raise ValueError("未知操作")