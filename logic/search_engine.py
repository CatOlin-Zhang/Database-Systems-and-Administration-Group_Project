from DataBase import product_dao


def perform_search(query_text, selected_tags):
    # 执行商品搜索并返回排序后的结果
    # 调用数据访问层获取原始搜索结果
    rows = product_dao.search_products(query_text, selected_tags)
    # 对结果进行排序：优先按库存数量降序（库存充足的在前），其次按商品名称升序
    return sorted(rows, key=lambda item: (-item["stock_quantity"], item["product_name"]))