from instrumentation import *

def iterative_deepening(start):

    max_depth = 0
    success, killed   = False, False
    visited = InstrumentedSet(set())
    queue  = InstrumentedDeque(deque([ start ]))
    depths = InstrumentedDeque(deque([ 0     ]))

    while not success and not killed:
        
        visited.clear()
        queue.clear()
        depths.clear()

        queue.append(start)
        depths.append(0)
        
        while len(queue) > 0:

            node  = queue.pop()
            depth = depths.pop()
            
            if node in visited:
                continue
            
            if node.is_goal():
                success = True
                break

            visited.add(node)
            
            if depth <= max_depth:
                for child in node.children():
                    queue.append(child)
                    depths.append(depth+1)
            
            # Coroutine hack to communicate algorithm state back to viz
            if (yield node, visited, queue) == -1:
                return

        max_depth += 1

    # Coroutine hack to communicate algorithm state back to viz
    signal = (yield node, visited, queue)