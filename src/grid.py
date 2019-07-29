import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from instrumentation import INSTANCE_COUNT
from collections import namedtuple

class GridNode:

    Backlink = namedtuple("Backlink", ["direction", "parent", "cost"])

    def __init__(self, grid, start, backlink = None):
        self._grid = grid
        self._y, self._x = start
        self.backlink = backlink
        self._cost = None
        INSTANCE_COUNT[0] += 1

    def __del__(self):
        INSTANCE_COUNT[0] -= 1

    def children(self):

        # 4-Neighbors, starting at 12 o clock and then clockwise
        
        children = {
            "T":  (self._y - 1, self._x + 0),
            "TR": (self._y - 1, self._x + 1),
            "R":  (self._y + 0, self._x + 1),
            "BR": (self._y + 1, self._x + 1),
            "B":  (self._y + 1, self._x + 0),
            "BL": (self._y + 1, self._x - 1),
            "L":  (self._y + 0, self._x - 1),
            "TL": (self._y - 1, self._x - 1),
        }

        return [ self._make_node(child, direction) for direction, child in children.items() if self._grid._has_position(child) ]

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

    def cost(self):
        if self._cost is None:
            cost = 0
            x = self
            while True:
                cost += 1
                if x.backlink is None:
                    break
                x = x.backlink.parent
            self._cost = cost
        return self._cost

    def path(self):
        path = []
        x = self
        while True:
            path.append(x)
            if x.backlink is None:
                break
            x = x.backlink.parent
        return path

    # value comparison only
    def __eq__(self, other):
        return (isinstance(other, self.__class__) and self._y == other._y and self._x == other._x)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self._y, self._x))

    def _make_node(self, pos, direction):
        backlink = GridNode.Backlink(direction = direction, parent= self, cost = 1.0)
        return GridNode(self._grid, pos, backlink)

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

        fig = plt.figure()
        img_plot = plt.subplot(111)

        img_plot.axis("off")
        img_plot.set_aspect('auto')

        self._fig = fig
        self._img = img_plot.imshow(self._grid)

        return self._fig

    def redraw(self, queued, visited, current, path, snapshot):

        self._mark_queued(queued)
        self._mark_visited(visited)
        self._mark_current(current)
        if current.is_goal():
            self._mark_path(path)

        self._img.set_data(self._grid)
        self._fig.canvas.draw_idle()

        plt.pause(0.001) # Trigger a draw update