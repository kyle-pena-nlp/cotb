from collections import deque

def breadth_first_search(start):

    if (yield) == -1:
        return
    
    visited = set()
    queue   = deque([ start ])

    while len(queue) > 0:

        node = queue.popleft()

        if node in visited:
            continue
        
        if node.is_goal():
            break
        
        for child in node.children():
            if child not in visited:
                visited.add(node)
                queue.append(child)
        
        # Coroutine hack to communicate algorithm state back to viz
        if (yield node, visited, queue) == -1:
            return
    
    # Coroutine hack to communicate algorithm state back to viz
    yield node, visited, queue