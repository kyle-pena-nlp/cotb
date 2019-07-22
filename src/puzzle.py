import math, random, json, os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from instrumentation import ops, space
from graphviz import Digraph

class PuzzleState:

    SOLVED_STATES           = {}
    STRING_FORMAT_TEMPLATES = {}

    @staticmethod
    def get_string_format_template(side_length):
        
        if side_length not in PuzzleState.STRING_FORMAT_TEMPLATES:
            n = max(map(len,map(str,range(1,side_length**2)))) + 2
            template_line = (("|{:^" + str(n) + "}") * side_length) + "|" + os.linesep
            separator = "-" * ( (side_length * n) + (side_length + 1) ) + os.linesep
            template = (separator + template_line) * side_length + separator
            PuzzleState.STRING_FORMAT_TEMPLATES[side_length] = template
        return PuzzleState.STRING_FORMAT_TEMPLATES[side_length]

    def __init__(self, state, graph, parent = None):
        self._state = state
        self._size  = state.shape[0]
        self._graph = graph
        self.parent = parent
        self._add_to_graph_viz()

    def children(self):

        children = []

        # Find coordinates of zero entry
        ((y,), (x,)) = (self._state == 0).nonzero()

        # Get all piece positions around the empty slot
        pieces_around_empty_slot = [
            [y - 1, x    ], # UP
            [y + 1, x    ], # DOWN
            [y,     x - 1], # LEFT
            [y,     x + 1], # RIGHT
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
        return np.array_equal(self._state, self._graph._goal._state)

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
        return PuzzleState(np.copy(self._state), self._graph)

    # value comparison only
    def __eq__(self, other):
        return isinstance(other, self.__class__) and np.array_equal(self._state, other._state)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        # TODO: more efficient hashing
        return hash(self._state.data.tobytes())

    def __str__(self):
        string_format = PuzzleState.get_string_format_template(self._size)
        return string_format.format(*[ x or " " for x in self._state.ravel() ])

    def _make_node(self, state):
        return PuzzleState(state, self._graph, self)

    def _add_to_graph_viz(self):
        graphviz = self._graph._graphviz
        if graphviz is None:
            return
        _id = str(hash(self))
        if not "\t{}".format(_id) in graphviz.body:
            if self.is_goal():
                graphviz.node(_id, str(self), shape = "doublecircle")
            else:
                graphviz.node(_id, str(self), shape = "circle")
            if self.parent is not None:
                parent_id = str(hash(self.parent))
                graphviz.edge(parent_id, _id)



class PuzzleGraph:

    BLANK    = 0
    SOLVED_STATES = {}

    def __init__(self, side_length):
        assert side_length % 2 == 1

        self._graphviz = None

        goal_state = PuzzleGraph.get_solved_state(side_length)
        self._goal = PuzzleState(goal_state, self)
        self._start = self._goal.copy()
        self._start.shuffle(50)

        self._graphviz = Digraph(format = "svg")
        self._graphviz.graph_attr.update(rank='min')
             

    def start_node(self):
        return self._start

    def init_viz(self):
        pass

    def redraw(self, queued, visited, current, path, snapshot):
        self._graphviz.edge_attr.update(arrowhead='vee', arrowsize='2')   
        self._graphviz.render()


    @staticmethod
    def get_solved_state(side_length):
        if side_length not in PuzzleGraph.SOLVED_STATES:
            numbers = np.full(side_length ** 2, 0, dtype = np.uint8)
            numbers[:(side_length ** 2 // 2)]  = range(1,side_length ** 2 // 2 + 1)
            numbers[-(side_length ** 2 // 2):] = range(side_length ** 2 // 2 + 1, side_length ** 2)
            state = numbers.reshape((side_length, side_length))
            PuzzleGraph.SOLVED_STATES[side_length] = state
        return PuzzleGraph.SOLVED_STATES[side_length]