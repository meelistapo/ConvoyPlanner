#!/usr/bin/env python
# -*- coding: utf-8 -*-
from itertools import islice
from copy import deepcopy
import numpy as np
import networkx as nx


def calculate(graph, convoys, headway, k, method):
    lb = 0
    ub = np.math.inf
    solution = None
    convoy_count = len(convoys)
    paths = find_feasible_paths(graph, convoys, k)
    if method == 'BB - 1':
        solution, ub = branch_and_bound(graph, paths, lb, lb, ub, 1, convoy_count, [], [], {}, headway, convoys, k)
    elif method == 'BB - 2':
        solution, ub = branch_and_bound_2(graph, paths, lb, lb, ub, 1, convoy_count, [], [], {}, headway, convoys, k)

    return solution


# branch-and-bound method for BB-1
def branch_and_bound(graph, all_feasible_paths, lb, selected_lb, ub, level, n,
                     current_collection, mid_solution, best_collection, headway, convoys, k):
    if level == n:
        last_paths = list(all_feasible_paths.values())[0]
        for i, last_path in enumerate(last_paths):
            incompatible = {last_path[3]:i}
            mid_solution = current_collection
            all_compatible_paths = replace_incompatible(graph, incompatible, mid_solution, all_feasible_paths, convoys, headway, k)
            path = all_compatible_paths[last_path[3]][i]
            current_collection.append(path[0:-1])
            ub_candidate = sum(paths[1] + paths[2] for paths in current_collection)
            if ub_candidate < ub:
                ub = ub_candidate
                best_collection = deepcopy(current_collection)
            del current_collection[-1]
        return best_collection, ub
    else:
        for paths in list(all_feasible_paths.values()):
            selected_convoy = paths[0][3]
            for i, path in enumerate(paths):
                all_compatible_paths = {i: fp for i, fp in all_feasible_paths.items() if i != selected_convoy}
                incompatible = {path[3]:i}
                if len(current_collection)>0:
                    mid_solution = deepcopy(current_collection)
                    all_compatible_paths = replace_incompatible(graph, incompatible, mid_solution, all_feasible_paths, convoys, headway, k)
                    path = all_compatible_paths[path[3]][i]
                    all_compatible_paths = {i: fp for i, fp in all_compatible_paths.items() if i != selected_convoy}
                if len(path) == 5:
                    current_collection.append(path[0:-1])
                else:
                    current_collection.append(path)
                if not all_compatible_paths:
                    # print("fathom 3")
                    del current_collection[-1]
                    continue
                selected_values = sum(paths[1]+paths[2] for paths in current_collection)
                remaining_best_values = 0
                for remaining_paths in list(all_compatible_paths.values()):
                    min = remaining_paths[0][1]+remaining_paths[0][2]
                    for p in remaining_paths:
                        if p[1]+p[2] < min:
                            min = p[1]+p[2]
                    remaining_best_values += min
                lb_candidate = selected_values + remaining_best_values
                if lb_candidate > lb:
                    lb = selected_values + remaining_best_values
                if lb > ub:
                    # print("fathom 1")
                    lb = selected_lb
                    del current_collection[-1]
                    continue
                if level < n:
                    level += 1
                    best_collection, ub = branch_and_bound(graph, all_compatible_paths, lb,
                                                           selected_lb, ub,
                                                           level, n,
                                                           current_collection, mid_solution, best_collection,
                                                           headway, convoys, k)
                level -= 1
                del current_collection[-1]
    return best_collection, ub


# branch-and-bound method for BB-2
def branch_and_bound_2(graph, all_feasible_paths, lb, selected_lb, ub, level, n,
                       current_collection, mid_solution, best_collection, headway, convoys, k):
    if level == n:
        last_paths = list(all_feasible_paths.values())[0]
        for i, last_path in enumerate(last_paths):
            incompatible = {last_path[3]:i}
            mid_solution = current_collection
            all_compatible_paths = replace_incompatible(graph, incompatible, mid_solution, all_feasible_paths, convoys, headway, k)
            path = all_compatible_paths[last_path[3]][i]
            current_collection.append(path[0:-1])
            ub_candidate = sum(paths[1] + paths[2] for paths in current_collection)
            if ub_candidate < ub:
                ub = ub_candidate
                best_collection = deepcopy(current_collection)
            del current_collection[-1]
        return best_collection, ub
    else:
        selected_convoy = min_objective(all_feasible_paths)
        paths = all_feasible_paths[selected_convoy]
        for i, path in enumerate(paths):
            all_compatible_paths = {i: fp for i, fp in all_feasible_paths.items() if i != selected_convoy}
            incompatible = {path[3]:i}
            if len(current_collection)>0:
                mid_solution = deepcopy(current_collection)
                all_compatible_paths = replace_incompatible(graph, incompatible, mid_solution, all_feasible_paths, convoys, headway, k)
                path = all_compatible_paths[path[3]][i]
                all_compatible_paths = {i: fp for i, fp in all_compatible_paths.items() if i != selected_convoy}
            if len(path) == 5:
                current_collection.append(path[0:-1])
            else:
                current_collection.append(path)
            if not all_compatible_paths:
                # print("fathom 3")
                del current_collection[-1]
                continue
            selected_values = sum(paths[1] for paths in current_collection)
            remaining_best_values = 0
            for remaining_paths in list(all_compatible_paths.values()):
                min = remaining_paths[0][1]+remaining_paths[0][2]
                for p in remaining_paths:
                    if p[1]+p[2] < min:
                        min = p[1]+p[2]
                remaining_best_values += min
            lb_candidate = selected_values + remaining_best_values
            if lb_candidate > lb:
                lb = selected_values + remaining_best_values
            if lb > ub:
                # print("fathom 1")
                lb = selected_lb
                del current_collection[-1]
                continue
            if level < n:
                level += 1
                best_collection, ub = branch_and_bound(graph, all_compatible_paths, lb, selected_lb, ub, level, n, current_collection, mid_solution, best_collection,
                                                       headway, convoys, k)
            level -= 1
            del current_collection[-1]
    return best_collection, ub


def calculate_new_paths(graph, fixed, path_data, headway, conflicting_convoy, convoy_map):
    time = -1
    result = path_data
    next_path = path_data
    result, next_path, time, unsettled = compare_paths(graph, headway, time, fixed, conflicting_convoy, next_path, result, False, convoy_map)
    while unsettled:
        result, next_path, time, unsettled = compare_paths(graph, headway, time, fixed, conflicting_convoy, next_path,result, False, convoy_map)
    return result


def compare_paths(graph, headway, time, fixed, conflicting_convoy, next_path, result, unsettled, convoy_map):
    for selected_path_data in fixed:
        selected_path_data = selected_path_data[0]
        selected_convoy = convoy_map[selected_path_data[3]]
        for node in next_path[0]:
            if node in selected_path_data[0]:
                if check_conflict(graph, selected_path_data, next_path, node, selected_convoy, conflicting_convoy, headway):
                    arrival_at_node_1 = arrival_time(graph, node, selected_path_data[0], selected_convoy,
                                                     selected_path_data[2])
                    arrival_at_node_2 = arrival_time(graph, node, next_path[0], conflicting_convoy,
                                                     0)
                    tail = selected_convoy.length / selected_convoy.speed + arrival_at_node_1
                    depature_time = tail + headway - arrival_at_node_2
                    if depature_time > time:
                        next_path = [next_path[0], next_path[1], depature_time, conflicting_convoy.id, conflicting_convoy]
                        result = next_path[0:-1]
                        time = depature_time
                        unsettled = True
                        break
    return result, next_path, time, unsettled


def min_objective(all_feasible_paths):
    identifiers = [k for k in all_feasible_paths.keys()]
    identifiers = sorted(identifiers)
    first = identifiers[0]
    convoys = [k for k in all_feasible_paths.keys() if k == first]
    selected_convoy = convoys[0]
    minimum = np.math.inf
    data = sorted(all_feasible_paths.items(), key=lambda x: x[1])
    for convoy, paths in data:
        for path in paths:
            if path[1] + path[2] < minimum:
                minimum = path[1] + path[2]
                selected_convoy = convoy
    return selected_convoy


def replace_incompatible(graph, incompatible, mid_solution, all_feasible_paths, convoys, headway, k):
    new_collections = {}
    selected_convoys =[]
    convoy_map = {i.id: i for i in convoys}
    if len(mid_solution) > 0:
        selected_convoys = [int(i[3]) for i in mid_solution]
    for i, j in incompatible.items():
        conflicting_convoy = convoy_map[i]
        conflicting_convoy_data = all_feasible_paths[i][j]
        fixed = [[i] for i in mid_solution]
        new_path = calculate_new_paths(graph, fixed, conflicting_convoy_data, headway, conflicting_convoy, convoy_map)
        collection = deepcopy(all_feasible_paths[i])
        collection[j]= new_path
        new_collections[i] = collection
        all_feasible_paths[i] = new_collections[i]
    if len(selected_convoys) > 0:
        all_feasible_paths = {i : j for i, j in all_feasible_paths.items() if i not in selected_convoys}
    return all_feasible_paths


def collision_check(graph, selected_convoy, convoy, selected_path, path, node, headway):
    start = arrival_time(graph, node, path[0], convoy, path[2])
    end = start + convoy.length / convoy.speed + headway
    selected_start = arrival_time(graph, node, selected_path[0], convoy, selected_path[2])
    selected_end = selected_start + selected_convoy.length / selected_convoy.speed + headway
    if start <= selected_start < end or selected_start <= start < selected_end:
        return True
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


def find_feasible_paths(graph, convoys, k):
    all_feasible_paths = {c.id:[] for c in convoys}
    for i in convoys:
        paths = k_shortest_paths(graph, i.origin, i.destination, i.speed, k, 0, weight='weight')
        for path in paths:
            new_path =[path['path'], path['cost'], i.ready_time, int(i.id),i]
            all_feasible_paths[i.id].append(new_path)
    return all_feasible_paths
