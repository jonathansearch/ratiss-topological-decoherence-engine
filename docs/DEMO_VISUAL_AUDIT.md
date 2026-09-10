# Vérification visuelle — démonstrations Studio Cloud

La vérification locale du 22 août 2026 confirme que les deux démonstrations Cloud affichent simultanément le design `transmon-microcell` et la cartographie WebGL RATISS. Chaque page expose le schéma de circuit, le comptage des composants et liens, les couches de proxy, la lecture fréquentielle nominale, le panneau de diaphonie nominale et la console de compilation avant la scène topologique.

| Démonstration | Panneau de conception visible | Scène WebGL visible | Contrôles confirmés |
|---|---:|---:|---|
| Trajectoire Studio → topologie | Oui | Oui | Timeline, pause, reset caméra, orbite et zoom |
| Comparaison TTF | Oui | Oui | Basculer référence/régularisation, timeline, pause, orbite et zoom |

> Ces contrôles attestent uniquement le rendu des artefacts locaux versionnés. Ils ne constituent pas une exécution QPU, une calibration électromagnétique ou une validation matérielle.

## Vue de travail complète

La page principale du Studio Cloud a aussi été contrôlée avec le design `transmon-microcell` chargé. Elle conserve les contrôles de démo, ajout de transmon, optimisation et export JSON ; les validations, couches conceptuelles, carte de fréquence, schéma, scène topologique, timeline, métriques, analyse de diaphonie et console sont toutes présentes dans la même vue. Une simulation interne a été déclenchée pour la capture de l’état calculé qui accompagne la documentation.

La feuille de style principale a été enrichie sans modifier les contrôleurs : accents turquoise, bleu, violet, ambre et rose différencient désormais les zones de conception, les métriques, la console et les vues schéma/topologie. La vérification en navigateur confirme que les contrôles restent visibles et que les textes restent lisibles sur fond sombre.

## Aperçu animé documentaire

Une séquence de captures authentiques est en préparation depuis les démos enrichies. Chaque aperçu est produit à partir du rendu réel de la page : aucun graphique, état de circuit ou résultat de timeline n’est ajouté pour les besoins de la documentation.

La seconde image de trajectoire a été capturée à l’étape `2 / 3`, porte `h(1)`, avec la signature logique affichée `0.766` et aucun itinéraire TSP à cette étape. L’animation documentaire ne modifie pas ces valeurs.

La capture terminale provient de l’étape `3 / 3`, porte `cz(0,1)`, avec la signature logique affichée `0.768` et `P_sig` de graphe `0.000`. Elle complète le cycle de trois états réels présenté par l’aperçu animé.

Pour l’aperçu d’ablation, la première image provient du scénario `ttf_smooth_baseline`. Le navigateur a ensuite basculé sur le scénario `ttf_smooth_regularized` par son contrôle de démonstration avant la seconde capture.

Les aperçus GIF Cloud ont été vérifiés après assemblage : le panneau Quantum Studio, la scène WebGL et le panneau de métriques restent lisibles à la largeur documentaire de 640 pixels.

Après la refonte topologique, la démo de trajectoire Cloud affiche bien l’anneau logique distribué, trois brins de tresse, l’arc de phase, les douze nœuds de l’anneau et les métriques `P_sig`, `phase`, `twist`, `coherence` et `protected` réellement extraites de `logical_topology`. La comparaison TTF affiche son graphe et sa provenance sans introduire de qubit logique lorsque le champ `logical_topology.P_sig` n’est pas fourni par l’artefact d’ablation.

Les nouvelles captures documentaires de la trajectoire Cloud proviennent de l’état `h(0)` (`P_sig` logique `0.765`, phase `0.785 rad`, torsion `1.571 rad`, cohérence `0.996`) et de l’état terminal `cz(0,1)` (`P_sig` logique `0.768`, phase `0.982 rad`, torsion `1.571 rad`, cohérence `0.952`). Les vues affichent le même design `transmon-microcell` dans les deux états.

Pour l’aperçu TTF Cloud actualisé, l’état initial `ttf_smooth_baseline` est comparé à l’étape terminale `ttf_smooth_correlation_regularization` : `cx(2,4)`, frontière `[4, 3]`, support topologique total `1.006`, activation lisse moyenne `0.505` et `P_sig` graphe `0.000`. La scène affiche « graphe d’inspection » et les champs logiques « non exportée » dans les deux états.

Le GIF actualisé `docs/media/cloud-trajectory-webgl-preview.gif` a été vérifié : le design Quantum Studio, l’anneau logique distribué, les trois brins de tresse, l’arc de phase et le panneau de signature logique restent visibles à la largeur d’intégration README.
