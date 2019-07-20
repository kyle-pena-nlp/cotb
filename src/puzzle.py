import math, random
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
            [y - 1, x - 1],
            [y - 1, x    ],
            [y - 1, x + 1],
            [y,     x - 1],

            [y,     x + 1],
            [y + 1, x - 1],
            [y + 1, x    ],
            [y + 1, x + 1],
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
        self._state = x._state
        self._size = self._state.shape[0]
        self._parent = None

    def is_goal(self):
        return np.array_equal(self._state, PuzzleState.SOLVED[self._size])

    def distance(self):
        cost = 0
        for y in range(self._size):
            for x in range(self._size):
                value = self._state[y,x]
                flat_index = value if value - 1 <= self._size // 2 else value
                solved_y = flat_index // self._size
                solved_x = flat_index %  self._size
                cost += abs(y - solved_y) + abs(x - solved_x)        
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

    # value comparison only
    def __eq__(self, other):
        return (isinstance(other, self.__class__) and np.array_equal(self._state, other._state)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        # TODO: more efficient hashing
        return hash(self._state.data.tobytes())

    def _make_node(self, state):
        return GridNode(state, self)

class PuzzleGraph:

    BLANK    = 0

    def __init__(self, side_length):
        assert side_length % 2 == 1
        start.shuffle(n = 50)
        self._start = start

    def reinit_grid(self):
        start_y, start_x = self._start
        self._grid[start_y,start_x] = Grid.START

        for (y1,y2,x1,x2) in self._obstacles:
            self._grid[y1:y2, x1:x2] = Grid.OBSTACLE

        goal_y, goal_x = self._goal
        self._grid[goal_y, goal_x] = Grid.GOAL
                

    def start_position(self):
        return GridNode(self, self._start)

    def has_position(self, pos):

        # De-structure position
        y, x = pos

        # Check that it is not out of bounds
        if not ((0 <= y < self._Y) and (0 <= x < self._X)):
            return False

        # Check that it is not within an obstacle
        for obstacle in self._obstacles:
            y1,y2,x1,x2 = obstacle
            if ((y1 <= y < y2) and (x1 <= x < x2)):
                return False

        return True

    def mark_current(self, node):
        y,x = node.pos()
        self._grid[y,x] = Grid.CURRENT

    def mark_visited(self, nodes):
        for node in nodes:
            y,x = node.pos()
            self._grid[y,x] = Grid.VISITED

    def mark_queued(self, nodes):
        goal_y, goal_x = self._goal
        for node in nodes:
            y,x = node.pos()
            if y == goal_y and x == goal_x:
                self._grid[y,x] = Grid.QUEUED_GOAL
            else:
                self._grid[y,x] = Grid.QUEUED

    def mark_path(self, nodes):
        # TODO
        pass

    def init_viz(self):
        fig, (img_plot, ops_plot, space_plot) = plt.subplots(3,1)


        #fig = plt.figure(constrained_layout=True)

        #gs = GridSpec(2, 2, figure=fig)
        #img_plot = fig.add_subplot(gs[0, :])
        #ops_plot   = fig.add_subplot(gs[1, 0])
        #space_plot = fig.add_subplot(gs[1, 1])

        img_plot.axis("off")
        img_plot.set_aspect('auto')
        ops_plot.set_title("Total Queue/Set Operations")
        space_plot.set_title("Total Queue/Set Size")

        self._fig = fig
        self._img = img_plot.imshow(self._grid)
        self._ops_plot = ops_plot
        self._space_plot = space_plot

        return self._fig

    def redraw(self):
        self._img.set_data(self._grid)
        
        self._ops_plot.plot(ops)
        
        self._space_plot.plot(space)
        
        self._fig.canvas.draw_idle()

        plt.pause(0.001) # Trigger a draw update