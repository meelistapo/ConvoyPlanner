import json
import networkx
from python.exact import best_choice

class Environment:
    def __init__(self, convoys, headway, algorithm, optimality, k, step):
        self.convoys = convoys
        self.headway = headway
        self.algorithm = algorithm
        self.optimality = optimality
        self.k = k
        self.step = step
        self.graph = create_graph()


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


def collect_paths(data):
    convoy_data = data[0]
    headway = float(data[1])/60
    algorithm = data[2]
    k = 1
    step = 0.5
    optimality = False
    convoys = []
    for convoyID, features in convoy_data.items():
        convoy = Convoy(int(convoyID), int(features["origin"]), int(features["destination"]), int(features["length"])/1000, int(features["speed"]), int(features["ready"]), int(features["due"]))
        convoys.append(convoy)

    env = Environment(convoys, headway, algorithm,optimality,k, step)
    feasible_solution, ub = best_choice(env)

    convoy_ids= []
    starts = []
    for conID, data in feasible_solution.items():
        convoy_ids.append(conID)
        starts.append(data[2])
    start_times, start_order = zip(*sorted(zip(starts, convoy_ids)))

    return [start_order, feasible_solution]