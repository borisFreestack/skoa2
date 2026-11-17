import unittest

from fixture import DepotDeTest, erreurs

from skoa_gates import langage

ALPHA = "backend/src/main/java/org/skoa/alpha/"
BETA = "backend/src/main/java/org/skoa/beta/"


class GateLangage(unittest.TestCase):
    def setUp(self):
        self.d = DepotDeTest()

    def tearDown(self):
        self.d.fermer()

    def verifier(self):
        return erreurs(langage.verifier(self.d.depot()))

    def test_un_terme_interdit_partout_dans_un_identifiant_bloque(self):
        self.d.ecrire(ALPHA + "Fiche.java", "package org.skoa.alpha;\nclass Fiche {\n  String nomDuPatient;\n}\n")
        messages = self.verifier()
        self.assertEqual(len(messages), 1)
        self.assertIn("« nomDuPatient » contient « Patient »", messages[0])

    def test_le_constat_donne_la_ligne(self):
        self.d.ecrire(ALPHA + "Fiche.java", "package org.skoa.alpha;\n\nclass Fiche {\n  int aidantId;\n}\n")
        constats = langage.verifier(self.d.depot())
        self.assertEqual(constats[0].ligne, 4)

    def test_un_terme_interdit_partout_bloque_aussi_hors_bc(self):
        self.d.ecrire("frontend/src/app/app.ts", "export class ListeClients {}\n")
        self.assertIn("« ListeClients » contient « Client »", self.verifier()[0])

    def test_les_commentaires_et_les_chaines_ne_sont_pas_juges(self):
        self.d.ecrire(ALPHA + "Fiche.java",
                      "package org.skoa.alpha;\n// pas de Patient ici\n/* ni d'Aidant */\n"
                      "class Fiche { String s = \"un Client\"; }\n")
        self.assertEqual(self.verifier(), [])

    def test_un_nom_importe_d_une_bibliotheque_n_est_pas_juge(self):
        self.d.ecrire("frontend/src/app/app.config.ts",
                      "import { provideHttpClient } from '@angular/common/http';\n"
                      "export const c = [provideHttpClient()];\n")
        self.assertEqual(self.verifier(), [])

    def test_un_nom_qu_on_choisit_est_juge_meme_s_il_imite_une_bibliotheque(self):
        self.d.ecrire("frontend/src/app/app.config.ts",
                      "import { provideHttpClient as fournirClient } from '@angular/common/http';\n")
        self.assertIn("fournirClient", self.verifier()[0])

    def test_un_synonyme_refuse_bloque_dans_son_bc(self):
        self.d.ecrire(ALPHA + "Requete.java", "package org.skoa.alpha;\nrecord Requete() {}\n")
        self.assertIn("synonyme refusé de Demande (alpha)", self.verifier()[0])

    def test_un_synonyme_refuse_d_un_bc_est_libre_dans_un_autre(self):
        self.d.ecrire(BETA + "Requete.java", "package org.skoa.beta;\nrecord Requete() {}\n")
        self.assertEqual(self.verifier(), [])

    def test_un_terme_du_glossaire_qui_contient_un_mot_interdit_passe(self):
        self.d.ecrire(ALPHA + "Motif.java", "package org.skoa.alpha;\nenum Motif { BesoinDEnParler }\n")
        self.assertEqual(self.verifier(), [])

    def test_le_mot_interdit_hors_du_terme_autorise_bloque(self):
        self.d.ecrire(ALPHA + "Motif.java", "package org.skoa.alpha;\nenum Motif { BesoinDEnParler, BesoinUrgent }\n")
        messages = self.verifier()
        self.assertEqual(len(messages), 1)
        self.assertIn("BesoinUrgent", messages[0])

    def test_les_tests_du_bc_sont_juges(self):
        self.d.ecrire("backend/src/test/java/org/skoa/alpha/DemandeTest.java",
                      "package org.skoa.alpha;\nclass DemandeTest { void unBenevoleAccepte() {} }\n")
        self.assertIn("unBenevoleAccepte", self.verifier()[0])

    def test_une_propriete_de_contrat_interdite_bloque(self):
        self.d.ecrire("contracts/alpha/openapi.yaml",
                      "openapi: 3.0.3\npaths:\n  /requetes/{id}:\n    get:\n      operationId: lireDemande\n"
                      "components:\n  schemas:\n    Demande:\n      properties:\n        besoin:\n"
                      "          type: string\n          description: Le Patient peut tout écrire ici.\n"
                      "          minimum: 3\n")
        messages = self.verifier()
        self.assertEqual(len(messages), 2, messages)
        self.assertIn("« requetes »", messages[0] + messages[1])
        self.assertIn("« besoin »", messages[0] + messages[1])

    def test_le_code_ignore_par_git_n_est_pas_juge(self):
        self.d.ecrire(".gitignore", "/frontend/src/app/*/api/\n")
        self.d.ecrire("frontend/src/app/alpha/api/models.ts", "export interface Client {}\n")
        self.assertEqual(self.verifier(), [])


if __name__ == "__main__":
    unittest.main()
