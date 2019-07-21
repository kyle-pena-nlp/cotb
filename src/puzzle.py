import math, random, json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from instrumentation import ops, space

class PuzzleState:

    SOLVED_STATES = {}

    @staticmethod
    def get_solved_state(side_length):
        if side_length not in PuzzleState.SOLVED_STATES:
            numbers = np.full(side_length ** 2, 0, dtype = np.uint8)
            numbers[:(side_length ** 2 // 2)]  = range(1,side_length ** 2 // 2 + 1)
            numbers[-(side_length ** 2 // 2):] = range(side_length ** 2 // 2 + 1, side_length ** 2)
            solved = PuzzleState(numbers.reshape((side_length, side_length)))
            PuzzleState.SOLVED_STATES[side_length] = solved
        return PuzzleState.SOLVED_STATES[side_length]

    def __init__(self, state, parent = None):
        self._state = state
        self._size  = state.shape[0]
        self.parent = parent

    def children(self):

        children = []

        # Find coordinates of zero entry
        ((y,), (x,)) = (self._state == 0).nonzero()

        # Get all piece positions around the empty slot
        pieces_around_empty_slot = [
            #[y - 1, x - 1],
            [y - 1, x    ],
            [y + 1, x    ],
            #[y - 1, x + 1],
            [y,     x - 1],
            [y,     x + 1],
            #[y + 1, x - 1],
            #[y + 1, x + 1],
        ]

        # 
        for (_y,_x) in pieces_around_empty_slot:
            
            # Invalid piece position
            if _y < 0 or _y >= self._size:
                continue
            
            # Invalid piece position
            if _x < 0 or _x >= self._size:
                continue
            
            # Slide the piece
            child = np.copy(self._state)
            child[y,  x] = child[_y, _x]
            child[_y,_x] = 0
            
            # Valid piece to slide into the empty slot
            children.append(self._make_node(child))

        return children

    def shuffle(self, n = 50):
        x = self
        for i in range(n):
            x = random.choice(x.children())
            x.parent = None
        self._state = np.copy(x._state)
        self._size = self._state.shape[0]
        self._parent = None

    def is_goal(self):
        return np.array_equal(self._state, PuzzleState.get_solved_state(self._size)._state)

    def distance(self):
        cost = 0
        for y in range(self._size):
            for x in range(self._size):
                value = self._state[y,x]
                if value == 0:
                    flat_index = self._size ** 2 // 2
                elif value <= self._size ** 2 // 2:
                    flat_index = value - 1
                else:
                    flat_index = value
                solved_y = flat_index // self._size
                solved_x = flat_index %  self._size
                this_cost = abs(y - solved_y) + abs(x - solved_x)
                cost += this_cost
        return cost

    def path(self):
        path = []
        x = self
        while True:
            path.append(x)
            if x.parent is None:
                break
            x = x.parent
        return path

    def copy(self):
        return PuzzleState(np.copy(self._state))

    # value comparison only
    def __eq__(self, other):
        return isinstance(other, self.__class__) and np.array_equal(self._state, other._state)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        # TODO: more efficient hashing
        return hash(self._state.data.tobytes())

    def _make_node(self, state):
        return PuzzleState(state, self)

class PuzzleGraph:

    BLANK    = 0

    def __init__(self, side_length):
        assert side_length % 2 == 1
        start = PuzzleState.get_solved_state(side_length).copy()
        start.shuffle(n = 50)
        self._start = start                

    def start_node(self):
        return self._start

    def init_viz(self):
        pass

    def redraw(self, queued, visited, current, path, snapshot):
        print(current._state)
        print(current.distance())
        #input("...")
        print(len(path))