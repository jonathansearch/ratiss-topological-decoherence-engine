# Provenance Quantum Circuit Studio dans le Studio Cloud

Le Studio Cloud est autonome au runtime. Son modèle de conception `web/studio-model.mjs` est une copie identique du fichier `src/model.mjs` de `quantum-circuit-studio`, projet privé de Jonathan, au moment de l’intégration. L’empreinte SHA-256 des deux fichiers était :

```text
4e23c863df2695a80eee12ae065a7dab94403d286300d132285bf149c2cd0448
```

La copie est conservée parce que le Studio Cloud doit pouvoir être cloné et lancé sans installer ou cloner un second dépôt. Les modifications ultérieures du modèle source doivent être comparées explicitement avant une nouvelle synchronisation ; aucun mécanisme ne modifie le dépôt Studio source.

| Brique copiée | Usage dans le Studio Cloud | Limite maintenue |
|---|---|---|
| Modèle JSON, composants et liens | Source de conception interne | Pas un PDK, ni un masque, ni une géométrie de fabrication |
| Couches conceptuelles | Lecture et affichage du design | Pas une pile de procédé |
| Carte de fréquence et collisions | Overlay nominal de revue | Pas une calibration |
| Score de diaphonie | Priorisation visuelle de design | Pas une extraction EM |
| Optimiseur transparent | Ajustement de placement/fréquence local | Pas un solveur de routage, de rendement ou de matériel |

Le code Python `studio_import.py` est une couche RATISS nouvelle qui compile le document JSON vers un scaffold logique `H`/`CZ` explicitement déclaré. Cette compilation ne change ni n’étend le modèle Studio source.
