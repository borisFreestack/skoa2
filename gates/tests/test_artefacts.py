import unittest

from fixture import DepotDeTest, erreurs, glossaire, termes_de_remplissage

from skoa_gates import artefacts


class GateArtefacts(unittest.TestCase):
    def setUp(self):
        self.d = DepotDeTest()

    def tearDown(self):
        self.d.fermer()

    def verifier(self):
        return artefacts.verifier(self.d.depot())

    def test_un_depot_coherent_passe(self):
        self.assertEqual(erreurs(self.verifier()), [])

    def test_un_yaml_invalide_bloque(self):
        self.d.ecrire("contexts/alpha/glossary.yaml", "context: alpha\nterms: [\n")
        self.assertIn("YAML invalide", erreurs(self.verifier())[0])

    def test_claude_md_sans_section_de_vocabulaire_interdit_bloque(self):
        self.d.ecrire("CLAUDE.md", "# skoa\n")
        self.assertIn("introuvable", erreurs(self.verifier())[0])

    def test_un_terme_qui_interdit_un_autre_terme_du_meme_glossaire_bloque(self):
        self.d.remplacer("contexts/alpha/glossary.yaml", "[Benevole]", "[Benevole, Demande]")
        self.assertIn("Preneur interdit Demande", " ".join(erreurs(self.verifier())))

    def test_un_terme_interdit_dans_un_autre_bc_est_un_avertissement(self):
        self.d.remplacer("contexts/beta/glossary.yaml", "[Seance]", "[Seance, Preneur]")
        constats = self.verifier()
        self.assertEqual(erreurs(constats), [])
        self.assertTrue(any("beta interdit Preneur" in c.message for c in constats if not c.bloquant))

    def test_un_terme_interdit_partout_ne_peut_pas_entrer_au_glossaire(self):
        self.d.remplacer("contexts/alpha/glossary.yaml", "term: TermeA", "term: Client")
        self.assertIn("Client est interdit partout", " ".join(erreurs(self.verifier())))

    def test_un_glossaire_trop_court_bloque(self):
        self.d.ecrire("contexts/beta/glossary.yaml", glossaire("beta", [("Rencontre", [], "Rencontre"),
                                                                         *termes_de_remplissage("Mot", 3)]))
        self.assertIn("4 termes", " ".join(erreurs(self.verifier())))

    def test_un_invariant_sur_un_agregat_inconnu_bloque(self):
        self.d.remplacer("contexts/alpha/invariants.yaml", "agregat: Demande", "agregat: Ticket")
        self.assertIn("Ticket, qui n'est pas un agrégat", " ".join(erreurs(self.verifier())))

    def test_un_identifiant_d_invariant_mal_forme_bloque(self):
        self.d.remplacer("contexts/alpha/invariants.yaml", "INV-ALP-001", "INV-ALPHA-1")
        self.assertIn("format INV-XXX-NNN", " ".join(erreurs(self.verifier())))

    def test_un_evenement_declare_dans_la_context_map_mais_absent_du_context_md_bloque(self):
        self.d.remplacer("contexts/beta/CONTEXT.md", "| `DemandeAcceptee` | alpha | effet |", "")
        self.assertIn("consomme DemandeAcceptee depuis alpha, CONTEXT.md ne le dit pas", " ".join(erreurs(self.verifier())))

    def test_un_evenement_du_context_md_absent_de_la_context_map_bloque(self):
        self.d.remplacer("contexts/alpha/CONTEXT.md", "| `DemandeAcceptee` | beta |",
                         "| `DemandeAcceptee` | beta |\n| `DemandeExpiree` | beta |")
        self.assertIn("publie DemandeExpiree vers beta", " ".join(erreurs(self.verifier())))


if __name__ == "__main__":
    unittest.main()
