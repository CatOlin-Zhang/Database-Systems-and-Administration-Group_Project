from DataBase.db_connector import get_managed_connection
from DataBase import order_dao, product_dao


EDITABLE_STATUSES = {"PENDING_PAY", "PENDING_SHIP"}


def place_order(customer_id, cart_items):
    if not cart_items:
        raise ValueError("购物车为空")

    with get_managed_connection() as conn:
        checked_items = []
        total_price = 0

        for cart_item in cart_items:
            product = product_dao.get_product_by_id(cart_item["product_id"], conn=conn, for_update=True)
            if not product:
                raise ValueError("商品不存在")
            quantity = int(cart_item["quantity"])
            if quantity <= 0:
                raise ValueError("购买数量必须大于 0")
            if product["stock_quantity"] < quantity:
                raise ValueError(f'{product["product_name"]} 库存不足')

            checked_items.append(
                {
                    "product_id": product["product_id"],
                    "name": product["product_name"],
                    "quantity": quantity,
                    "unit_price": float(product["price"]),
                }
            )
            total_price += float(product["price"]) * quantity

        order_id = order_dao.create_order(customer_id, total_price, "PENDING_SHIP", conn=conn)

        for item in checked_items:
            order_dao.add_order_item(
                order_id,
                item["product_id"],
                item["quantity"],
                item["unit_price"],
                conn=conn,
            )
            product_dao.update_stock(item["product_id"], -item["quantity"], conn=conn)

        order_dao.rebuild_transactions_for_order(order_id, conn=conn)
        return order_dao.get_order_by_id(order_id, conn=conn)


def modify_order_action(order_id, action_type, item_id=None):
    with get_managed_connection() as conn:
        order = order_dao.get_order_by_id(order_id, conn=conn, for_update=True)
        if not order:
            raise ValueError("订单不存在")
        if order["order_status"] not in EDITABLE_STATUSES:
            raise ValueError("订单已进入配送流程，不能修改")

        if action_type == "cancel":
            details = order_dao.get_order_details(order_id, conn=conn)
            for detail in details:
                product_dao.update_stock(detail["product_id"], detail["quantity"], conn=conn)
            order_dao.update_order_status(order_id, "CANCELLED", conn=conn)
            order_dao.delete_transactions_by_order(order_id, conn=conn)
            return order_dao.get_order_by_id(order_id, conn=conn)

        if action_type == "remove":
            if item_id is None:
                raise ValueError("缺少订单项")

            detail = order_dao.get_order_item_by_id(order_id, item_id, conn=conn, for_update=True)
            if not detail:
                raise ValueError("订单项不存在")

            product_dao.update_stock(detail["product_id"], detail["buy_quantity"], conn=conn)
            order_dao.remove_order_item_by_id(order_id, item_id, conn=conn)
            details = order_dao.get_order_details(order_id, conn=conn)
            if details:
                order_dao.update_order_total(order_id, conn=conn)
                order_dao.rebuild_transactions_for_order(order_id, conn=conn)
            else:
                order_dao.update_order_status(order_id, "CANCELLED", conn=conn)
                order_dao.update_order_total(order_id, conn=conn)
                order_dao.delete_transactions_by_order(order_id, conn=conn)
            return order_dao.get_order_by_id(order_id, conn=conn)

        raise ValueError("未知操作")
