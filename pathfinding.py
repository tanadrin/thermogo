# Implementation of A* pathfinding based on http://www.redblobgames.com/pathfinding/a-star/implementation.html
import heapq

# Nodes, start, and goal are graph nodes (see mapping.py)

def a_star_search(gamemap, start, goal, land_or_sea = 'land'):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    
    if land_or_sea == 'land':
        graph = gamemap.land_graph
    elif land_or_sea == 'sea':
        graph = gamemap.sea_graph
        
    came_from = {} # Dict of node : previous node
    cost_so_far = {} # Dict of node : cost to get there
    came_from[start] = None
    cost_so_far[start] = 0
    
    while not frontier.is_empty():
        current = frontier.get()
        
        if current == goal:
            break
        
        for next_node in graph[current.x][current.y].neighbors:
            new_cost = cost_so_far[current] + gamemap.get_cost(graph, current_node, next_node)
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                priority = new_cost + heuristic(goal, next_node)
                frontier.put(next_node, priority)
                came_from[next_node] = current
        
    return came_from, cost_so_far
    
class PriorityQueue:
    def __init__(self):
        self.elements = []
        
    def is_empty(self):
        return len(self.elements) == 0
    
    def put(self, node, priority):
        heapq.heappush(self.elements, (priority, node))
        
    def get_next_node(self):
        return heapq.heappop(self.elements)[1]
        
def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)
