from collections import deque
from sortedcontainers import SortedList


def a_star_search(start):
    
    if (yield) == -1:
        return
    
    # Keep track of distance from initial to current node in a lookup
    costs       = { start: 0 }

    # Maintain a priority queue where the priority is based on a estimated total cost of a path that passes through the node
    priority    = { start: 0 }
    queue       = SortedList([start], key = lambda x: priority[x] )

    # Maintain a visited set to prevent going in circles
    visited     = set()

    # While there's something to explore
    while len(queue) > 0:

        # Pop the item with lowest priority (bets estimated total path length from initial state to goal)
        node = queue.pop(0)

        visited.add(node)
        
        if node.is_goal():
            break
        
        for child in node.children():
        
            # Calculate the cost of this node (total distance from initial state)
            child_cost = costs[node] + child.backlink.cost
            
            # Record the cost, esp. if it is a cheaper path to this node than previously discovered 
            if child_cost not in costs or child_cost < costs[child]:
                costs[child] = child_cost

                # Estimate the total cost of a path to the goal that passes through this node by adding distance from initial state to heuristic distance to goal 
                priority[child] = child_cost + child.distance()

                # Enqueue into priority queue.
                if child not in queue:
                    queue.add(child)
        
        # Coroutine hack to communicate algorithm state back to viz
        if (yield node, visited, queue) == -1:
            return
    
    # Coroutine hack to communicate algorithm state back to viz
    yield node, visited, queue
    