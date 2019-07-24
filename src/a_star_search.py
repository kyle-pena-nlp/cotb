from instrumentation import *
from collections import deque
from sortedcontainers import SortedList


def a_star_search(start):
    
    if (yield) == -1:
        return

    # Visit items in order of priority ascending -- priority is calculated as we go
    priority    = { start: 0 }
    queue   = SortedList([start], key = lambda x: priority[x] )
    
    while len(queue) > 0:

        node = queue.pop(0)
        
        if node.is_goal():
            break
        
        for child in node.children():
            new_cost = child.cost()
            if child not in cost_so_far or new_cost < cost_so_far[child]:
                priority[child] = new_cost + child.distance()
                queue.put(child, priority)
        
        # Coroutine hack to communicate algorithm state back to viz
        if (yield node, visited, queue) == -1:
            return
    
    # Coroutine hack to communicate algorithm state back to viz
    yield node, visited, queue
    