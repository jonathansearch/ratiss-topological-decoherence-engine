# Vérification du Studio Cloud

## Interface de conception

Le Studio Cloud a été ouvert localement. Il affiche à partir du même document Quantum Circuit Studio la validation de topologie, le schéma, les couches conceptuelles, la carte de fréquences et l’overlay de diaphonie nominale de `transmon-microcell`.

## Déclenchement de simulation

Le bouton **« Simuler avec RATISS »** transmet le document Studio courant au chemin interne `/api/simulate/studio`. La réponse attendue est une timeline RATISS avec provenance `internal_studio_import`, ainsi qu’un contexte de conception conservant le mapping des composants Studio vers les qubits logiques RATISS.

## Résultat observé

La simulation a terminé dans la même interface. Le Studio affiche l’étape initiale de la timeline, `P_sig` logique `1.214`, provenance `internal_studio_import`, le scaffold `h` sur les deux qubits plus une interaction `cz` dérivée du coupler `c0`, et le mapping `q0 → 0`, `q1 → 1`.

Le schéma de conception, les couches conceptuelles, les fréquences et le risque nominal de diaphonie restent visibles à gauche. La scène WebGL topologique, les métriques et la console de compilation restent visibles à droite. Cette vérification confirme que ces couches sont réunies dans un seul Studio Cloud, sans affirmation de calibration, d’extraction EM, de fabrication ou de validation matérielle.
