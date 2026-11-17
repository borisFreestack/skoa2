import unittest

from fixture import DepotDeTest, erreurs

from skoa_gates import invariants

AGREGAT = "backend/src/main/java/org/skoa/alpha/Demande.java"
TEST = "backend/src/test/java/org/skoa/alpha/DemandeTest.java"


class GateInvariants(unittest.TestCase):
    def setUp(self):
        self.d = DepotDeTest()

    def tearDown(self):
        self.d.fermer()

    def verifier(self):
        return invariants.verifier(self.d.depot())

    def test_un_invariant_dont_l_agregat_n_est_pas_ecrit_est_en_attente(self):
        constats = self.verifier()
        self.assertEqual(erreurs(constats), [])
        self.assertTrue(any("INV-ALP-001 en attente" in c.message for c in constats))

    def test_un_agregat_ecrit_sans_test_bloque(self):
        self.d.ecrire(AGREGAT, "package org.skoa.alpha;\npublic class Demande {}\n")
        self.assertIn("INV-ALP-001 (Demande) n'est cité par aucun test", erreurs(self.verifier())[0])

    def test_un_test_qui_cite_l_invariant_dans_son_nom_le_couvre(self):
        self.d.ecrire(AGREGAT, "package org.skoa.alpha;\npublic class Demande {}\n")
        self.d.ecrire(TEST, 'class DemandeTest {\n  @DisplayName("INV-ALP-001 un seul Preneur")\n  void t() {}\n}\n')
        self.assertEqual(erreurs(self.verifier()), [])

    def test_un_spec_angular_du_bc_compte(self):
        self.d.ecrire(AGREGAT, "package org.skoa.alpha;\npublic record Demande() {}\n")
        self.d.ecrire("frontend/src/app/alpha/demande.spec.ts", "it('INV-ALP-001 un seul Preneur', () => {});\n")
        self.assertEqual(erreurs(self.verifier()), [])

    def test_une_citation_en_commentaire_ne_compte_pas(self):
        self.d.ecrire(AGREGAT, "package org.skoa.alpha;\npublic class Demande {}\n")
        self.d.ecrire(TEST, "class DemandeTest {\n  // INV-ALP-001\n  void t() {}\n}\n")
        self.assertEqual(len(erreurs(self.verifier())), 1)

    def test_un_agregat_cite_seulement_en_commentaire_n_est_pas_ecrit(self):
        self.d.ecrire(AGREGAT, "package org.skoa.alpha;\n// la class Demande viendra plus tard\n")
        self.assertEqual(erreurs(self.verifier()), [])

    def test_un_identifiant_inconnu_bloque(self):
        self.d.ecrire(TEST, 'class DemandeTest { @DisplayName("INV-ALP-999 rien") void t() {} }\n')
        self.assertIn("INV-ALP-999 n'existe dans aucun", erreurs(self.verifier())[0])

    def test_un_bc_ne_prouve_pas_les_regles_d_un_autre(self):
        self.d.ecrire(TEST, 'class DemandeTest { @DisplayName("INV-BET-001 deux") void t() {} }\n')
        self.assertIn("invariant de beta, pas de alpha", erreurs(self.verifier())[0])


if __name__ == "__main__":
    unittest.main()
