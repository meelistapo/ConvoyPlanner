#!/usr/bin/env python
# -*- coding: utf-8 -*-
from itertools import islice
import networkx as nx
import itertools
import numpy as np

'''
Exhaustive fixed-order method predefined fixed-order method
'''


def common_edge(path1, path2, node):
    canditates1 = get_neighbors(path1, node)
    canditates2 = get_neighbors(path2, node)
    return bool(set(canditates1) & set(canditates2))


def common_direction(path1, path2, node):
    if node in path1 and node in path2:
        index1 = path1.index(node)
        index2 = path2.index(node)
        if index1 != 0 and index2 != 0:
            if path1[index1 - 1] == path2[index2 - 1]:
                return True
        if index1 != len(path1) - 1 and index2 != len(path2) - 1:
            if path1[index1 + 1] == path2[index2 + 1]:
                return True
    return False


def get_neighbors(path, node):
    if node in path:
        index = path.index(node)
        canditates = []
        if index == 0:
            canditates.append(path[1])
        elif index == len(path) - 1:
            canditates.append(path[len(path) - 2])
        else:
            canditates.append(path[index - 1])
            canditates.append(path[index + 1])
        return canditates
    return None


def before_and_after(path, node):
    if node in path:
        index = path.index(node)
        before = None
        after = None
        if index == 0:
            after = path[1]
        elif index == len(path) - 1:
            before = path[len(path) - 2]
        else:
            before = path[index - 1]
            after =path[index + 1]
        return before, after
    return None


def collision_check(graph, selected_convoy, convoy, selected_path, path, node, headway):
    start = arrival_time(graph, node, path[0], convoy, path[2])
    end = start + convoy.length / convoy.speed + headway
    selected_start = arrival_time(graph, node, selected_path[0], convoy, selected_path[2])
    selected_end = selected_start + selected_convoy.length / selected_convoy.speed + headway
    if start <= selected_start < end or selected_start <= start < selected_end:
        return True
    return False


def paths_touch(coordinates, path1, path2, node):
    if node in path1 and node in path2:
        index1 = path1.index(node)
        index2 = path2.index(node)
        # if both paths have nodes before and after common node
        if index1 != 0 and index1 != len(path1) - 1 and index2 != 0 and index2 != len(path2) - 1:
            # if both nodes are on the same side
            return side(coordinates, path1[index1 - 1], path1[index1 + 1], path2[index2 - 1]) == side(coordinates, path1[index1 - 1], path1[index1 + 1], path2[index2 + 1])
    return False


def parallel(path1, path2, node):
    if node in path1 and node in path2:
        before1, after1 = before_and_after(path1, node)
        before2, after2 = before_and_after(path2, node)

        if after1 is None or before2 is None:
            return before1 == after2
        elif before1 is None or after2 is None:
            return before2 == after1
        else:
            return before1 == after2 and before2 == after1
    return False


def check_conflict(graph, selected_path_data, path_data, node, selected_convoy, convoy, headway):
    if node == selected_path_data[0][0] or node == selected_path_data[0][-1] or node == path_data[0][0] or node == path_data[0][-1]:
        return False
    elif collision_check(graph, selected_convoy, convoy, selected_path_data, path_data, node, headway):
        return True
    return False


def arrival_time(graph, node, path, convoy, start):
    if node not in path:
        return False
    elif path[0] == node:
        return start
    else:
        time = start
        for i in range(1, len(path)):
            time += graph[path[i - 1]][path[i]]['weight'] / convoy.speed
            if path[i] == node:
                return time


def calculate_path_cost(G, path):
    cost = 0
    for i in range(len(path)):
        if i > 0:
            cost += G[path[i - 1]][path[i]]['weight']
    return cost


def k_shortest_paths(graph, source, target, speed, k, start, weight=None):
    paths = []
    routes = list(islice(nx.shortest_simple_paths(graph, source, target, weight='weight'), start + k))

    for i in range(start, len(routes)):
        paths.append({'path': routes[i], 'cost': calculate_path_cost(graph, routes[i]) / speed})
    return paths


# determining if three points are listed in a counterclockwise order
def ccw(coordinates, path):
    a = path[0]
    b = path[1]
    c = path[2]
    if (coordinates[c][1] - coordinates[a][1]) * (coordinates[b][0] - coordinates[a][0]) > (
                coordinates[b][1] - coordinates[a][1]) * (coordinates[c][0] - coordinates[a][0]):
        return True
    return False


def side(coordinates, line1, line2, point):
    # v1 = [coordinates[line2][0] - coordinates[line1][0], coordinates[line2][1] - coordinates[line1][1]]  # Vector 1
    # v2 = [coordinates[line2][0] - coordinates[point][0], coordinates[line2][1] - coordinates[point][1]]  # Vector 2
    # xp = v1[0] * v2[1] - v1[1] * v2[0]  # Cross product
    xp = (coordinates[line2][0]-coordinates[line1][0])*(coordinates[point][1]-coordinates[line1][1])- \
         (coordinates[line2][1]-coordinates[line1][1])*(coordinates[point][0]-coordinates[line2][0])
    if xp > 0:
        return 'left'
    elif xp < 0:
        return 'right'
    else:
        return 'on the same line'


def find_feasible_paths(graph, convoys):
    paths = []
    for i in convoys:
        path = k_shortest_paths(graph, i.origin, i.destination, i.speed, 1, 0, weight='weight')
        paths.append([[path[0]['path'], path[0]['cost'], i.ready_time, int(i.id),i]])
    return paths


def calculate(g, convoys, headway, method):
    paths = find_feasible_paths(g, convoys)
    best_collection = None
    best_ub = np.math.inf
    if method == 'EFO':
        ordering = [list(item) for item in itertools.permutations(paths)]
        for o in ordering:
            ub, collection = solve(g, headway, o)
            if ub < best_ub:
                best_ub = ub
                best_collection = collection
        return best_collection
    elif method == 'PFO':
        ub, collection = solve(g, headway, paths)
        return collection


def solve(g, headway, col):
    collection = [col[0][0][0:-1]]
    fixed = [col[0][0]]
    for i in range(len(col)-1):
        next_path = col[i + 1][0]
        time = -1
        next_path, time, unsettled = compare_paths(g, headway, time, fixed,col, next_path, i, False)
        while unsettled:
            next_path, time, unsettled = compare_paths(g, headway, time, fixed,col, next_path, i, False)
        collection.append(next_path[0:-1])
        fixed.append(next_path)
    ub = sum(path[1] + path[2] for path in collection)
    return ub,collection


def compare_paths(g, headway, time, fixed,col, next_path, i, unsettled):
    for f in fixed:
        for node in col[i+1][0][0]:
            if node in f[0]:
                if check_conflict(g, f, next_path, node, f[4], col[i+1][0][4], headway):
                    arrival_at_node_1 = arrival_time(g, node, f[0], f[4], f[2])
                    arrival_at_node_2 = arrival_time(g, node, col[i+1][0][0], col[i+1][0][4], 0)
                    tail = f[4].length / f[4].speed + arrival_at_node_1
                    depature_time = tail + headway - arrival_at_node_2
                    if depature_time > time:
                        time = depature_time
                        next_path = [col[i + 1][0][0], col[i + 1][0][1], depature_time, col[i + 1][0][3], col[i + 1][0][4]]
                        unsettled = True
                        break
    return next_path, time, unsettled