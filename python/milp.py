from itertools import islice
from gurobipy import *
import networkx as nx
import numpy as np
import operator
import copy

'''
Mixed Integer Linear Programming Methods MILP-1, MILP-2 and MILP-3
'''


def calculate(graph, origin, destination, length, speed, ready, due, headway, k, method):
    convoy_count = len(origin)
    if method == 'MILP - 1':
        node_count = graph.number_of_nodes()
        distances = nx.to_numpy_matrix(graph, weight="weight")
        result = solve(origin, destination, length, ready, due, distances, speed, node_count, convoy_count, headway, node_count*10, k, [], method)

    else:
        path_collection, used_nodes = get_k_shortest_paths(graph, origin, destination, k)
        graph_small = copy.deepcopy(graph)
        keymap = {}
        for v in graph_small.nodes():
            if v not in used_nodes:
                graph_small.remove_node(v)
        for v in graph_small.nodes():
            keymap[graph_small.nodes().index(v)] = v
        node_count = graph_small.number_of_nodes()
        distances = nx.to_numpy_matrix(graph_small, weight="weight")
        new_origin = [graph_small.nodes().index(origin[i]) for i in range(len(origin))]
        new_destination = [graph_small.nodes().index(destination[i]) for i in range(len(origin))]
        new_path_collection = []

        for paths in path_collection:
            new_paths =[]
            for path in paths:
                new_path = []
                for node in path:
                    new_path.append(graph_small.nodes().index(node))
                new_paths.append(new_path)
            new_path_collection.append(new_paths)

        pre_result = solve(new_origin, new_destination, length, ready, due, distances, speed, node_count, convoy_count, headway, node_count*10, k, new_path_collection, method)

        result={c:{} for c in range(convoy_count)}
        for c, n in pre_result.items():
            for k,v in n.items():
                result[c][keymap[k]] = v

    solution = []
    ub = 0
    for k,v in result.items():
        path = [e for e,f in sorted(v.items(), key=operator.itemgetter(1))]
        travel_time = result[k][path[-1]] - result[k][path[0]]
        start_time = result[k][path[0]]
        solution.append([path, travel_time, start_time, k+1])
        ub += travel_time+start_time
    solution = sorted(solution, key=operator.itemgetter(3))

    return solution


def get_k_shortest_paths(graph, origin, destination, k):
    paths = []
    used_nodes = set()
    for i in range(len(origin)):
        paths.append(list(islice(nx.shortest_simple_paths(graph, origin[i], destination[i], weight="weight"), k)))
        for p in paths[-1]:
            used_nodes = used_nodes.union(set(p))
    return paths, used_nodes


def solve(O, D, L, R, F, E, S, m, c, h, M, k, P, method):
    """
    Solves the optimization problem
    :param O: origin points for convoys
    :param D: destination points for convoys
    :param L: length of convoys
    :param R: earliest ready ready times(departure times from origins) for convoys
    :param F: latest finishing times (arrival times in destinations) for convoys
    :param E: edge lengths
    :param S: speed of convoys
    :param m: number of nodes on the network
    :param c: number of convoys
    :param h: minimum headway between convoys (in time units).
    :param M: large integer - M = 10m, used to limit th set of variables based on the value of a binary variable.
    :param k: number of paths genereted per convoy
    :param P: all paths for all convoys
    :param P: used optimization method
    """

    model = Model()

    # Add variables
    T = np.empty((c, m), dtype=Var)        # 2D array, time when convoy c arrives at node i
    X = np.empty((c, m, m), dtype=Var)     # 3D array, 1, if convoy c traverse between nodes i and j,  otherwise 0
    Y = np.empty((m, c, c), dtype=Var)     # 3D array, 1, if convoy c traverse node i before convoy cc, otherwise 0
    nodes = np.arange(m)    # set of nodes
    convoys = np.arange(c)  # set of convoys


    # filling continuous variables
    for i in convoys:
        for u in nodes:
            T[i][u] = model.addVar(name='T({}_{})'.format(i, u))

    # filling binary variables
    for i in convoys:
        for u in nodes:
            for v in nodes:
                if E[u,v] > 0:
                    X[i][u][v] = model.addVar(vtype=GRB.BINARY, name='X({}_{}_{})'.format(i, u, v))

    if method == 'MILP - 3':
        Z = np.empty((c, k), dtype=Var)
        for i in convoys:
            for q in range(k):
                Z[i][q] = model.addVar(vtype=GRB.BINARY, name='P({}_{})'.format(i, q))

    if len(convoys) > 1:
        for u in nodes:
            for i in convoys:
                for j in convoys:
                    if i != j:
                        Y[u][i][j] = model.addVar(vtype=GRB.BINARY, name='Y({}_{}_{})'.format(u, i, j))

    model.update()

    # objective function - minimize the sum of arrival times of convoys at their respective destinations
    model.setObjective(quicksum(T[i][D[i]] for i in convoys), GRB.MINIMIZE)

    # 1) Flow conservation constraint
    for i in convoys:
        for v in nodes:
            sum = 0
            for u in nodes:
                if E[u,v] > 0:
                    sum += X[i][u][v]
                    sum -= X[i][v][u]
            if v == D[i]:
                model.addConstr(sum == 1, name='1a')  # 2
            elif v == O[i]:
                model.addConstr(sum == -1, name='1b')
            else:
                model.addConstr(sum == 0, name='1c')

    # 2) Each convoy can leave a node at most once
    for i in convoys:
        for v in nodes:
            sum = 0
            for u in nodes:
                if E[u,v] > 0:
                    sum += X[i][u][v]
            model.addConstr(sum <= 1, name='2')  # 3

    # 3) Each convoy can enter a node at most once
    for i in convoys:
        for u in nodes:
            sum = 0
            for v in nodes:
                if E[u,v] > 0:
                    sum += X[i][u][v]
            model.addConstr(sum <= 1, name='3')  # 4

    # 4) Arrival time of the head of a convoy based on the selected arc
    for i in convoys:
        for u in nodes:
            sum = 0
            for v in nodes:
                if E[u, v] > 0:
                    model.addConstr(T[i][u] + E[u,v] / S[i] + M * (1 - X[i][u][v]) >= T[i][v], name='4a')  # 5m
                    model.addConstr(T[i][u] + E[u,v] / S[i] - M * (1 - X[i][u][v]) <= T[i][v], name='4b')  # 6m
                    sum += X[i][v][u]
            if u != O[i]:
                model.addConstr(sum * M >= T[i][u], name='4f')  # 6m

    # 5) Convoy k starts its trip after its earliest ready time.
    for i in convoys:
        model.addConstr(T[i][O[i]] >= R[i], name='5')  # 7m  #+ B[c]

    # 6) Convoy completes its arrival to its destination before its due date.
    for i in convoys:
        for u in nodes:
            if E[u,D[i]] > 0:
                model.addConstr(T[i][D[i]] + L[i] / S[i] <= F[i] + M * (1 - X[i][u][D[i]]), name='6')  # 8m

    # 7) Headway is maintained between two convoys which pass through the same node, such that two convoys do not occupy the same node at the same time
    if len(convoys) > 1:
        for i in convoys:
            for j in convoys:
                if i != j:
                    for u in nodes:
                        for v in nodes:
                            if E[u,v] > 0:
                                    model.addConstr(T[i][v] + L[i] / S[i] + h - M * (2 - Y[v][i][j] - X[i][u][v]) <= T[j][v], name='7')  # 12m

        for i in convoys:
            for j in convoys:
                if i != j:
                    for v in nodes:
                        if v != O[i] and v != O[j]:
                            sum = 0
                            for u in nodes:
                                if E[u,v] > 0:
                                    sum += X[i][u][v]
                                    sum += X[j][u][v]
                            model.addConstr(sum >= 2 * (Y[v][i][j] + Y[v][j][i]), name='8a')  # 13
                            model.addConstr(sum <= Y[v][i][j] + Y[v][j][i] + 1, name='8b')  # 16


                        elif v == O[i] or v == O[j]:
                            sum = 0
                            for u in nodes:
                                if E[u,v] > 0:
                                    # print(i,j)
                                    sum += X[i][u][v]
                                    sum += X[j][u][v]
                            model.addConstr(1 + sum >= 2 * (Y[v][i][j] + Y[v][j][i]), name='8c')  # 14
                            model.addConstr(sum <= Y[v][i][j] + Y[v][j][i], name='8d')  # 18

        # 9) Convoys starting from same node can't start at the same time
        for v in nodes:
            for i in convoys:
                for j in convoys:
                    if v == O[i] and v == O[j] and i != j:
                        model.addConstr((Y[v][i][j] + Y[v][j][i]) <= 1, name='9a')  # 15

        for i in convoys:
            for j in convoys:
                if i != j:
                    for u in nodes:
                        for v in nodes:
                            if E[u,v] > 0:
                                model.addConstr(m * (2 - X[i][u][v] - X[j][v][u]) >= Y[v][i][j] + Y[u][j][i] -1)  # 17

    # ensures that only one path out of k paths is used and that all nodes on that path are used
    if method == 'MILP - 3':
        for i in convoys:
            sum = 0
            for q in range(k):
                sum += Z[i][q]
                for n in range(len(P[i][q]) - 1):
                    model.addConstr(Z[i][q] <= X[i][P[i][q][n]][P[i][q][n + 1]])
            model.addConstr(sum == 1)


    model.optimize()
    result={c:{} for c in convoys}
    convoys = convoys.tolist()
    for v in model.getVars():
        convoy, node = v.varName[2:-1].split('_', 1)
        if v.varName.startswith('T'):
            if v.x != 0 or O[convoys.index(int(convoy))] == int(node):
                # print(v.varName, v.x)
                result[int(convoy)][int(node)]= float(v.x)
    return result