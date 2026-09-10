"""Transparent TSP route for inspecting critical nodes; never used for P_sig."""

from __future__ import annotations

from itertools import combinations

import numpy as np


def _distance_matrix(points: np.ndarray) -> np.ndarray:
    delta = points[:, None, :] - points[None, :, :]
    return np.linalg.norm(delta, axis=2)


def _held_karp_cycle(distance: np.ndarray) -> tuple[list[int], float]:
    n = len(distance)
    dp: dict[tuple[int, int], tuple[float, int]] = {}
    for end in range(1, n):
        dp[(1 | (1 << end), end)] = (float(distance[0, end]), 0)
    for subset_size in range(3, n + 1):
        for members in combinations(range(1, n), subset_size - 1):
            subset = 1
            for member in members:
                subset |= 1 << member
            for end in members:
                previous = subset ^ (1 << end)
                cost, parent = min(
                    ((dp[(previous, candidate)][0] + float(distance[candidate, end]), candidate) for candidate in members if candidate != end),
                    default=(float("inf"), -1),
                )
                dp[(subset, end)] = (cost, parent)
    complete = (1 << n) - 1
    total_cost, end = min((dp[(complete, candidate)][0] + float(distance[candidate, 0]), candidate) for candidate in range(1, n))
    route = [end]
    subset = complete
    while end != 0:
        parent = dp[(subset, end)][1]
        subset ^= 1 << end
        route.append(parent)
        end = parent
    route.reverse()
    return route + [0], float(total_cost)


def _two_opt(route: list[int], distance: np.ndarray) -> list[int]:
    improved = True
    while improved:
        improved = False
        for start in range(1, len(route) - 2):
            for end in range(start + 1, len(route) - 1):
                a, b, c, d = route[start - 1], route[start], route[end], route[end + 1]
                if distance[a, c] + distance[b, d] + 1e-12 < distance[a, b] + distance[c, d]:
                    route[start : end + 1] = reversed(route[start : end + 1])
                    improved = True
    return route


def inspection_route(coordinates: list[list[float]], node_ids: list[int]) -> dict[str, object]:
    """Return a closed inspection route, exact for <= 10 nodes.

    The output declares its method so a later renderer never implies an exact
    route when the deterministic heuristic was used.
    """

    unique = sorted(set(int(node_id) for node_id in node_ids))
    if len(unique) < 2:
        return {"path": unique, "cost": 0.0, "method": "trivial", "nodes": unique}
    points = np.asarray([coordinates[node] for node in unique], dtype=float)
    distance = _distance_matrix(points)
    if len(unique) <= 10:
        local_route, cost = _held_karp_cycle(distance)
        method = "held_karp_exact"
    else:
        remaining = set(range(1, len(unique)))
        local_route = [0]
        while remaining:
            current = local_route[-1]
            next_node = min(remaining, key=lambda candidate: (distance[current, candidate], candidate))
            local_route.append(next_node)
            remaining.remove(next_node)
        local_route.append(0)
        local_route = _two_opt(local_route, distance)
        cost = float(sum(distance[local_route[idx], local_route[idx + 1]] for idx in range(len(local_route) - 1)))
        method = "nearest_neighbor_2opt"
    return {"path": [unique[index] for index in local_route], "cost": round(float(cost), 9), "method": method, "nodes": unique}
