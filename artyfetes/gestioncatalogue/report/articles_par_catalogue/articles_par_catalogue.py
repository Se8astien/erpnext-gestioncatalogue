import frappe
from frappe import _

def execute(filters=None):
    """
    Script Report pour lister tous les Articles actifs avec leurs Catalogues / Univers
    """
  
    # Récupérer tous les articles actifs
    items = frappe.get_all("Item", 
        filters={"disabled": 0}, 
        fields=["name", "item_name"],
        order_by="item_name"
    )
      
    item_catalogues = {}
    max_catalogues = 0

    # Construire la liste des catalogues pour chaque article
    for item in items:
        # Récupérer tous les liens Catalogue Article
        links = frappe.get_all("Catalogue Article", 
            filters={"article": item.name}, 
            fields=["parent"]
        )
        
        catalogues = []
        for l in links:
            # Récupérer les données du Catalogue/Univers
            cat_data = frappe.db.get_value("Catalogue", l.parent,
                ["titre", "actif", "visible_sur_site", "niveau"],
                as_dict=True
            )
            
            if not cat_data:
                frappe.log_error(f"Catalogue introuvable pour parent: {l.parent}")
                continue
                
            if cat_data and cat_data["actif"]:
                # Format : "Titre (Type) - Visible/Non Visible"
                visibility = "Visible" if cat_data["visible_sur_site"] else "Non Visible"
                catalogues.append(f"{cat_data['titre']} - {visibility}")

        item_catalogues[item.name] = catalogues
        if len(catalogues) > max_catalogues:
            max_catalogues = len(catalogues)

    # Construire les colonnes au format DICTIONNAIRE (requis pour ERPNext v13+)
    columns = [
        {
            "fieldname": "item_code",
            "label": _("Code Article"),
            "fieldtype": "Link",
            "options": "Item",
            "width": 150
        },
        {
            "fieldname": "item_name",
            "label": _("Désignation"),
            "fieldtype": "Data",
            "width": 250
        }
    ]
    
    # Ajouter dynamiquement les colonnes pour chaque catalogue
    for i in range(1, max_catalogues + 1):
        columns.append({
            "fieldname": f"catalogue_{i}",
            "label": _(f"Catalogue / Univers {i}"),
            "fieldtype": "Data",
            "width": 300
        })

    # Construire les lignes au format DICTIONNAIRE
    data = []
    for item in items:
        row = {
            "item_code": item.name,
            "item_name": item.item_name
        }
        
        # Ajouter les catalogues
        catalogues = item_catalogues.get(item.name, [])
        for i, cat in enumerate(catalogues, start=1):
            row[f"catalogue_{i}"] = cat
        
        # Remplir les colonnes vides
        for i in range(len(catalogues) + 1, max_catalogues + 1):
            row[f"catalogue_{i}"] = ""
        
        data.append(row)

    return columns, data


def get_report_summary(data, filters):
    """Génère un résumé en haut du report"""
    if not data:
        return []
    
    # Compter les articles avec/sans catalogue
    articles_avec_catalogue = len([d for d in data if d.get("catalogue_1")])
    articles_sans_catalogue = len(data) - articles_avec_catalogue
    
    return [
        {
            "value": len(data),
            "label": _("Total Articles"),
            "datatype": "Int",
            "indicator": "Blue"
        },
        {
            "value": articles_avec_catalogue,
            "label": _("Avec Catalogue"),
            "datatype": "Int",
            "indicator": "Green"
        },
        {
            "value": articles_sans_catalogue,
            "label": _("Sans Catalogue"),
            "datatype": "Int",
            "indicator": "Orange"
        }
    ]