#!/usr/bin/env python
# -*- coding: utf-8 -*-
from itertools import islice
from copy import deepcopy
import json
import networkx
import numpy as np
import networkx as nx



class Convoy:
    def __init__(self, id, origin, destination, length, speed, ready_time, due_time):
        self.id = id
        self.origin = origin
        self.destination = destination
        self.length = length
        self.speed = speed
        self.ready_time = ready_time
        self.due_time = due_time


def create_graph():
    edges = load_json('../data/edges.json')
    graph = networkx.Graph()
    graph.add_weighted_edges_from(edges)
    return graph


def load_json(filename):
    with open(filename) as json_data:
        data = json.load(json_data)
    json_data.close()
    return data


def calculate_new_paths(graph, coordinates, fixed, path_data, headway, conflicting_convoy, convoy_map):
    time = -1
    result = path_data
    next_path = path_data
    result, next_path, time, unsettled = compare_paths(graph, coordinates, headway, time, fixed, conflicting_convoy, next_path, result, False, convoy_map)
    while unsettled:
        result, next_path, time, unsettled = compare_paths(graph, coordinates, headway, time, fixed, conflicting_convoy, next_path,result, False, convoy_map)
    return result


def compare_paths(graph, coordinates, headway, time, fixed, conflicting_convoy, next_path, result, unsettled, convoy_map):
    for selected_path_data in fixed:
        selected_path_data = selected_path_data[0]
        selected_convoy = convoy_map[selected_path_data[3]]
        for node in next_path[0]:
            if node in selected_path_data[0]:
                if check_conflict(graph, coordinates, selected_path_data, next_path, node, selected_convoy,
                                  conflicting_convoy,
                                  headway):
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


def best_choice(graph, coordinates, convoys, headway, k, method):
    lb = 0
    ub = np.math.inf
    solution = None
    convoy_count = len(convoys)
    paths = find_feasible_paths(graph, convoys, k)
    if method == 'Exact - 1':
        solution, ub = branch_and_bound(graph, coordinates, paths, lb, lb, ub,
                                                                             1,
                                                                             convoy_count, [], [], {}, headway, convoys, k)
    elif method == 'Exact - 2':
        solution, ub = branch_and_bound_2(graph, coordinates, paths, lb, lb, ub,
                                            1,
                                            convoy_count, [], [], {}, headway, convoys, k)

    return solution


def minPaths(all_feasible_paths):
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


def replace_incompatible(graph, coordinates,incompatible, mid_solution, all_feasible_paths, convoys, headway, k):
    new_collections = {}
    selected_convoys =[]
    convoy_map = {i.id: i for i in convoys}
    if len(mid_solution) > 0:
        selected_convoys = [int(i[3]) for i in mid_solution]
    for i, j in incompatible.items():
        conflicting_convoy = convoy_map[i]
        conflicting_convoy_data = all_feasible_paths[i][j]
        fixed = [[i] for i in mid_solution]
        new_path = calculate_new_paths(graph, coordinates, fixed, conflicting_convoy_data, headway, conflicting_convoy, convoy_map)
        collection = deepcopy(all_feasible_paths[i])
        collection[j]= new_path
        new_collections[i] = collection
        all_feasible_paths[i] = new_collections[i]
    if len(selected_convoys) > 0:
        all_feasible_paths = {i : j for i, j in all_feasible_paths.items() if i not in selected_convoys}
    return all_feasible_paths


def branch_and_bound(graph, coordinates, all_feasible_paths, lb, selected_lb, ub, level, n,
                     current_collection, mid_solution, best_collection, headway, convoys, k):
    if level == n:
        last_paths = list(all_feasible_paths.values())[0]
        for i, last_path in enumerate(last_paths):
            incompatible = {last_path[3]:i}
            mid_solution = current_collection
            all_compatible_paths = replace_incompatible(graph, coordinates, incompatible, mid_solution, all_feasible_paths, convoys, headway, k)
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
                    all_compatible_paths = replace_incompatible(graph, coordinates, incompatible, mid_solution, all_feasible_paths, convoys, headway, k)
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
                    best_collection, ub = branch_and_bound(graph, coordinates, all_compatible_paths, lb,
                                                           selected_lb, ub,
                                                           level, n,
                                                           current_collection, mid_solution, best_collection,
                                                           headway, convoys, k)
                level -= 1
                del current_collection[-1]
    return best_collection, ub


def branch_and_bound_2(graph, coordinates, all_feasible_paths, lb, selected_lb, ub, level, n,
                       current_collection, mid_solution, best_collection, headway, convoys, k):
    if level == n:
        last_paths = list(all_feasible_paths.values())[0]
        for i, last_path in enumerate(last_paths):
            incompatible = {last_path[3]:i}
            mid_solution = current_collection
            all_compatible_paths = replace_incompatible(graph, coordinates, incompatible, mid_solution, all_feasible_paths, convoys, headway, k)
            path = all_compatible_paths[last_path[3]][i]
            current_collection.append(path[0:-1])
            ub_candidate = sum(paths[1] + paths[2] for paths in current_collection)
            if ub_candidate < ub:
                ub = ub_candidate
                best_collection = deepcopy(current_collection)
            del current_collection[-1]
        return best_collection, ub
    else:
        selected_convoy = minPaths(all_feasible_paths)
        paths = all_feasible_paths[selected_convoy]
        for i, path in enumerate(paths):
            all_compatible_paths = {i: fp for i, fp in all_feasible_paths.items() if i != selected_convoy}
            incompatible = {path[3]:i}
            if len(current_collection)>0:
                mid_solution = deepcopy(current_collection)
                all_compatible_paths = replace_incompatible(graph, coordinates, incompatible, mid_solution, all_feasible_paths, convoys, headway, k)
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
                best_collection, ub = branch_and_bound(graph, coordinates, all_compatible_paths, lb,
                                                       selected_lb, ub,
                                                       level, n,
                                                       current_collection, mid_solution, best_collection,
                                                       headway, convoys, k)

            level -= 1
            del current_collection[-1]
    return best_collection, ub


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


def check_conflict(graph, selected_path_data, path_data, node, selected_convoy, convoy, headway):
    if node == selected_path_data[0][0] or node == selected_path_data[0][-1] or node == path_data[0][0] or node == path_data[0][-1]:
        return False
    elif collision_check(graph, selected_convoy, convoy, selected_path_data, path_data, node, headway):
        return True
    return False


def remove_incompatible(graph, coordinates, options, current_collection, selected_convoy, headway, convoy_map):
    new_options = {}
    incompatible_list = []
    incompatible = False
    for convoy_paths in options.values():
        incompatible_paths = []
        # if len(convoy_paths[0]) > 4:
        convoy = convoy_map[convoy_paths[0][3]]
        for i, path_data in enumerate(convoy_paths):
            for selected_path_data in current_collection:
                for node in path_data[0]:
                    if node in selected_path_data[0]:
                        if i not in incompatible_paths and check_conflict(graph, coordinates, selected_path_data, path_data, node, selected_convoy, convoy,
                                          headway):
                            incompatible_paths.append(i)
                            break
        new_convoy_paths = [convoy_paths[i] for i in range(len(convoy_paths)) if i not in incompatible_paths]
        if len(new_convoy_paths) > 1:
            new_options[convoy.id] = new_convoy_paths
        if len(incompatible_paths) > 0:
            incompatible = True
            incompatible_list.append({convoy.id : incompatible_paths})
    if incompatible:
        return new_options, incompatible_list
    return options, None


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



def side(coordinates, line1, line2, point):
    xp = (coordinates[line2][0]-coordinates[line1][0])*(coordinates[point][1]-coordinates[line1][1])-\
         (coordinates[line2][1]-coordinates[line1][1])*(coordinates[point][0]-coordinates[line2][0])
    if xp > 0:
        return 'left'
    elif xp < 0:
        return 'right'
    else:
        return 'on the same line'


def direction(graph, node1, node2):
    coordinates = {key: value for (key, value) in enumerate(graph.nodes())}
    if coordinates[node1][0] < coordinates[node2][0]:
        return True
    return False


def find_lower_bounds(all_feasible_paths):
    lb_overall = {}
    for convoy, paths in all_feasible_paths.items():
        convoys_worst = paths[-1][1]
        best_from_rest = sum([p[0][1] if c is not convoy else 0 for c, p in all_feasible_paths.items()])
        lb_overall[convoy] = convoys_worst + best_from_rest
    return lb_overall


def find_feasible_paths(graph, convoys, k):
    all_feasible_paths = {c.id:[] for c in convoys}
    for i in convoys:
        paths = k_shortest_paths(graph, i.origin, i.destination, i.speed, k, 0, weight='weight')
        for path in paths:
            new_path =[path['path'], path['cost'], i.ready_time, int(i.id),i]
            all_feasible_paths[i.id].append(new_path)
    return all_feasible_paths
