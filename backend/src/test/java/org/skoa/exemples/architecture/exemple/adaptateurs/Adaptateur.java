package org.skoa.exemples.architecture.exemple.adaptateurs;

import org.skoa.exemples.architecture.exemple.api.CodeGenere;
import org.skoa.exemples.architecture.exemple.application.CasDUsage;

/** Correcte : un adaptateur implémente le contrat et appelle l'application. */
public class Adaptateur implements CodeGenere {
    private CasDUsage casDUsage;
}
