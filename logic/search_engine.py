from DataBase import product_dao


def perform_search(query_text, selected_tags):
    rows = product_dao.search_products(query_text, selected_tags)
    return sorted(rows, key=lambda item: (-item["stock_quantity"], item["product_name"]))
