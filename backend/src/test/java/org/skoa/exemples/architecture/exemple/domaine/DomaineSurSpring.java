package org.skoa.exemples.architecture.exemple.domaine;

import org.springframework.context.ApplicationEventPublisher;

/** Fautive : le domaine dépend de Spring. */
public class DomaineSurSpring {
    private ApplicationEventPublisher publication;
}
