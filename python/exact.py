#!/usr/bin/env python
# -*- coding: utf-8 -*-
from itertools import islice

from copy import deepcopy
from scipy.sparse import csr_matrix
import numpy as np
import networkx as nx
import math


def lest_geo(x,y):
  a = 6378137.0
  F = 1/298.257222100883
  ESQ = (F + F - F * F)
  B0 = (57.0 + 31.0 / 60.0 + 3.19414800000 / 3600.0) / math.radians(1)
  L0 = (24.0 / math.radians(1))
  FN = 6375000.0
  FE = 500000.0
  B2 = (59.0 + 20.0 / 60.0) / math.radians(1)
  B1 = 58.0 / math.radians(1)
  xx = x - FN
  yy = y - FE
  t0 = math.sqrt((1.0 - math.sin(B0)) / (1.0 + math.sin(B0)) * pow(((1.0 + math.sqrt(ESQ) * math.sin(B0)) / (1.0 - math.sqrt(ESQ) * math.sin(B0))), math.sqrt(ESQ)))
  t1 = math.sqrt((1.0 - math.sin(B1)) / (1.0 + math.sin(B1)) * pow(((1.0 + math.sqrt(ESQ) * math.sin(B1)) / (1.0 - math.sqrt(ESQ) * math.sin(B1))), math.sqrt(ESQ)))
  t2 = math.sqrt((1.0 - math.sin(B2)) / (1.0 + math.sin(B2)) * pow(((1.0 + math.sqrt(ESQ) * math.sin(B2)) / (1.0 - math.sqrt(ESQ) * math.sin(B2))), math.sqrt(ESQ)))
  m1 = (math.cos(B1) / pow((1.0 - ESQ * math.sin(B1) * math.sin(B1)), 0.5))
  m2 = (math.cos(B2) / pow((1.0 - ESQ * math.sin(B2) * math.sin(B2)), 0.5))
  n1 = (math.log(m1) - math.log(m2)) / (math.log(t1) - math.log(t2))
  FF = m1 / (n1 * pow(t1, n1))
  p0 = a * FF * pow(t0, n1)
  p = pow((yy * yy + (p0 - xx) * (p0 - xx)), 0.5)
  t = pow(p / a * FF, 1.0 / n1)
  print(p / a * FF, 1.0 / n1)
  print(pow(-2,-3.1))
  print("e",pow(-27.137849206398474, -6.319903343397881))
  FII = math.atan(yy / (p0 - xx))
  LON = FII / n1 + L0
  u = (math.pi / 2.0) - (2.0 * math.atan(t))
  LAT = (u + (ESQ / 2.0 + (5.0 * pow(ESQ, 2) / 24.0) + (pow(ESQ, 3) / 12.0) +
     (13.0 * pow(ESQ, 4) / 360.0)) * math.sin(2.0 * u) +
     ((7.0 * pow(ESQ, 2) / 48.0) + (29.0 * pow(ESQ, 3) / 240.0) +
     (811.0 * pow(ESQ, 4) / 11520.0)) * math.sin(4.0 * u) +
     ((7.0 * pow(ESQ, 3) / 120.0) + (81.0 * pow(ESQ, 4) / 1120.0)) * math.sin(6.0 * u) +
     (4279.0 * pow(ESQ, 4) / 161280.0) * math.sin(8.0 * u))
  LAT = math.radians(LAT)
  LON = math.radians(LON)
  #LON = LON * rad2dedegrees(1)

  return (LAT,LON)





def load_sparse_csr(filename):
    loader = np.load(filename)
    return csr_matrix((loader['data'], loader['indices'], loader['indptr']), shape=loader['shape'])


def addPaths(candidates, new_path, timestep, convoy):
    newpaths = []
    start = timestep
    while start < due_time[convoy] - new_path['cost']:
        newpaths.append([new_path, start])
        start += timestep
    if convoy in candidates:
        candidates[convoy] += newpaths
    else:
        candidates[convoy] = newpaths

    candidates[convoy].sort(key=lambda x: x[0]['cost'] + x[1])

    return candidates


def k_shortest_routes_optimal(graph, convoy, k, k_start, timestep, candidate_paths):
    feasible_paths = []
    i = 0
    newpath = next_shortest_path(graph, origin[convoy], destination[convoy], speed[convoy], k_start, weight='distance')
    while i < k:
        arrival_time_new = newpath['cost']
        if convoy in candidate_paths:
            # print(candidate_paths)
            arrival_time_old = candidate_paths[convoy][0][0]['cost'] + candidate_paths[convoy][0][1]
            if arrival_time_new < due_time[convoy]:
                if arrival_time_old < arrival_time_new:
                    feasible_paths.append([candidate_paths[convoy][0][0]['path'], candidate_paths[convoy][0][0]['cost'], candidate_paths[convoy][0][1]])
                    i += 1
                    candidate_paths[convoy].pop(0)
                elif arrival_time_new < due_time[convoy] and arrival_time_old > arrival_time_new:
                    feasible_paths.append([newpath['path'], newpath['cost'], 0])
                    i += 1
                    k_start += 1
                    candidate_paths = addPaths(candidate_paths, newpath, timestep, convoy)
                    newpath = next_shortest_path(graph, origin[convoy], destination[convoy], speed[convoy], k_start, weight='distance')
                else:
                    break
            else:
                feasible_paths.append([candidate_paths[convoy][0][0]['path'], candidate_paths[convoy][0][0]['cost'], candidate_paths[convoy][0][1]])
                i += 1
                candidate_paths[convoy].pop(0)
        else:
            if arrival_time_new < due_time[convoy]:
                feasible_paths.append([newpath['path'], newpath['cost'], 0])
                i += 1
                k_start += 1
                candidate_paths = addPaths(candidate_paths, newpath, timestep, convoy)
                newpath = next_shortest_path(graph, origin[convoy], destination[convoy], speed[convoy], k_start, weight='distance')
            else:
                break
    return feasible_paths


def add_paths(paths, added_paths):
    new_paths = []
    extended_paths = paths
    paths = {i: p[0] for i, p in paths.items()} # no multiple paths for these convoys, needs better implementation
    for selected_convoy, selected_path_data in paths.items():
        # remove selected convoy's paths
        compatible_paths = {i: p for i, p in paths.items() if i != selected_convoy}
        for convoy, path_data in compatible_paths.items():
            for node in path_data[0]:
                if node in selected_path_data[0]:
                    if check_conflict(selected_path_data, path_data, node, selected_convoy, convoy):
                        arrival_at_node_1 = arrival_time(node, selected_path_data[0], selected_convoy, ready_time[selected_convoy])
                        arrival_at_node_2 = arrival_time(node, path_data[0], convoy, ready_time[convoy])
                        tail = convoy_length[convoy] / speed[convoy] + arrival_at_node_2
                        depature_time = tail - arrival_at_node_1 + headway
                        print(selected_convoy,depature_time)
                        new_path = [selected_path_data[0],selected_path_data[1],depature_time]
                        if new_path not in added_paths:
                            new_paths.append(new_path)
                            extended_paths[selected_convoy].append(new_path)
    if new_paths:
        return extended_paths, added_paths+ new_paths
    return False, added_paths


def add_timeintervals(paths, convoy, k, step):
    path = paths[convoy][-1]
    start = path[2]
    duration =  path[1]
    arrival_time = start + duration
    for i in range(k):
        arrival_time += step
        start += step
        if arrival_time < due_time[convoy]:
            paths[convoy].append([path[0], duration, start])
        else:
            break

def best_choice():
    all_feasible_paths, lb, ub = find_feasible_paths()
    print(all_feasible_paths)
    first_convoy = minPaths(all_feasible_paths)
    k_start = {i: k for i in range(len(origin))}
    feasible_solution, ub = branch_and_bound(all_feasible_paths, lb, lb, ub, 1, convoy_count, {}, {}, first_convoy)

    if not optimality:
        new_paths = []
        while not feasible_solution:
            extended_paths, new_paths = add_paths(all_feasible_paths, new_paths)
            print(len(new_paths))
            if extended_paths:
                print("uued",extended_paths)
                feasible_solution, ub = branch_and_bound(extended_paths, lb, lb, ub, 1, convoy_count, {}, {}, first_convoy)
                if (feasible_solution):
                    return feasible_solution, ub
        #     print("No feasible solution")
        #     return None
        # aa

    obtainable_lb = find_lower_bounds(all_feasible_paths)
    print(obtainable_lb)
    while obtainable_lb:
        argmin = (min(obtainable_lb, key=obtainable_lb.get))
        lb = obtainable_lb[argmin]
        if lb > ub:
            break
        if optimality:
            extra_paths = k_shortest_routes_optimal(G, argmin, k, k_start[argmin], step, canditate_paths)
        else:
            extra_paths = k_shortest_routes(G, argmin, k, step, 0)
        k_start[argmin] += k
        if extra_paths:
            all_feasible_paths[argmin] += extra_paths
            all_feasible_paths[argmin].sort(key=lambda x: x[1] + x[2])
            # update lower bound
            # print('juurde', (all_feasible_paths[argmin][-1][1]+all_feasible_paths[argmin][-1][2]) - (all_feasible_paths[argmin][-2][1]+all_feasible_paths[argmin][-2][2]))
            # obtainable_lb[argmin] += (all_feasible_paths[argmin][-1][1]+all_feasible_paths[argmin][-1][2]) - (all_feasible_paths[argmin][-2][1]+all_feasible_paths[argmin][-2][2])
            obtainable_lb = find_lower_bounds(all_feasible_paths) # viga sees
        else:
            del obtainable_lb[argmin]
        # print(lb, ub)
        print(obtainable_lb)
        feasible_solution, new_ub = branch_and_bound(all_feasible_paths, lb, lb, ub, 1, convoy_count, {}, {}, argmin)
        if new_ub < ub:
            best_solution = feasible_solution
        print("------------",obtainable_lb)

    return ub, best_solution

def minPaths(all_feasible_paths):
    selected_convoy = [elem for elem in all_feasible_paths.keys()][0]
    minimum = np.math.inf
    for i, feasible_paths in all_feasible_paths.items():
        if 0 < len(feasible_paths) < minimum:
            minimum = len(feasible_paths)
            selected_convoy = i
    return selected_convoy

def branch_and_bound(all_feasible_paths, lb, selected_lb, ub, level, n, current_collection, best_collection, first_convoy):
    if level == n:
        current_collection[n] = list(all_feasible_paths.values())[0][0]
        ub_candidate =sum(paths[1]+paths[2] for paths in list(current_collection.values()))
        print(ub_candidate)
        if ub_candidate < ub:
            ub = ub_candidate
            best_collection = deepcopy(current_collection)
        del current_collection[level]
        return best_collection, ub
    else:
        if level == 1:
            selected_convoy = first_convoy
        else:
            # find convoy with fewest number of paths in all_feasible_paths
            selected_convoy = minPaths(all_feasible_paths)
        paths = all_feasible_paths[selected_convoy]
        # print(selected_convoy)
        for path in paths:
            current_collection[level] = path
            # remove selected convoy's paths
            all_compatible_paths = {i:fp for i, fp in all_feasible_paths.items() if i != selected_convoy}
            # remove paths uncompatible with selected path
            all_compatible_paths = remove_uncompatible(all_compatible_paths, path, selected_convoy)
            # print(all_compatible_paths)
            if not all_compatible_paths:
                # print("fantom 3")
                del current_collection[level]
                continue
            selected_values = sum(paths[1] for paths in list(current_collection.values()))
            remaining_best_values = sum(paths[0][1] for paths in list(all_compatible_paths.values()) if paths)
            lb_candidate = selected_values + remaining_best_values
            if lb_candidate > lb:
                lb = selected_values + remaining_best_values
            if lb > ub:
                print("fantom 1")
                lb = selected_lb
                del current_collection[level]
                continue
            if level < n:
                level += 1
                best_collection, ub = branch_and_bound(all_compatible_paths, lb, selected_lb, ub, level, n, current_collection, best_collection, first_convoy)

            level -= 1
            del current_collection[level]
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


def collision_check(selected_convoy, convoy, selected_path, path, node):
    start = arrival_time(node, path[0], convoy, path[2])
    end = start + convoy_length[convoy] / speed[convoy] + headway
    selected_start = arrival_time(node, selected_path[0], convoy, selected_path[2])
    selected_end = selected_start + convoy_length[selected_convoy] / speed[selected_convoy] + headway
    if start <= selected_start <= end or selected_start <= start <= selected_end:
        return True
    return False


def paths_touch(path1, path2, node):
    if node in path1 and node in path2:
        index1 = path1.index(node)
        index2 = path2.index(node)
        # if both paths have nodes before and after common node
        if index1 != 0 and index1 != len(path1) - 1 and index2 != 0 and index2 != len(path2) - 1:
            # if both nodes are on the same side
            return side(path1[index1 - 1], path1[index1 + 1], path2[index2 - 1]) == side(path1[index1 - 1], path1[index1 + 1],
                                                                                     path2[index2 + 1])
    return False


def check_conflict(selected_path_data, path_data, node, selected_convoy, convoy):
    selected_path = selected_path_data[0]
    path = path_data[0]
    if common_edge(selected_path, path, node):
        if common_direction(selected_path, path, node):
            if collision_check(selected_convoy, convoy, selected_path_data, path_data, node):
                # print("same edge, same direction - conflict")
                return True
            # print("same edge, same direction - no conflict")
            return False
        # print("same edge, different direction")
        return False
    else:
        # paths have common node but they don't cross each other
        if paths_touch(selected_path, path, node):
            index1 = selected_path.index(node)
            index2 = path.index(node)
            relavant_nodes1 = selected_path[index1 - 1:index1 + 2]
            relavant_nodes2 = path[index2 - 1:index2 + 2]
            # if turns are same-sided
            if ccw(relavant_nodes1) == ccw(relavant_nodes2):
                # print("touching, same turns")
                return False
            else:
                if collision_check(selected_convoy, convoy, selected_path_data, path_data, node):
                    # print("touching, different turns - conflict ")
                    return True
                else:
                    # print("touching, different turns - no conflict ")
                    return False
        # paths cross each other
        else:
            if collision_check(selected_convoy, convoy, selected_path_data, path_data, node):
                # print("crossing - conflict")
                return True
            else:
                # print("crossing - no conflict")
                return False


def remove_uncompatible(options, selected_path_data, selected_convoy):
    new_options = {}
    for convoy, convoy_paths in options.items():
        remove = []
        for i, path_data in enumerate(convoy_paths):
            for node in path_data[0]:
                if node in selected_path_data[0]:
                    if check_conflict(selected_path_data, path_data, node, selected_convoy, convoy):
                        remove.append(i)
        new_convoy_paths = [convoy_paths[i] for i in range(len(convoy_paths)) if i not in remove]
        if len(new_convoy_paths) > 0:
            new_options[convoy] = new_convoy_paths
    return new_options



def remove_uncompatible2(options, selected_path_data, selected_convoy):
    new_options = {}
    for convoy, convoy_paths in options.items():
        remove = []
        for i, path_data in enumerate(convoy_paths):
            for node in path_data[0]:
                if node in selected_path_data[0]:
                    print(node)
                    if check_conflict(selected_path_data, path_data, node, selected_convoy, convoy):
                        arrival_at_node_1 = arrival_time(node, selected_path_data[0], selected_convoy, 0)
                        arrival_at_node_2 = arrival_time(node, path_data[0], convoy, 0)
                        tail_1 = convoy_length[selected_convoy]/speed[selected_convoy] + arrival_at_node_1
                        tail_2 = convoy_length[convoy]/speed[convoy] + arrival_at_node_2
                        depature_time_1 = tail_2 - arrival_at_node_1 + headway
                        depature_time_2 = tail_1 - arrival_at_node_2 + headway

                        print(arrival_at_node_1,arrival_at_node_2)
                        print(arrival_time(3800, selected_path_data[0], selected_convoy, 0), arrival_time(164, path_data[0], convoy, 0))
                        print(tail_1,tail_2)
                        print(depature_time_1,depature_time_2)
                        hhh
                        remove.append(i)
        new_convoy_paths = [convoy_paths[i] for i in range(len(convoy_paths)) if i not in remove]
        if len(new_convoy_paths) > 0:
            new_options[convoy] = new_convoy_paths
    return new_options


def arrival_time(node, path, convoy, start):
    if node not in path:
        return False
    elif path[0] == node:
        return start
    else:
        time = start
        for i in range(1, len(path)):
            time += G[path[i - 1]][path[i]]['distance'] / speed[convoy]
            if path[i] == node:
                return time


def calculate_path_cost(G, path):
    cost = 0
    for i in range(len(path)):
        if i > 0:
            cost += G[path[i - 1]][path[i]]['distance']
    return cost


def next_shortest_path(G, source, target, speed, start, weight=None):
    path = {}
    route = list(islice(nx.shortest_simple_paths(G, source, target, weight='distance'), start, start+1))
    path['path'] = route[0]
    path['cost'] = calculate_path_cost(G, route[0]) / speed
    return path


def k_shortest_paths(G, source, target, speed, k, start, weight=None):
    paths = []
    routes = list(islice(nx.shortest_simple_paths(G, source, target, weight='distance'), start + k))

    for i in range(start, len(routes)):
        paths.append({'path': routes[i], 'cost': calculate_path_cost(G, routes[i]) / speed})
    return paths


# determining if three points are listed in a counterclockwise order
def ccw(path):
    a = path[0]
    b = path[1]
    c = path[2]
    if (coordinates[c][1] - coordinates[a][1]) * (coordinates[b][0] - coordinates[a][0]) > (
        coordinates[b][1] - coordinates[a][1]) * (coordinates[c][0] - coordinates[a][0]):
        return True
    return False


def side(line1, line2, point):
    v1 = [coordinates[line2][0] - coordinates[line1][0], coordinates[line2][1] - coordinates[line1][1]]  # Vector 1
    v2 = [coordinates[line2][0] - coordinates[point][0], coordinates[line2][1] - coordinates[point][1]]  # Vector 2
    xp = v1[0] * v2[1] - v1[1] * v2[0]  # Cross product
    if xp > 0:
        return 'right'
    elif xp < 0:
        return 'left'
    else:
        return 'on the same line!'


# def paths_cross(path1, path2, node):
#     if

def direction(node1, node2):
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


# def k_shortest_routes(graph, origin, destination, speed, due_time, k, λ, start):
#     feasible_paths = []
#     paths = k_shortest_paths(graph, origin, destination, speed, k, start, weight='distance')
#     for path in paths:
#         arrival_time = path['cost']
#         if arrival_time < due_time:
#             j = 0
#             while j < due_time - arrival_time:
#                 feasible_paths.append()
#                 j += λ
#     return feasible_paths


def find_feasible_paths():
    all_feasible_paths = {}
    lower_bound = 0
    upper_bound = np.math.inf
    for i in range(convoys):
        if optimality:
            feasible_paths = k_shortest_routes_optimal(G, i, k, ready_time[i], step, canditate_paths)
        else:
            path = k_shortest_paths(G, origin[i], destination[i], speed[i], 1, 0, weight='distance')
            feasible_paths = [[path[0]['path'], path[0]['cost'], ready_time[i]]]
        all_feasible_paths[i] = feasible_paths


    #
    # shortest_paths = {i :[paths[0]] for i, paths in enumerate(all_feasible_paths.values())}
    # max_arrival = get_max_arrival(shortest_paths)
    # #filter based on max_arrival
    # for i, paths_data in all_feasible_paths.items():
    #     all_feasible_paths[i] = [path_data for path_data in paths_data if path_data[2] <= max_arrival]
    return all_feasible_paths, lower_bound, upper_bound





def tere(text):
    print("sees")
    if text == "hei":
        return "super"
    return "Tere"

if __name__ == '__main__':

    origin = [1,2,3,4,5,6,7,8,9,10]
    # origin = [3338, 2960] #, 164, 2960]
    # destination = [3800, 164] #, 3800, 3338]
    destination = [11,12, 13 ,14,15,16,17,18,19,20]
    ready_time = [0, 0, 0, 0, 0, 0, 0, 0.14,0,0]
    due_time = [10, 10, 10, 10,10,10,10,10,10,10]
    convoy_length = [10, 10, 10, 10,10,10,10,10,10,10]
    convoy_count = len(origin)
    headway = 0.05
    speed = [50, 50, 50, 50,50,50,50,50,50,50]
    convoys = len(origin)
    k = 1
    step = 0.5
    canditate_paths = {}
    optimality = False



    # M = load_sparse_csr('data.npz')
    # G = nx.from_scipy_sparse_matrix(M)

    # Read data from shp file
    G = nx.read_shp('data.shp')

    # get coordinates
    coordinates = {key: value for (key, value) in enumerate(G.nodes())}
    # print(coordinates[0])
    # dd


    # change labels to integers
    G = nx.convert_node_labels_to_integers(G, first_label=0)

    # change graph to simple graph
    G = G.to_undirected()

    # keep only edge length as it's attribute
    nx.set_edge_attributes(G, "distance", nx.get_edge_attributes(G, 'Length'))

    #
    # print(nx.dijkstra_path_length(G, 525, 415, weight='weight'))
    # print(nx.dijkstra_path_length(G, 3800, 2960, weight='weight'))
    # paths = k_shortest_paths(G, 525, 1983, 3)

    # solution = best_choice()
    # print("feasible_solution", solution)


    # path = k_shortest_paths(G,515,100,50,1,0)[0]['path']
    # print(len(list(coordinates)))
    # c = ''
    # cnt =0
    # a = []
    # for i in coordinates.values():
    #     cnt+=1
    #     if cnt%200==0:
    #         a.append(c)
    #         # print(c)
    #         c =''
    #     c+=str(i[0])
    #     c+=','
    #     c+=str(i[1])
    #     c += ','
    # a.append(c)
    # print(c)


    # v = f.split(' ')
    # f = {}
    # for i,j in enumerate(v):
    #     f[i] =j.split(',')
    #     if(len(f[i]) != 2):
    #         print(f[i],"jama")
    #
    # print(len(coordinates))
    # print(f)


    # # print(check_conflict([[3338, 3583, 3800], 0.43484810014, 0], [[2960, 3583, 164], 0.2580022264992, 0.17920564813540008], 3583, 0, 1))

    # a= [10, 655, 2791, 467, 2479, 11, 3, 1490, 1020, 721, 3524, 3531, 1531, 1349, 1989, 2228, 339, 1728, 1889, 2385, 1060, 2565, 516, 1421, 1793, 3854, 2981, 3719, 3087, 1459, 3561, 2105, 1098, 1691, 997, 597, 3021, 1067, 3229, 2874, 1329, 3048, 82, 375, 2497, 3860, 2778, 2443, 1920, 830, 3493, 69, 335, 741, 706, 2367, 513, 476, 267, 876, 1743, 20]
    # print(arrival_time(3, a, 9,0))