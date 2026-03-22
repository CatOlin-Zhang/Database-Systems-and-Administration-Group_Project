#TODO 处理标签搜索逻辑
def perform_search(query_text, selected_tags):
    """
        解析用户输入的文本和选中的标签。
        调用 product_dao.search_products。
        对结果进行二次过滤或排序（如果需要）。
    """
