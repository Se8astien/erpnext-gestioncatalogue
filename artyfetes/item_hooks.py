import frappe

def handle_item_before_save(doc, method):
    """
    Si Item est Désactivé, mettre is_purchase_item et is_sales_item à 0
    """
    if getattr(doc, "disabled", 0):
        doc.is_purchase_item = 0
        doc.is_sales_item = 0