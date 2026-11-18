package org.skoa.exemples.architecture.exemple.evenements;

import org.skoa.exemples.architecture.exemple.domaine.Entite;

/** Fautif : un événement publié expose un objet du domaine. */
public record EvenementSurDomaine(Entite entite) {
}
