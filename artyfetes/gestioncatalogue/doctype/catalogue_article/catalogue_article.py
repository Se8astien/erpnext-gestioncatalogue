# Copyright (c) 2024, Votre Nom and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CatalogueArticle(Document):
    """Classe pour gérer les articles dans les univers"""
    
    def validate(self):
        """Validation avant sauvegarde"""
        self.validate_unique_article()
    
    def validate_unique_article(self):
        """Vérifie qu'un article n'est pas déjà dans cet univers"""
        if self.article:
            existing = frappe.db.exists(
                "Catalogue Article",
                {
                    "parent": self.parent,
                    "article": self.article,
                    "name": ["!=", self.name]
                }
            )
            
            if existing:
                frappe.throw(frappe._("Cet article est déjà présent dans cet univers"))