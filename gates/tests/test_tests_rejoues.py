import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import tests_rejoues as tr  # noqa: E402
from tests_rejoues import Passe, Statut  # noqa: E402

PAQUETS = ["miseenrelation", "rencontre", "suivi"]
ANCIEN = ("org.skoa.miseenrelation.domaine.DemandeTest", "INV-MER-001 une Demande a un service")
NOUVEAU = ("org.skoa.miseenrelation.domaine.DemandeTest", "INV-MER-005 jamais sollicité pour sa propre Demande")
GATE_RACINE = ("org.skoa.ArchitectureHexagonaleTest", "unDomaineQuiDependDeSpringBloque()")


class GateTestsRejoues(unittest.TestCase):

    def juger(self, tete, base, rejouee):
        return tr.juger(Passe(tete), Passe(base), rejouee, PAQUETS)

    def test_un_nouveau_test_rouge_sur_la_base_passe(self):
        constats, rouges = self.juger({ANCIEN: Statut.PASSE, NOUVEAU: Statut.PASSE}, {ANCIEN: Statut.PASSE},
                                      Passe({ANCIEN: Statut.PASSE, NOUVEAU: Statut.ECHOUE}))
        self.assertEqual(constats, [])
        self.assertEqual(len(rouges), 1)

    def test_un_nouveau_test_deja_vert_sur_la_base_bloque(self):
        constats, _ = self.juger({NOUVEAU: Statut.PASSE}, {}, Passe({NOUVEAU: Statut.PASSE}))
        self.assertEqual(len(constats), 1)
        self.assertIn("passe déjà sur la branche de base", constats[0].message)
        self.assertEqual(constats[0].chemin, "backend/src/test/java/org/skoa/miseenrelation/domaine/DemandeTest.java")

    def test_un_nouveau_test_ignore_sur_la_base_bloque(self):
        constats, _ = self.juger({NOUVEAU: Statut.IGNORE}, {}, Passe({NOUVEAU: Statut.IGNORE}))
        self.assertIn("ignoré", constats[0].message)

    def test_un_nouveau_test_absent_de_la_passe_rejouee_bloque(self):
        constats, _ = self.juger({NOUVEAU: Statut.PASSE}, {}, Passe({}))
        self.assertIn("pas été exécuté", constats[0].message)

    def test_un_test_qui_ne_compile_pas_sans_le_code_de_la_pr_est_rouge(self):
        constats, rouges = self.juger({NOUVEAU: Statut.PASSE}, {}, Passe({}, compilation_echouee=True))
        self.assertEqual(constats, [])
        self.assertIn("ne compile pas", rouges[0])

    def test_un_test_qui_existait_n_est_pas_rejuge(self):
        constats, rouges = self.juger({ANCIEN: Statut.PASSE}, {ANCIEN: Statut.PASSE}, Passe({ANCIEN: Statut.PASSE}))
        self.assertEqual((constats, rouges), ([], []))

    def test_un_test_de_gate_a_la_racine_n_est_pas_juge(self):
        constats, rouges = self.juger({GATE_RACINE: Statut.PASSE}, {}, Passe({GATE_RACINE: Statut.PASSE}))
        self.assertEqual((constats, rouges), ([], []))

    def test_le_chemin_d_une_classe_imbriquee_est_celui_de_son_fichier(self):
        self.assertEqual(tr.chemin_du_test("org.skoa.suivi.domaine.StructureTest$Creation"),
                         "backend/src/test/java/org/skoa/suivi/domaine/StructureTest.java")

    def test_seuls_les_tests_des_bc_declenchent_la_gate(self):
        self.assertTrue(tr.touche_les_tests(["backend/src/test/java/org/skoa/rencontre/domaine/RencontreTest.java"], PAQUETS))
        self.assertFalse(tr.touche_les_tests(["backend/src/test/java/org/skoa/ArchitectureTest.java",
                                              "backend/src/main/java/org/skoa/rencontre/domaine/Rencontre.java",
                                              "docs/journal-sdlc.md"], PAQUETS))

    def test_les_rapports_junit_donnent_un_statut_par_test(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "TEST-org.skoa.suivi.domaine.StructureTest.xml").write_text("""<?xml version="1.0"?>
<testsuite name="org.skoa.suivi.domaine.StructureTest">
  <testcase name="vert()" classname="org.skoa.suivi.domaine.StructureTest"/>
  <testcase name="rouge()" classname="org.skoa.suivi.domaine.StructureTest"><failure message="x"/></testcase>
  <testcase name="erreur()" classname="org.skoa.suivi.domaine.StructureTest"><error message="x"/></testcase>
  <testcase name="ignore()" classname="org.skoa.suivi.domaine.StructureTest"><skipped/></testcase>
</testsuite>""", encoding="utf-8")
            resultats = tr.lire_resultats(Path(d))
        classe = "org.skoa.suivi.domaine.StructureTest"
        self.assertEqual(resultats, {(classe, "vert()"): Statut.PASSE, (classe, "rouge()"): Statut.ECHOUE,
                                     (classe, "erreur()"): Statut.ECHOUE, (classe, "ignore()"): Statut.IGNORE})


if __name__ == "__main__":
    unittest.main()
