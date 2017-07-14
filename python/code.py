from gurobipy import *
import numpy as np
from scipy.sparse import csr_matrix
import networkx as nx
import queue as Q
from itertools import islice
import copy


def k_short(g, U, V, k):
    l = []
    s = set()
    for i in range(len(U)):
        l.append(list(islice(nx.shortest_simple_paths(g, U[i], V[i], weight="weight"), k)))
        for p in l[-1]:
            s = s.union(set(p))
    return l , s

def solve(m, c, O, D, L, R, F, E, S, h, new_m, k, mynode, paths):
    """
    Solves the optimization problem
    :param m: number of nodes on the network
    :param c: number of convoys
    :param O: origin points for convoys
    :param D: destination points for convoys
    :param L: length of convoys
    :param R: earliest ready ready time(departure time from origin) for convoys
    :param F: latest finishing time (arrival time in destination) for convoys
    :param E: edge lengths
    :param S: speed of convoys on edges
    :param h: minimum headway between convoys passing the same node (in time units).
    """

    model = Model("cmp16")
    # Add variables
    B = np.empty(c, dtype=Var)             # 1D array, discrete time intervals for convoys
    T = np.empty((c, m), dtype=Var)        # 2D array, time when convoy c arrives at node i
    X = np.empty((c, m, m), dtype=Var)     # 3D array, 1, if convoy c traverse between nodes i and j,  otherwise 0
    Y = np.empty((m, c, c), dtype=Var)     # 3D array, 1, if convoy c traverse node i before convoy cc, otherwise 0
    Q = np.empty((c, c, m, m), dtype=Var)  # 4D array, 1, if convoy c traverse edge i j before convoy cc, otherwise 0
    u = np.empty((c, k), dtype=Var)
    nodes = np.arange(m)    # set of nodes
    convoys = np.arange(c)  # set of convoys

    #########################
    ####### NEW IDEA
    #########################
    for c in convoys:
        temp = 0
        for i in range(k):
            u[c][i] = model.addVar(vtype=GRB.BINARY, name='u({}_{})'.format(c, i))
            temp += u[c][i]
        model.addConstr(temp == 1)


    #########################
    ####### /////////
    #########################


    # filling continuous variables
    for c in convoys:
        # B[c] = model.addVar(name='B({})'.format(c))
        for i in nodes:
            T[c][i] = model.addVar(name='T({}_{})'.format(c, i))

    # filling binary variables
    for c in convoys:
        for i in nodes:
            for j in nodes:
                if E[i,j] > 0:
                    X[c][i][j] = model.addVar(vtype=GRB.BINARY, name='X({}_{}_{})'.format(c, i, j))

    ######################
    ##### NEW
    ######################
    for c in convoys:
        for i in range(k):
            for j in range(len(paths[c][i]) - 1):
                model.addConstr(u[c][i] <= X[c][mynode.index(paths[c][i][j])][mynode.index(paths[c][i][j+1])])

                #model.addGenConstrIndicator(u[c][i], True, X[c][mynode.index(paths[c][i][j])][mynode.index(paths[c][i][j+1])], GRB.EQUAL, 1.0)
    ######################
    ########## //////
    ######################

    # variables for multi-convoy conditions
    if len(convoys) > 1:
        for i in nodes:
            for c in convoys:
                for cc in convoys:
                    if c != cc:
                        Y[i][c][cc] = model.addVar(vtype=GRB.BINARY, name='Y({}_{}_{})'.format(i, c, cc))

        # for c in convoys:
        #     for cc in convoys:
        #         if c != cc:
        #             for i in nodes:
        #                 for j in nodes:
        #                     if E[i,j] > 0:
        #                         Q[c][cc][i][j] = model.addVar(vtype=GRB.BINARY, name='Q({}_{}_{}_{})'.format(c, cc, i, j))
        #                         # Q[c][cc][i][j][k][l] = model.addVar(vtype=GRB.BINARY, name='Q({}_{}_{}_{}_{}_{})'.format(c, cc, i, j, k, l))

    model.update()

    # objective function - minimize the sum of arrival times of convoys at their respective destinations
    model.setObjective(quicksum(T[c][D[c]] for c in convoys), GRB.MINIMIZE)

    # Add constraints
    # for c in convoys:
    #     for i in nodes:
    #         model.addConstr(T[c][i] <= T[c][D[c], name='0a')  # 0


    # 1) Flow conservation constraint
    # for c in convoys:
    #     for j in nodes:
    #         sum1 = 0
    #         for i in nodes:
    #             if E[i,j] > 0:
    #                 sum1 += X[c][i][j]
    #                 sum1 -= X[c][j][i]
    #         if j == D[c]:
    #             model.addConstr(sum1 == 1, name='1a')  # 2
    #         elif j == O[c]:
    #             model.addConstr(sum1 == -1, name='1b')
    #         else:
    #             model.addConstr(sum1 == 0, name='1c')

    # 2) Each convoy can leave a node at most once
    for c in convoys:
        for j in nodes:
            sum1 = 0
            for i in nodes:
                if E[i,j] > 0:
                    sum1 += X[c][i][j]
            model.addConstr(sum1 <= 1, name='2')  # 3

    # 3) Each convoy can enter a node at most once
    for c in convoys:
        for i in nodes:
            sum1 = 0
            for j in nodes:
                if E[i,j] > 0:
                    sum1 += X[c][i][j]
            model.addConstr(sum1 <= 1, name='3')  # 4

    # 4) Arrival time of the head of a convoy based on the selected arc
    for c in convoys:
        for i in nodes:
            bah = 0
            for j in nodes:
                if E[i, j] > 0:
                    model.addConstr(T[c][i] + E[i,j] / S[c] + new_m * (1 - X[c][i][j]) >= T[c][j], name='4a')  # 5m
                    model.addConstr(T[c][i] + E[i,j] / S[c] - new_m * (1 - X[c][i][j]) <= T[c][j], name='4b')  # 6m
                    bah += X[c][j][i]
            if i != O[c]:
                model.addConstr(bah * new_m >= T[c][i], name='4f')  # 6m

    # 5) Convoy k starts its trip after its earliest ready time.
    for c in convoys:
        model.addConstr(T[c][O[c]] >= R[c], name='5')  # 7m  #+ B[c]

    # 6) Convoy completes its arrival to its destination before its due date.
    # for c in convoys:
    #     for i in nodes:
    #         if E[i,D[c]] > 0:
    #             # print(c,i,  D[c])
    #             model.addConstr(T[c][D[c]] + L[c] / S[c] <= F[c] + new_m * (1 - X[c][i][D[c]]), name='6')  # 8m

    # 7) Headway is maintained between two convoys which pass through the same node, such that two convoys do not occupy the same node at the same time
    if len(convoys) > 1:
        for c in convoys:
            for cc in convoys:
                if c != cc:
                    for i in nodes:
                        for j in nodes:
                            if E[i,j] > 0:
                                # if O[c] == j:
                                #     model.addConstr(L[c] / S[c] + h - new_m * (2 - Y[j][c][cc] - X[c][i][j]) <= T[cc][j], name='7')  # 12m
                                # else:
                                    model.addConstr(T[c][j] + L[c] / S[c] + h - new_m * (2 - Y[j][c][cc] - X[c][i][j]) <= T[cc][j], name='7')  # 12m
                                    



        for c in convoys:
            for cc in convoys:
                if c != cc:
                    for j in nodes:
                        if j != O[c] and j != O[cc]:
                            sum1 = 0
                            for i in nodes:
                                if E[i,j] > 0:
                                    sum1 += X[c][i][j]
                                    sum1 += X[cc][i][j]
                            model.addConstr(sum1 >= 2 * (Y[j][c][cc] + Y[j][cc][c]), name='8a')  # 13
                            model.addConstr(sum1 <= Y[j][c][cc] + Y[j][cc][c] + 1, name='8b')  # 16

        for c in convoys:
            for cc in convoys:
                if c != cc:
                    for j in nodes:
                        if j == O[c] or j == O[cc]:
                            sum1 = 0
                            for i in nodes:
                                if E[i,j] > 0:
                                    # print(i,j)
                                    sum1 += X[c][i][j]
                                    sum1 += X[cc][i][j]
                            model.addConstr(1 + sum1 >= 2 * (Y[j][c][cc] + Y[j][cc][c]), name='8c')  # 14
                            model.addConstr(sum1 <= Y[j][c][cc] + Y[j][cc][c], name='8d')  # 18                   !!!!!!!!!!!!! 1+ sum in the paper


        # 9) Convoys starting from same node can't start at the same time
        for j in nodes:
            for c in convoys:
                for cc in convoys:
                    if j == O[c] and j == O[cc] and c != cc:
                        model.addConstr((Y[j][c][cc] + Y[j][cc][c]) <= 1)  # 15
                        model.addConstr((Y[j][c][cc] + Y[j][cc][c]) >= 1)  # 19

        for c in convoys:
            for cc in convoys:
                if c != cc:
                    for i in nodes:
                        for j in nodes:
                            if E[i,j] > 0:
                                model.addConstr(m * (2 - X[c][i][j] - X[cc][j][i]) >= Y[i][c][cc] + Y[j][cc][c] - 1)  # 17

    print("opt")

    model.optimize()

    for v in model.getVars():
        if v.x != 0:
            print(v.varName, v.x)

    # model.computeIIS()
    #
    # for con in model.getConstrs():
    #     if con.IISConstr:
    #         print('%s' % con.constrName,"fail")



def load_sparse_csr(filename):
    loader = np.load(filename)
    return csr_matrix((loader['data'], loader['indices'], loader['indptr']), shape=loader['shape'])



if __name__ == '__main__':

    #distances = load_sparse_csr('data.npz')
    # distances = np.array(
    #     [[0, 0, 10, 0, 0, 0, 0, 0],
    #      [0, 0, 10, 0, 0, 0, 0, 0],
    #      [10, 10, 0, 10, 0, 0, 0, 0],
    #      [0, 0, 10, 0, 10, 0, 0, 0],
    #      [0, 0, 0, 10, 0, 10, 0, 0],
    #      [0, 0, 0, 0, 10, 0, 10, 10],
    #      [0, 0, 0, 0, 0, 10, 0, 0],
    #      [0, 0, 0, 0, 0, 10, 0, 0]])
    #Test with networkX generators
    # n = 10
    # g = nx.cycle_graph(n)
    # A = nx.adjacency_matrix(g)
    # distances = A.todense()
    # print(distances)
    # distances[2,3] = 1000
    # distances[3,2] = 1000
    # print(distances)
    ###################################
    # origin = [0, 4]
    # destination = [4, 0]
    origin = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    destination = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    ready_time = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    due_time = [10000000000, 10000000000, 10000000000, 1000000000, 1000000000, 10000000000, 10000000000, 10000000000, 1000000000, 1000000000]
    convoy_length = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
    convoy_speed = [50, 50, 50, 50, 50, 50, 50, 50, 50, 50]
    convoy_count = len(origin)
    #node_count = distances.shape[0]
    headway = 0.5

    ########################
    ######### NEW
    #######################
    dis = load_sparse_csr('data.npz').todense()
    g = nx.Graph(dis)
    k = 5
    ans = k_short(g,origin, destination, k)
    h = copy.deepcopy(g)
    for v in h.nodes():
        if v not in ans[1]:
            h.remove_node(v)
    node_count = h.number_of_nodes()
    distances = nx.to_numpy_matrix(h, weight="weight")

    print(ans[0][1][1])
    print(h.nodes())
    print(ans[1])
    print(ans[0])
    new_origin = [h.nodes().index(origin[i]) for i in range(len(origin))]
    new_destination = [h.nodes().index(destination[i]) for i in range(len(origin))]

    print(new_origin)
    print(new_destination)
    print(distances)

    # distances = distances.todense()
    # print(distances[525, 415])

    # speeds = np.array([np.full((node_count, node_count), v, dtype='int32') for v in convoy_speed])

    solve(node_count, convoy_count, new_origin, new_destination, convoy_length, ready_time, due_time, distances, convoy_speed, headway, 30000, k, h.nodes(), ans[0])
