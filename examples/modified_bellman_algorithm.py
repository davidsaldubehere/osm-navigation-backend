def bellman_modified():
    distances = {}
    previous = {}
    #loop through each vertice and set the distance to infinity
    for vertice in G.vs:
        distances[vertice.index] = float('inf')
        previous[vertice.index] = None
    distances[node1_index.index] = 0
    for vertice in G.vs:
        for edge in G.es:
            if distances[edge.source] + edge['user_weight'] < distances[edge.target] and not check_path_intersection(previous, edge.source, edge.target, node1_index.index):
                distances[edge.target] = distances[edge.source] + edge['user_weight']
                previous[edge.target] = edge.source
    return distances, previous
def check_path_intersection(prev, source, target, start):
    path = set()
    path.add(target)
    while source != start:
        if source in path:
            return True
        path.add(source)
        source =  prev[source]
    return False
    
distances, previous = bellman_modified()
#Get the shortest path
path = []
current = node2_index.index
while current != None:
    path.append(current)
    current = previous[current]
path = path[::-1]