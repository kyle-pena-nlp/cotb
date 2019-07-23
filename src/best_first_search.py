from instrumentation import *
from collections import deque

def best_first_search(start):
    
    if (yield) == -1:
        return

    visited = InstrumentedSet(set())
    queue   = InstrumentedList([ start ])
    
    while len(queue) > 0:

        node = queue.pop()
        
        if node in visited:
            continue
        
        if node.is_goal():
            break

        visited.add(node)
        
        for child in node.children():
            queue.append(child)

        queue.sort(key = lambda node: node.distance(), reverse = True)
        
        # Coroutine hack to communicate algorithm state back to viz
        if (yield node, visited, queue) == -1:
            return
    
    # Coroutine hack to communicate algorithm state back to viz
    yield node, visited, queue
    