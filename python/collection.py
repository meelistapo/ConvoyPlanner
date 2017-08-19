import json
import traceback
import networkx
import operator
from exact import calculate
from milp  import calculate as calculate1
from fixed import calculate as calculate2



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
    data = load_json('data/edges.json')
    graph = networkx.Graph()
    graph.add_weighted_edges_from(data)
    return graph


def load_json(filename):
    with open(filename) as json_data:
        data = json.load(json_data)
    json_data.close()
    return data


def collect(data):
    convoy_data = {int(k):v for k,v in data[0].items()}
    convoy_data = sorted(convoy_data.items(), key=operator.itemgetter(0))
    headway = data[1]/60
    k = data[2]
    method = data[3]
    convoys = []
    origin = []
    destination = []
    length = []
    speed= []
    ready = []
    due = []
    solution = "no solution"
    graph = create_graph()

    if method.startswith('BB'):
        for convoyID, features in convoy_data:
            convoy = Convoy(convoyID, features["origin"], features["destination"], features["length"]/1000, features["speed"], features["ready"],features["due"])
            convoys.append(convoy)
        try:
            solution = calculate(graph, convoys, headway, k, method)
        except:
            solution = str(traceback.format_exc())
    elif method == "EFO" or method == "PFO":
        for convoyID, features in convoy_data:
            convoy = Convoy(convoyID, features["origin"], features["destination"], features["length"]/1000, features["speed"], features["ready"],features["due"])
            convoys.append(convoy)
        try:
            solution = calculate2(graph, convoys, headway, method)
        except:
            solution = str(traceback.format_exc())
    elif method.startswith('MILP'):
        for convoyID, features in convoy_data:
            origin.append(features["origin"])
            destination.append(features["destination"])
            length.append(features["length"]/1000)
            speed.append(features["speed"])
            ready.append(features["ready"])
            due.append(features["due"])
        try:
            solution = calculate1(graph, origin, destination, length, speed, ready, due, headway, k, method)
        except:
            solution = str(traceback.format_exc())
    # elif method == 'Input':
        # insert paths here
    return json.dumps(solution)