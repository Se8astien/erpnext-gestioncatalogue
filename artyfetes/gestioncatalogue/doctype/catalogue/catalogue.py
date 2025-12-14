import frappe
from frappe.model.document import Document
from frappe.utils.nestedset import NestedSet


class Catalogue(NestedSet):
    """
    Doctype Catalogue en mode Tree
    """

    def onload(self):
        self.set_univers_html()

    def validate(self):
        self.set_univers_html()

    def set_univers_html(self):
        """
        Affiche dynamiquement la liste des Univers
        uniquement si niveau = Catalogue
        """
        if self.niveau != "Catalogue":
            self.univers_html = ""
            return

        univers = frappe.get_all(
            "Catalogue",
            filters={
                "parent_catalogue": self.name,
                "niveau": "Univers",
                "actif": 1
            },
            fields=["name", "titre"],
            order_by="titre"
        )

        if not univers:
            self.univers_html = "<div class='text-muted'>Aucun univers actif.</div>"
            return

        html = "<h4>Univers du catalogue</h4><ul>"
        for u in univers:
            html += f"<li><a href='/app/catalogue/{u.name}'>{u.titre}</a></li>"
        html += "</ul>"

        self.univers_html = html


# 🔽 🔽 🔽
# PARTIE IMPORTANTE POUR LA TREE VIEW
# 🔽 🔽 🔽

@frappe.whitelist()
def get_children(doctype, parent=None, is_root=False):
    """
    Surcharge de la Tree View
    → n'affiche QUE les catalogues / univers actifs
    """

    filters = {
        "actif": 1
    }

    if parent:
        filters["parent_catalogue"] = parent
    else:
        filters["parent_catalogue"] = ""

    return frappe.get_all(
        "Catalogue",
        filters=filters,
        fields=[
            "name",
            "titre as title",
            "is_group"
        ],
        order_by="lft"
    )
