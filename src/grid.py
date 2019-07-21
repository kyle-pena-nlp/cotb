import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from instrumentation import INSTANCE_COUNT

class GridNode:

    def __init__(self, grid, start, parent = None):
        self._grid = grid
        self._y, self._x = start
        self.parent = parent
        INSTANCE_COUNT[0] += 1

    def __del__(self):
        INSTANCE_COUNT[0] -= 1

    def children(self):

        # 4-Neighbors, starting at 12 o clock and then clockwise
        
        children = [
            (self._y - 1, self._x + 0),
            (self._y - 1, self._x + 1),
            (self._y + 0, self._x + 1),
            (self._y + 1, self._x + 1),
            (self._y + 1, self._x + 0),
            (self._y + 1, self._x - 1),
            (self._y + 0, self._x - 1),
            (self._y - 1, self._x - 1),
        ]

        return [ self._make_node(child) for child in children if self._grid._has_position(child) ]

    def pos(self):
        return self._y, self._x

    def is_goal(self):
        goal_y, goal_x = self._grid._goal
        if self._y == goal_y and self._x == goal_x:
            return True
        return False

    def distance(self):
        goal_y, goal_x = self._grid._goal
        return (self._y - goal_y) ** 2.0 + (self._x - goal_x) ** 2.0

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
        return (isinstance(other, self.__class__) and self._y == other._y and self._x == other._x)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self._y, self._x))

    def _make_node(self, pos):
        return GridNode(self._grid, pos, self)

class Grid:

    BLANK    = 0
    VISITED  = 1
    OBSTACLE = 2
    QUEUED   = 3
    GOAL     = 4
    QUEUED_GOAL = 5
    CURRENT = 6
    START   = 7
    PATH    = 8

    def __init__(self, size, obstacles, start, goal):

        self._Y, self._X = size
        self._grid       = np.zeros(size, dtype = np.uint8)
        self._start      = start
        self._goal       = goal
        self._obstacles  = obstacles

        self._fig = None
        self._img = None
        self._ops_plot = None
        self._space_plot = None

        self.reinit_grid()

    def reinit_grid(self):
        start_y, start_x = self._start
        self._grid[start_y,start_x] = Grid.START

        for (y1,y2,x1,x2) in self._obstacles:
            self._grid[y1:y2, x1:x2] = Grid.OBSTACLE

        goal_y, goal_x = self._goal
        self._grid[goal_y, goal_x] = Grid.GOAL
                

    def start_node(self):
        return GridNode(self, self._start)

    def _has_position(self, pos):

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

    def _mark_current(self, node):
        if node is None:
            return
        y,x = node.pos()
        self._grid[y,x] = Grid.CURRENT

    def _mark_visited(self, nodes):
        if nodes is None:
            return
        for node in nodes:
            y,x = node.pos()
            self._grid[y,x] = Grid.VISITED

    def _mark_queued(self, nodes):
        if nodes is None:
            return
        goal_y, goal_x = self._goal
        for node in nodes:
            y,x = node.pos()
            if y == goal_y and x == goal_x:
                self._grid[y,x] = Grid.QUEUED_GOAL
            else:
                self._grid[y,x] = Grid.QUEUED

    def _mark_path(self, nodes):
        if nodes is None:
            return
        # TODO
        for node in nodes:
            y,x = node.pos()
            self._grid[y,x] = Grid.PATH

    def init_viz(self):
        #fig, (img_plot, ops_plot, space_plot) = plt.subplots(3,1)

        fig = plt.figure()
        img_plot = plt.subplot(221)
        ops_plot = plt.subplot(223)
        space_plot = plt.subplot(122)

        #fig = plt.figure(constrained_layout=True)

        #gs = GridSpec(2, 2, figure=fig)
        #img_plot = fig.add_subplot(gs[0, :])
        #ops_plot   = fig.add_subplot(gs[1, 0])
        #space_plot = fig.add_subplot(gs[1, 1])

        img_plot.axis("off")
        img_plot.set_aspect('auto')
        ops_plot.set_title("Operations Performed")
        space_plot.set_title("Space Allocated")

        self._fig = fig
        self._img = img_plot.imshow(self._grid)
        self._ops_plot = ops_plot
        self._space_plot = space_plot

        return self._fig

    def redraw(self, queued, visited, current, path, snapshot):

        self._mark_queued(queued)
        self._mark_visited(visited)
        self._mark_current(current)
        self._mark_path(path)

        self._img.set_data(self._grid)
        self._ops_plot.plot(snapshot["ops"])
        self._space_plot.plot(snapshot["space"])
        self._fig.canvas.draw_idle()

        plt.pause(0.001) # Trigger a draw update