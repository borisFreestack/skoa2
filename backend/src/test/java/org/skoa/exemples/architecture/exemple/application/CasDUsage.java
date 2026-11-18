package org.skoa.exemples.architecture.exemple.application;

import org.springframework.context.ApplicationEventPublisher;

import org.skoa.exemples.architecture.exemple.domaine.Entite;

/** Correcte : l'application orchestre le domaine et peut dépendre de Spring. */
public class CasDUsage {
    private ApplicationEventPublisher publication;
    private Entite entite;
}
