import sys, time
from numpy.random import random
from grid import Grid
from depth_first_search import depth_first_search
from breadth_first_search import breadth_first_search
from best_first_search import best_first_search
from iterative_deepening import iterative_deepening
import instrumentation

algo_choice  = sys.argv[1]
space_choice = sys.argv[2]

if algo_choice == "depthfirst":
    algorithm = depth_first_search(start)
elif algo_choice == "breadthfirst":
    algorithm = breadth_first_search(start)
elif algo_choice == "bestfirst":
    algorithm = best_first_search(start)
elif algo_choice == "iterativedeepening":
    algorithm = iterative_deepening(start)

if space_choice == "grid":
    graph = Grid((25,50), obstacles = [(10,20,15,25), (5,15,30,35)], start = (12,12), goal = (12,37))
elif space_choice == "puzzle":
    graph = Puzzle()


start = graph.start_position()

next(algorithm)

def handle_close(evt):
    try:
        algorithm.send(-1)
    except StopIteration:
        pass

fig = graph.init_viz()
fig.canvas.mpl_connect('close_event', handle_close)

while True:
    try:
        current, visited, queued = algorithm.send(0)

        if current.is_goal():
            print("Goal!!!!!")

        #graph.mark_queued(queued)    
        #graph.mark_visited(visited)
        #graph.mark_current(current)
        instrumentation.take_snapshot()        
        graph.redraw(queued, visited, current, snapshot)
    except StopIteration:
        print("Booya!")
        break

input("...")
    
