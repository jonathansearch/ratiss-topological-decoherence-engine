# Guide d’intégration

## Intégrer le moteur dans un projet Python local

```python
import json
from pathlib import Path
from ratiss_topological_decoherence import SimulationConfig, run_local_demo

config = SimulationConfig(criticality_threshold=0.38)
artifact = run_local_demo(config)
Path("full_timeline.json").write_text(json.dumps(artifact, indent=2), encoding="utf-8")
```

La manière la plus sûre d’intégrer le SDK consiste à préserver l’artefact complet et sa provenance. Le visualiseur, un rapport ou une application aval ne doit pas copier seulement les valeurs graphiques, car les limites de portée se trouvent dans `provenance`.

## Charger dans l’atlas local

1. Cloner ou télécharger `ratiss-decoherence-atlas`.
2. Ouvrir `index.html` directement dans le navigateur.
3. Choisir le fichier `full_timeline.json` produit par le moteur.
4. Utiliser le curseur temporel et le clic de nœud pour l’inspection.

L’atlas n’a besoin ni de serveur, ni de token, ni de connexion active. Three.js est inclus localement dans `vendor/`.

## Ajouter un adaptateur externe

Un adaptateur externe est délibérément séparé du moteur. Sa responsabilité est de convertir un résultat externe — par exemple des comptes dans les bases X/Y/Z, ou une matrice densité fournie par un autre simulateur — vers le contrat d’artefact. Il ne doit pas modifier la sémantique de `P_sig`, ni convertir une soumission en preuve de validation.

| Exigence d’adaptateur | Raison |
|---|---|
| Jetons uniquement dans l’environnement local de l’utilisateur | Aucun secret dans le code ou les artefacts |
| `provenance.mode` distinct (`adapter_import`, `hardware_import`, etc.) | Traçabilité de l’origine des données |
| `validated_on_hardware` à `true` seulement avec source, backend, date, shots et identifiant de job documentés | Empêcher les revendications automatiques |
| Écrire le modèle de mesure dans l’artefact | Rendre l’analyse contestable et reproductible |

## Utiliser la pipeline sur d’autres phénomènes

Le même contrat peut représenter une trajectoire de relations ou de corrélations fournie par un autre domaine, à condition de documenter la méthode qui produit le cube, la signification des nœuds et la normalisation. La topologie et le TSP deviennent alors des outils d’inspection de données structurées. Cette extensibilité ne transforme pas le SDK en appareil de mesure ni en outil de diagnostic.
