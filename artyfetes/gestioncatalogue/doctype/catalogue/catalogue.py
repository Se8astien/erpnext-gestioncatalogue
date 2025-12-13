# Copyright (c) 2024, Votre Nom and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils.nestedset import NestedSet

class Catalogue(NestedSet):
    """Classe pour gérer les Catalogues et Univers en structure arbre"""
    
    nsm_parent_field = 'parent_catalogue'
    
    def validate(self):
        """Validation avant sauvegarde"""
        self.validate_niveau()
        self.validate_articles()
    
    def validate_niveau(self):
        """Valide que le niveau est cohérent avec la hiérarchie"""
        if self.parent_catalogue:
            parent = frappe.get_doc("Catalogue", self.parent_catalogue)
            
            # Un Univers doit avoir un Catalogue comme parent
            if self.niveau == "Univers" and parent.niveau != "Catalogue":
                frappe.throw(_("Un Univers doit être sous un Catalogue"))
            
            # Un Catalogue ne peut pas avoir de parent Univers
            if self.niveau == "Catalogue" and parent.niveau == "Univers":
                frappe.throw(_("Un Catalogue ne peut pas être sous un Univers"))
    
    def validate_articles(self):
        """Valide que les articles ne sont ajoutés que pour les Univers"""
        if self.niveau == "Catalogue" and self.articles:
            frappe.throw(_("Les articles ne peuvent être ajoutés qu'aux Univers, pas aux Catalogues"))
    
    def on_update(self):
        """Après sauvegarde"""
        super().on_update()
        self.update_univers_list()
    
    def update_univers_list(self):
        """Met à jour la liste HTML des univers pour un Catalogue"""
        if self.niveau == "Catalogue":
            # Récupérer les univers enfants
            univers = frappe.get_all(
                "Catalogue",
                filters={
                    "parent_catalogue": self.name,
                    "niveau": "Univers"
                },
                fields=["name", "titre", "actif", "visible_sur_le_site"],
                order_by="titre asc"
            )
            
            if univers:
                html = '''
                <div class="univers-list">
                    <table class="table table-bordered table-hover">
                        <thead>
                            <tr>
                                <th style="width: 50%">Titre</th>
                                <th style="width: 15%; text-align: center;">Actif</th>
                                <th style="width: 15%; text-align: center;">Visible</th>
                                <th style="width: 20%; text-align: center;">Articles</th>
                            </tr>
                        </thead>
                        <tbody>
                '''
                
                for u in univers:
                    # Compter les articles
                    nb_articles = frappe.db.count("Catalogue Article", {"parent": u.name})
                    
                    actif_badge = '<span class="badge badge-success">✓</span>' if u.actif else '<span class="badge badge-danger">✗</span>'
                    visible_badge = '<span class="badge badge-success">✓</span>' if u.visible_sur_le_site else '<span class="badge badge-secondary">✗</span>'
                    
                    html += f'''
                        <tr>
                            <td><a href="/app/catalogue/{u.name}" target="_blank"><strong>{u.titre}</strong></a></td>
                            <td style="text-align: center;">{actif_badge}</td>
                            <td style="text-align: center;">{visible_badge}</td>
                            <td style="text-align: center;"><span class="badge badge-primary">{nb_articles}</span></td>
                        </tr>
                    '''
                
                html += '''
                        </tbody>
                    </table>
                </div>
                '''
                
                self.db_set("liste_univers_html", html, update_modified=False)
            else:
                html = '<p class="text-muted"><em>Aucun univers créé pour ce catalogue. Créez un nouveau Catalogue avec ce Catalogue comme parent et niveau = Univers.</em></p>'
                self.db_set("liste_univers_html", html, update_modified=False)
    
    def on_trash(self):
        """Avant suppression"""
        # Vérifier qu'il n'y a pas d'enfants
        children = frappe.get_all("Catalogue", filters={"parent_catalogue": self.name})
        if children:
            frappe.throw(_("Impossible de supprimer : ce catalogue a des univers enfants. Supprimez-les d'abord."))
        
        super().on_trash()


# Méthodes API publiques

@frappe.whitelist()
def get_catalogue_tree(parent=None, is_root=False, actif=None):
    """Retourne l'arbre des catalogues pour la vue arbre
    
    Args:
        parent: Parent catalogue pour filtrer les enfants
        is_root: Si True, retourne uniquement les éléments racine
        actif: Filtre sur le champ actif (1 pour actifs uniquement)
    """
    # Toujours filtrer sur actif = 1 par défaut
    filters = {"actif": 1}
    
    # Si actif est explicitement passé, l'utiliser
    if actif is not None:
        filters["actif"] = actif
    
    if is_root:
        filters["parent_catalogue"] = ""
    elif parent:
        filters["parent_catalogue"] = parent
    
    catalogues = frappe.get_all(
        "Catalogue",
        filters=filters,
        fields=["name", "titre", "niveau", "actif", "is_group", "visible_sur_le_site"],
        order_by="titre asc"
    )
    
    # Formater pour la vue arbre
    for cat in catalogues:
        cat["value"] = cat["name"]
        cat["title"] = cat["titre"]
        cat["expandable"] = cat["is_group"]
    
    return catalogues


@frappe.whitelist()
def get_univers_articles(univers_name):
    """Retourne tous les articles d'un univers"""
    articles = frappe.get_all(
        "Catalogue Article",
        filters={"parent": univers_name},
        fields=["article", "article_name", "ordre", "description"],
        order_by="ordre asc, article_name asc"
    )
    
    return articles


@frappe.whitelist()
def get_catalogue_stats():
    """Retourne des statistiques sur les catalogues"""
    stats = {
        "total_catalogues": frappe.db.count("Catalogue", {"niveau": "Catalogue", "actif": 1}),
        "total_univers": frappe.db.count("Catalogue", {"niveau": "Univers", "actif": 1}),
        "total_articles": frappe.db.count("Catalogue Article"),
    }
    
    return stats



    