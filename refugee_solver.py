from scipy.optimize import linprog
from itertools import product
from cvxopt import solvers, matrix

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

B = 1

countries = ["Germany", "Syria", "Tunisia", "Greece", "Hungary"]
is_source = {"Germany": False, "Syria": True, "Tunisia": True, "Greece": False, "Hungary": False}

travel_routes = [
    ("Syria", "Hungary", 1),
    ("Hungary", "Germany", 1),
    ("Tunisia", "Greece", 1),
    ("Greece", "Germany", 1),
    ("Greece", "Hungary", 1)
]

danger_edge = {
    ("Syria", "Hungary"): 0.2,
    ("Hungary", "Germany"): 0.2,
    ("Tunisia", "Greece"): 0.2,
    ("Greece", "Germany"): 0.5,
    ("Greece", "Hungary"): 0.2
}

country_capacity = {
    "Germany":100.0,
    "Syria":0.0,
    "Tunisia":0.0,
    "Greece":50.0,
    "Hungary":100.0
}

country_refugees = {
    "Germany":0.0,
    "Syria":150.0,
    "Tunisia":100.0,
    "Greece":0.0,
    "Hungary":0.0
}

def danger_product(node_tuple):
    product = 1
    for i in range(len(node_tuple) - 1):
        product = product*(1 - danger_edge[(node_tuple[i], node_tuple[i+1])])
    return product

def danger(node_tuple):
    if len(node_tuple) == 1: return 0
    else: return danger(node_tuple[:-1]) + danger_product(node_tuple[:-1])*danger_edge[node_tuple[-2:]]

def danger_probabilities(curve_1, curve_2):
    pass

# Create Graph Structure
G = nx.DiGraph()
for country in countries: G.add_node(country, source = is_source[country])
G.add_weighted_edges_from(travel_routes)

# Find all simply paths from source nodes to other nodes.
path_list = [
    set(tuple(x) for x in nx.all_simple_paths(G, x, y))
    for (x,y) in product(countries, countries) if is_source[x]
]
paths = list(set.union(*path_list))
dangers = {path:danger(path) for path in paths}

# Variables to represent the linear program:
# We wish to max <f,x>, subject to Mx <= B.
f = np.array([(dangers[path] + len(path)) for path in paths])
M = np.array([])
b = np.array([])

for country in (country for country in countries if is_source[country]):
    newrow = np.array([(1.0 if path[0] == country else 0.0) for path in paths])
    if (M.shape == (0,)): M = np.vstack([newrow, -newrow])
    else:
        M = np.vstack([M, newrow])
        M = np.vstack([M, -newrow])
    if (b.shape == (0,)): b = np.vstack([np.array(country_refugees[country]), np.array(-country_refugees[country])])
    else: b = np.vstack([b, country_refugees[country], -country_refugees[country]])

for country in (country for country in countries if not is_source[country]):
    newrow = np.array([(1.0 if path[-1] == country else 0.0) for path in paths])
    M = np.vstack([M, newrow])
    b = np.vstack([b, country_capacity[country]])

# Run linear program
x = linprog(f,M,b)['x']
print(len(paths))
for i in range(len(paths)): print(paths[i], x[i])

# Add Quadratic Factor to program
Q = 2*B*np.identity(len(paths))
better_x = solvers.qp(matrix(Q), matrix(f), matrix(M), matrix(b))['x']
for i in range(len(paths)): print(paths[i], better_x[i])

#print(matrix(Q))
#print(matrix(f))
#print(matrix(M))
#print(matrix(b))

#print(M)
#print(b)

#for node in G.nodes():
#    print(node)

#for edge in G.edges():
#    print(edge)

#nx.draw(G)
#plt.show()