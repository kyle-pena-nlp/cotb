from collections import *
from instrumentation import *

def depth_first_search(start):

    if (yield) == -1:
        return

    visited = InstrumentedSet(set())
    queue   = InstrumentedDeque(deque([ start ]))

    while len(queue) > 0:

        node = queue.pop()
        
        if node.is_goal():
            break

        visited.add(node)
        
        for child in node.children():
            if child not in visited:
                queue.append(child)
        
        # Coroutine hack to communicate algorithm state back to viz
        if (yield node, visited, queue) == -1:
            return
    
    # Coroutine hack to communicate algorithm state back to viz
    yield node, visited, queue