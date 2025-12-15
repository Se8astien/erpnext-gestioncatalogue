# Copyright (c) 2025, Sébastien and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

class TestCatalogue(FrappeTestCase):
    """Tests pour le DocType Catalogue"""
    
    def setUp(self):
        #pass
        print("Init")

    def tearDown(self):
        """Exécuté après chaque test - Nettoie les données"""
        frappe.db.rollback()
    
    def test_create_catalogue(self):
        """Test 1 : Créer un catalogue simple"""
        catalogue = frappe.get_doc({
            "doctype": "Catalogue",
            "titre": "Test Catalogue 1",
            "niveau": "Catalogue",
            "actif": 1,
            "visible_sur_le_site": 1
        })
        
        catalogue.insert()
        
        # Vérifications
        self.assertEqual(catalogue.titre, "Test Catalogue 1")
        self.assertEqual(catalogue.niveau, "Catalogue")
        self.assertTrue(catalogue.actif)
        
        print("Test 1 ok : Catalogue créé")
    
    def test_create_univers(self):
        """Test 2 : Créer un univers sous un catalogue"""
        # Créer le catalogue parent
        catalogue = frappe.get_doc({
            "doctype": "Catalogue",
            "titre": "Catalogue Parent",
            "niveau": "Catalogue",
            "actif": 1
        })
        catalogue.insert()
        
        # Créer l'univers enfant
        univers = frappe.get_doc({
            "doctype": "Catalogue",
            "titre": "Univers Enfant",
            "niveau": "Univers",
            "parent_catalogue": catalogue.name,
            "actif": 1
        })
        univers.insert()
        
        # Vérifications
        self.assertEqual(univers.niveau, "Univers")
        self.assertEqual(univers.parent_catalogue, catalogue.name)
        
        print("Test 2 réussi : Univers créé sous catalogue")
    

    
    def test_add_articles_to_univers(self):
        """Test 3 : Ajouter des articles à un univers"""
        # Créer un article de test
        if not frappe.db.exists("Item", "TEST-ITEM-001"):
            item = frappe.get_doc({
                "doctype": "Item",
                "item_code": "TEST-ITEM-001",
                "item_name": "Article de Test",
                "stock_uom": "Nos",
                "item_group": "Products"
            })
            item.insert()
        
        # Créer catalogue et univers
        catalogue = frappe.get_doc({
            "doctype": "Catalogue",
            "titre": "Catalogue Articles",
            "niveau": "Catalogue",
            "actif": 1
        })
        catalogue.insert()
        
        univers = frappe.get_doc({
            "doctype": "Catalogue",
            "titre": "Univers Articles",
            "niveau": "Univers",
            "parent_catalogue": catalogue.name,
            "actif": 1,
            "articles": [
                {
                    "article": "TEST-ITEM-001",
                    "ordre": 1
                }
            ]
        })
        univers.insert()
        
        # Vérifications
        self.assertEqual(len(univers.articles), 1)
        self.assertEqual(univers.articles[0].article, "TEST-ITEM-001")
        
        print("Test 3 réussi : Articles ajoutés à l'univers")
    

    def test_actif_filter(self):
        """Test 4 : Filtrer uniquement les catalogues actifs"""
        # Créer un catalogue actif
        cat_actif = frappe.get_doc({
            "doctype": "Catalogue",
            "titre": "Catalogue Actif",
            "niveau": "Catalogue",
            "actif": 1
        })
        cat_actif.insert()
        
        # Créer un catalogue inactif
        cat_inactif = frappe.get_doc({
            "doctype": "Catalogue",
            "titre": "Catalogue Inactif",
            "niveau": "Catalogue",
            "actif": 0
        })
        cat_inactif.insert()
        
        # Récupérer uniquement les actifs
        actifs = frappe.get_all("Catalogue", filters={"actif": 1})
        
        # Vérifications
        self.assertGreaterEqual(len(actifs), 1)
        
        print("Test 4 réussi : Filtrage sur actif fonctionne")
    


# Fonction pour lancer tous les tests manuellement
def run_all_tests():
    """Lance tous les tests manuellement"""
    import unittest
    
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCatalogue)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result