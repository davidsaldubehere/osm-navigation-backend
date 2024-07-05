import path_finding

graph = [[0, 1, -1], [0, 2, 4], [1, 2, 3], [1, 3, 2], [1, 4, 2]]

print(path_finding.bellman_ford_no_interesections(graph, 5))