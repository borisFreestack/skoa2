package org.skoa.exemples.architecture.exemple.domaine;

import java.time.Instant;
import java.util.List;

import org.skoa.exemples.architecture.exemple.evenements.FaitPublie;

/** Correcte : ne dépend que du JDK, du domaine et des événements du BC. */
public class Entite {
    private final List<String> etiquettes = List.of();
    private final int[] compteurs = new int[0];

    public FaitPublie publier() {
        return new FaitPublie("1", Instant.EPOCH);
    }
}
