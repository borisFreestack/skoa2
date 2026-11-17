import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fichiers_proteges as fp  # noqa: E402

CODEOWNERS = """\
# commentaire
/contexts/                  @Proprio
/gates/                     @proprio
/backend/src/test/java/org/skoa/*.java  @proprio
/docs/adr/                  @proprio @autre
/docs/adr/brouillons/       @autre
*.lock                      @proprio
"""


class GateFichiersProteges(unittest.TestCase):
    regles = fp.lire_codeowners(CODEOWNERS)

    def erreurs(self, fichiers, valide_par=None):
        return [c for c in fp.verifier(self.regles, fichiers, valide_par) if c.bloquant]

    def test_un_fichier_non_protege_passe(self):
        self.assertEqual(self.erreurs(["backend/src/main/java/org/skoa/suivi/Structure.java", "docs/journal-sdlc.md"]), [])

    def test_un_dossier_protege_couvre_tout_son_contenu(self):
        self.assertEqual(len(self.erreurs(["contexts/suivi/glossary.yaml", "gates/skoa_gates/langage.py"])), 2)

    def test_un_motif_ancre_ne_couvre_pas_un_dossier_homonyme_plus_bas(self):
        self.assertEqual(self.erreurs(["frontend/src/app/contexts/x.ts"]), [])

    def test_une_etoile_ne_traverse_pas_les_dossiers(self):
        self.assertEqual(len(self.erreurs(["backend/src/test/java/org/skoa/ContextMapTest.java"])), 1)
        self.assertEqual(self.erreurs(["backend/src/test/java/org/skoa/suivi/StructureTest.java"]), [])

    def test_un_motif_sans_barre_couvre_tout_le_depot(self):
        self.assertEqual(len(self.erreurs(["frontend/package.lock"])), 1)

    def test_la_validation_d_un_proprietaire_debloque(self):
        self.assertEqual(self.erreurs(["contexts/suivi/glossary.yaml"], valide_par="proprio"), [])

    def test_le_login_n_est_pas_sensible_a_la_casse(self):
        self.assertEqual(self.erreurs(["contexts/suivi/glossary.yaml"], valide_par="PROPRIO"), [])

    def test_la_validation_d_un_non_proprietaire_ne_debloque_pas(self):
        messages = [c.message for c in self.erreurs(["gates/verifier.py"], valide_par="agent-bot")]
        self.assertEqual(len(messages), 1)
        self.assertIn("qui n'en est pas propriétaire", messages[0])

    def test_la_derniere_regle_qui_couvre_un_chemin_l_emporte(self):
        self.assertEqual(self.erreurs(["docs/adr/brouillons/idee.md"], valide_par="autre"), [])
        self.assertEqual(len(self.erreurs(["docs/adr/brouillons/idee.md"], valide_par="proprio")), 1)

    def test_le_cli_echoue_sans_validation(self):
        with tempfile.TemporaryDirectory() as d:
            co, fichiers = Path(d) / "CODEOWNERS", Path(d) / "fichiers.txt"
            co.write_text(CODEOWNERS)
            fichiers.write_text("contexts/suivi/glossary.yaml\nREADME.md\n")
            self.assertEqual(fp.main(["--codeowners", str(co), "--fichiers", str(fichiers)]), 1)
            self.assertEqual(fp.main(["--codeowners", str(co), "--fichiers", str(fichiers), "--valide-par", "proprio"]), 0)
            co.write_text("# vide\n")
            self.assertEqual(fp.main(["--codeowners", str(co), "--fichiers", str(fichiers)]), 1)

    def test_le_vrai_codeowners_protege_ce_que_claude_md_declare_en_lecture_seule(self):
        racine = Path(__file__).resolve().parents[2]
        regles = fp.lire_codeowners((racine / ".github" / "CODEOWNERS").read_text(encoding="utf-8"))
        for chemin in ["contexts/context-map.yaml", "gates/verifier.py", ".github/CODEOWNERS",
                       ".github/workflows/fichiers-proteges.yml", "CLAUDE.md", "contracts/suivi/openapi.yaml"]:
            self.assertIsNotNone(fp.proprietaires(regles, chemin), chemin)


if __name__ == "__main__":
    unittest.main()
