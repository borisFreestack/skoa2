package org.skoa;

import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeSet;

import org.yaml.snakeyaml.Yaml;

/**
 * Gate « conformité à la context map » : les dépendances réelles entre modules
 * correspondent aux événements déclarés dans {@code contexts/context-map.yaml}.
 *
 * <p>Conventions vérifiées :
 * <ul>
 *   <li>les événements publiés par un BC sont des records du paquet {@code org.skoa.<bc>.evenements} ;</li>
 *   <li>un BC ne dépend d'un autre BC que par ces records, et seulement pour un événement
 *       que la context map déclare de cet amont vers lui ;</li>
 *   <li>les composants d'un record d'événement sont exactement les champs de son payload
 *       (l'union des payloads quand l'événement part vers plusieurs BC).</li>
 * </ul>
 *
 * <p>La logique est séparée de l'extraction des faits (Spring Modulith) pour pouvoir prouver
 * qu'elle échoue sur des faits fabriqués ({@code ConformiteContextMapTest}).
 */
final class ConformiteContextMap {

    static final String PAQUET_EVENEMENTS = "evenements";

    record Evenement(String nom, String amont, String aval, List<String> payload) {}

    /** Un type d'un module qui dépend d'un type d'un autre module. */
    record Dependance(String moduleSource, String typeSource, String moduleCible, String typeCible) {}

    /** Un type trouvé dans un paquet {@code evenements}. */
    record TypeEvenement(String module, String nomComplet, boolean estRecord, List<String> composants) {
        String nomSimple() {
            return nomComplet.substring(nomComplet.lastIndexOf('.') + 1);
        }
    }

    private final List<Evenement> evenements;

    ConformiteContextMap(List<Evenement> evenements) {
        this.evenements = List.copyOf(evenements);
    }

    /** Identifiant de module Spring Modulith d'un BC : « mise-en-relation » devient « miseenrelation ». */
    static String module(String bc) {
        return bc.replace("-", "");
    }

    static String paquetEvenements(String module) {
        return "org.skoa." + module + "." + PAQUET_EVENEMENTS;
    }

    @SuppressWarnings("unchecked")
    static ConformiteContextMap lire(Path contextMap) throws IOException {
        Map<String, Object> racine;
        try (InputStream in = Files.newInputStream(contextMap)) {
            racine = new Yaml().load(in);
        }
        List<Evenement> evenements = new ArrayList<>();
        for (Map<String, Object> relation : (List<Map<String, Object>>) racine.get("relations")) {
            Object aval = relation.get("downstream");
            List<String> avals = aval instanceof List<?> liste ? (List<String>) liste : List.of((String) aval);
            List<Map<String, Object>> events = (List<Map<String, Object>>) relation.get("events");
            for (Map<String, Object> e : events == null ? List.<Map<String, Object>>of() : events) {
                List<String> payload = (List<String>) e.getOrDefault("payload", List.of());
                for (String a : avals) {
                    evenements.add(new Evenement((String) e.get("name"), (String) relation.get("upstream"), a, payload));
                }
            }
        }
        return new ConformiteContextMap(evenements);
    }

    List<String> verifier(List<Dependance> dependances, List<TypeEvenement> types) {
        List<String> violations = new ArrayList<>();
        Set<String> dejaSignalees = new LinkedHashSet<>();

        for (Dependance d : dependances) {
            if (d.moduleSource().equals(d.moduleCible())) {
                continue;
            }
            String paquetCible = d.typeCible().substring(0, d.typeCible().lastIndexOf('.'));
            String nomCible = d.typeCible().substring(d.typeCible().lastIndexOf('.') + 1);
            boolean declare = paquetCible.equals(paquetEvenements(d.moduleCible()))
                    && evenements.stream().anyMatch(e -> e.nom().equals(nomCible)
                            && module(e.amont()).equals(d.moduleCible())
                            && module(e.aval()).equals(d.moduleSource()));
            String cle = d.moduleSource() + "->" + d.typeCible();
            if (!declare && dejaSignalees.add(cle)) {
                violations.add("%s dépend de %s (module %s) : seule une dépendance à un événement déclaré de %s vers %s, dans le paquet %s, est permise"
                        .formatted(d.typeSource(), d.typeCible(), d.moduleCible(), d.moduleCible(), d.moduleSource(),
                                paquetEvenements(d.moduleCible())));
            }
        }

        for (TypeEvenement t : types) {
            List<Evenement> declares = evenements.stream()
                    .filter(e -> e.nom().equals(t.nomSimple()) && module(e.amont()).equals(t.module()))
                    .toList();
            if (declares.isEmpty()) {
                violations.add("%s est dans le paquet %s mais la context map ne déclare aucun événement %s publié par %s ; un événement interne n'a rien à faire là"
                        .formatted(t.nomComplet(), PAQUET_EVENEMENTS, t.nomSimple(), t.module()));
                continue;
            }
            if (!t.estRecord()) {
                violations.add("%s doit être un record : un événement publié est une donnée immuable".formatted(t.nomComplet()));
                continue;
            }
            Set<String> attendus = new TreeSet<>();
            declares.forEach(e -> attendus.addAll(e.payload()));
            Set<String> reels = new TreeSet<>(t.composants());
            if (!attendus.equals(reels)) {
                Set<String> manquants = new TreeSet<>(attendus);
                manquants.removeAll(reels);
                Set<String> enTrop = new TreeSet<>(reels);
                enTrop.removeAll(attendus);
                violations.add("%s ne suit pas son payload déclaré %s : manquants %s, en trop %s"
                        .formatted(t.nomComplet(), attendus, manquants, enTrop));
            }
        }
        return violations;
    }
}
