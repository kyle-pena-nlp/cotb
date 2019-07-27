import math, random, json, os
from collections import namedtuple
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from instrumentation import ops, space
from graphviz import Digraph

class PuzzleState:

    Backlink = namedtuple("Backlink", ["edit_description", "parent", "cost"])

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

    def __init__(self, state, graph, backlink = None):
        self._state = state
        self._size  = state.shape[0]
        self._graph = graph
        self.backlink = backlink
        #self._add_to_graph_viz()
        self.string = str(self)
        self.cost = None

    def children(self):

        children = []

        # Find coordinates of zero entry
        ((y,), (x,)) = (self._state == 0).nonzero()

        # Get all piece positions around the empty slot
        pieces_around_empty_slot = {
            "UP": [y - 1, x    ], # UP
            "DOWN": [y + 1, x    ], # DOWN
            "LEFT": [y,     x - 1], # LEFT
            "RIGHT": [y,     x + 1] # RIGHT
        }

        # 
        for move, (_y,_x) in pieces_around_empty_slot.items():
            
            # Invalid piece position
            if _y < 0 or _y >= self._size:
                continue
            
            # Invalid piece position
            if _x < 0 or _x >= self._size:
                continue
            
            # Create a link to the parent
            backlink = PuzzleState.Backlink(move, self, 1.0)  

            # Slide the piece
            child_state = np.copy(self._state)
            child_state[y,  x] = child_state[_y, _x]
            child_state[_y,_x] = 0          

            # Valid piece to slide into the empty slot
            children.append(PuzzleState(child_state, self._graph, backlink))

        return children

    def shuffle(self, n = 50):
        x = self
        for i in range(n):
            x = random.choice(x.children())
            x.backlink = None
        self._state = np.copy(x._state)
        self._size = self._state.shape[0]
        self.backlink = None
        self.string = str(self)

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
            if x.backlink is None:
                break
            x = x.backlink.parent
        return path

    def cost(self):
        if self.cost is None:
            cost = 0
            x = self
            while x.backlink is not None:
                x = x.backlink.parent
                cost += x.backlink.cost
            self.cost = cost
        return self.cost

    def copy(self):
        return PuzzleState(np.copy(self._state), self._graph)

    def is_root(self):
        return self.backlink is None

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





class PuzzleGraph:

    BLANK    = 0
    SOLVED_STATES = {}

    def __init__(self, side_length):
        assert side_length % 2 == 1

        self._graphviz = None

        goal_state = PuzzleGraph.get_solved_state(side_length)
        self._goal = PuzzleState(goal_state, self)
        
        #self._start = self._goal.copy()
        #self._start.shuffle(50)

        self._start = PuzzleState(np.asarray([ [2, 3, 0], [1, 4, 5], [7, 8, 6] ]), self, None)

        self._graphviz = Digraph(format = "svg")
        self._graphviz.graph_attr.update(rank='min')

        self.rendered_nodes = set()
        self.rendered_edges = set()
             

    def start_node(self):
        return self._start

    def init_viz(self):
        pass

    def redraw(self, queued, visited, current, path, snapshot):

        if self._graphviz is None:
            return

        g = self._graphviz
        g.attr(rankdir = "LR")
        
        # For the parts of the graph that have been visited
        for node in visited:

            # If this node hasn't been rendered before, render it
            if node not in self.rendered_nodes:
                if node.is_root():
                    g.node(node.string, node.string, shape = "doublecircle", style = "filled", color = "gray")
                else:
                    g.node(node.string, node.string, shape = "circle", style = "", color = "black")
                self.rendered_nodes.add(node.string)

            # If the edge leading to this node hasn't been rendered before, render it
            if not node.is_root():
                edge = (node.backlink.parent.string, node.string)
                if edge not in self.rendered_edges:
                    g.edge(edge[0], edge[1], label = node.backlink.edit_description)
                    self.rendered_edges.add(edge)

        # Always render the current node - green for goal, gray for root, orange for anything else
        # Don't mark it as rendered, so that when the graph is re-rendered, it can be re-colored to something else (if need be)
        if current.is_goal():
            g.node(current.string, current.string, shape="doublecircle", style = "filled", color = "green")
        elif current.is_root():
            g.node(current.string, current.string, shape = "doublecircle", style = "filled", color = "gray")
        else:
            g.node(current.string, current.string, shape = "circle", style = "filled", color = "orange")

        # Change the color of all the nodes between the root and the current yellow if the current is the goal
        if current.is_goal():
            for node in path:
                is_goal = node == current
                is_root = node.backlink is None
                if not is_goal and not is_root:
                    g.node(node.string, node.string, shape = "circle", style = "filled", color = "yellow")
                    #g.edge(node.backlink.parent.string, node.string, color = "yellow", label = node.backlink.edit_description)

        # Add the backlink between the current node and its previous if it hasn't already been rendered
        if not current.is_root():
            current_backedge = (current.backlink.parent.string, current.string)
            if current_backedge not in self.rendered_edges:
                g.edge(current_backedge[0], current_backedge[1], label = current.backlink.edit_description)

        g.render()

    @staticmethod
    def get_solved_state(side_length):
        if side_length not in PuzzleGraph.SOLVED_STATES:
            numbers = np.full(side_length ** 2, 0, dtype = np.uint8)
            numbers[:(side_length ** 2 // 2)]  = range(1,side_length ** 2 // 2 + 1)
            numbers[-(side_length ** 2 // 2):] = range(side_length ** 2 // 2 + 1, side_length ** 2)
            state = numbers.reshape((side_length, side_length))
            PuzzleGraph.SOLVED_STATES[side_length] = state
        return PuzzleGraph.SOLVED_STATES[side_length]