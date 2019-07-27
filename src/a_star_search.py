from instrumentation import *
from collections import deque
from sortedcontainers import SortedList


def a_star_search(start):
    
    if (yield) == -1:
        return

    
    costs       = { start: 0 }
    priority    = { start: 0 }
    queue       = SortedList([start], key = lambda x: priority[x] )
    visited     = set()


    while len(queue) > 0:

        # Pop the item with lowest priority
        node = queue.pop(0)

        visited.add(node)
        
        if node.is_goal():
            break
        
        for child in node.children():
            child_cost = costs[node] + child.backlink.cost
            if child_cost not in costs or child_cost < costs[child]:
                costs[child] = child_cost
                priority[child] = child_cost + child.distance()
                if child not in queue:
                    queue.add(child)
        
        # Coroutine hack to communicate algorithm state back to viz
        if (yield node, visited, queue) == -1:
            return
    
    # Coroutine hack to communicate algorithm state back to viz
    yield node, visited, queue
    