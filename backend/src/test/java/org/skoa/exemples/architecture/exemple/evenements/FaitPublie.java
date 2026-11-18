package org.skoa.exemples.architecture.exemple.evenements;

import java.time.Instant;

/** Correct : un record du JDK seul. */
public record FaitPublie(String id, Instant date) {
}
