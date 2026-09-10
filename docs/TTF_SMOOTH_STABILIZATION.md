# Régularisation lisse TTF — ablation expérimentale

Le Studio Cloud ajoute une **ablation de régularisation de graphe** inspirée de deux éléments réellement documentés dans le Preprint 2 : la persistance est lue sur une représentation relationnelle TTF plutôt que sur des coordonnées brutes, et les deux régimes enregistrés doivent rester séparés. Le sweep `shell_ttf_brain.json` contient `P_sig = 2.0524951073` aux seuils `max_edge` 2.5 et 3.0 ; le contrôle à graphe fixe atteint `1.4639`. Ces valeurs servent ici de **références documentaires de protocole**, jamais de cible universelle, de seuil de correction ou de valeur à forcer.

## Contrat algorithmique

À chaque étape, le module calcule une variation de corrélation par nœud :

```text
variation(i) = mean_j |M[k,i,j] - M[k-1,i,j]|
```

Les nœuds ayant les plus fortes variations deviennent la **frontière d’inspection**. La route TSP est alors calculée sur ce sous-ensemble, et non sur tous les nœuds. Ce choix réduit la taille de l’entrée TSP pour les cas où la frontière est petite ; il ne garantit pas une accélération fixe et ne change pas le calcul de `P_sig`.

La régularisation applique sur les arêtes incidentes à cette frontière un gain borné et lisse :

```text
a(i) = 0.5 × (1 + tanh(slope × (variation(i) - threshold)))
M'[i,j] = M[i,j] + strength × max(a(i), a(j)) × (1 - M[i,j])
```

`M'` reste symétrique, bornée dans `[0,1]` et sa diagonale vaut `1`. Le gain est appliqué au **graphe de corrélations exporté**, pas à une matrice densité, à des pulses, à un code de correction quantique ou à un QPU. Toute variation de Betti, `P_sig`, criticité ou route observée dans la timeline régularisée est donc un **résultat de cette ablation logicielle**.

## Livrables

Le générateur produit deux artefacts distincts : une timeline de référence et une timeline régularisée. La seconde inclut les paramètres, les nœuds de frontière, les variations, la liste d’arêtes modifiées et la provenance `ttf_smooth_correlation_regularization`. Le Studio Personnel doit afficher ces informations comme une comparaison de scénarios, sans employer les termes « protection », « correction d’erreur », « bouclier » ou « stabilisation de qubit physique » comme conclusions.
