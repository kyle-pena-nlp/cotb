import sys, time
from numpy.random import random
from grid import *
from puzzle import *
from autocorrect import *
from depth_first_search import depth_first_search
from breadth_first_search import breadth_first_search
from best_first_search import best_first_search
from iterative_deepening import iterative_deepening
from a_star_search import a_star_search
import instrumentation

algo_choice  = sys.argv[1]
space_choice = sys.argv[2]

if algo_choice == "bestfirst":
    obstacles = [(5,15,33,35), (5,7,20,35), (13,15,20,35)]
else:
    obstacles = [(10,20,15,25), (5,15,30,35)]

if space_choice == "grid":
    graph = Grid((25,50), obstacles = obstacles, start = (12,12), goal = (12,37))
elif space_choice == "puzzle":
    graph = PuzzleGraph(3)
elif space_choice == "autocorrect":
    canonical_string = "brithdya"
    graph = StringGraph(canonical_string, allowed_transitions = "td")

start = graph.start_node()

if algo_choice == "depthfirst":
    algorithm = depth_first_search(start)
elif algo_choice == "breadthfirst":
    algorithm = breadth_first_search(start)
elif algo_choice == "bestfirst":
    algorithm = best_first_search(start)
elif algo_choice == "iterativedeepening":
    algorithm = iterative_deepening(start)
elif algo_choice == "astar":
    algorithm = a_star_search(start)

next(algorithm)

if space_choice == "grid" or space_choice == "autocorrect":
    def handle_close(evt):
        try:
            algorithm.send(-1)
        except StopIteration:
            pass
    fig = graph.init_viz()
    fig.canvas.mpl_connect('close_event', handle_close)


i = 0
while True:
    try:
        current, visited, queued = algorithm.send(0)
        i+=1
        graph.redraw(queued, visited, current, current.path(), None)
        if current.is_goal():
            print("Goal!!!!")
            break
    except StopIteration:
        print("Finished.")
        break

input("Press [ENTER] to close.")
    
