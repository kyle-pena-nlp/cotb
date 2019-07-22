from puzzle import *
from breadth_first_search import *
start = PuzzleGraph.get_solved_state(3).copy()
start.shuffle(1)
print("start\r\n", start._state)
algo = breadth_first_search(start)
next(algo)
while True:
    current, visited, queue = algo.send(0)
    print(current._state, "\r\n", PuzzleGraph.get_solved_state(3)._state, "\r\n", current == PuzzleGraph.get_solved_state(3))
    input("...")
    if current.is_goal():
        print("Goal.")
        break