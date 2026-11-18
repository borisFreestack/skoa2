package org.skoa.exemples.architecture.exemple.application;

import org.skoa.exemples.architecture.exemple.api.CodeGenere;

/** Fautive : l'application dépend du code généré depuis le contrat. */
public class ApplicationSurContrat {
    private CodeGenere genere;
}
