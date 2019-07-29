from collections import deque
from sortedcontainers import SortedList


def best_first_search(start):
    
    if (yield) == -1:
        return

    visited = set()
    queue   = SortedList([start], key = lambda x: x.distance())
    
    while len(queue) > 0:

        node = queue.pop(0)
        
        if node in visited:
            continue
        
        if node.is_goal():
            break

        visited.add(node)
        
        for child in node.children():
            queue.add(child)
        
        # Coroutine hack to communicate algorithm state back to viz
        if (yield node, visited, queue) == -1:
            return
    
    # Coroutine hack to communicate algorithm state back to viz
    yield node, visited, queue
    