from collections import namedtuple
from graphviz import Digraph
import nltk
from english import letters, word_set, word_list, smallest_distance_to_any_english_word
from PIL import Image
import matplotlib.pyplot as plt

class String:

    Backlink = namedtuple("Backlink", ["edit_description", "parent", "cost"])

    def __init__(self, string, graph, backlink = None):
        assert type(string) == str
        self.string = string
        self.graph = graph
        self.length = len(string)
        self.backlink = backlink
        self._distance = None
        self._cost = None
        #self.add_to_graphviz()

    def children(self):

        string, parent, children = self.string, self, []

        allowed_transitions = self.graph.allowed_transitions

        # Generate Inserts
        if "i" in allowed_transitions:
            for i in range(len(self.string) + 1):
                for letter in letters:
                    edited_string = string[:i] + letter + string[i:]
                    edit_description = "insert({},{})".format(i,letter)
                    child = String(edited_string, self.graph, backlink = String.Backlink(edit_description, parent, 1.0) )
                    children.append(child)

        # Generate Transpositions
        if "t" in allowed_transitions:
            for i in range(len(self.string) - 1):
                edited_string = string[:i] + string[i+1] + string[i] + string[i+2:]
                edit_description = "transpose({},{})".format(i, i + 1)
                child = String(edited_string, self.graph, backlink = String.Backlink(edit_description, parent, 1.0))
                children.append(child)

        # Generate Deletes
        if "d" in allowed_transitions:
            for i in range(len(self.string)):
                edited_string = string[:i] + string[i+1:]
                edit_description = "delete({})".format(i)
                child = String(edited_string, self.graph, backlink = String.Backlink(edit_description, parent, 1.0))
                children.append(child)            

        return children

    def is_goal(self):
        return self.string.lower() in word_set

    def distance(self):
        if self._distance is None:
            self._distance = smallest_distance_to_any_english_word(self.string)
        return self._distance

    def is_root(self):
        return self.backlink is None

    def cost(self):
        if self._cost is None:
            cost = 0
            x = self
            while x.backlink is not None:
                x = x.backlink.parent
                cost += x.backlink.cost
            self._cost = cost
        return self._cost           

    def path(self):
        path = [self]
        x = self
        while x.backlink is not None:
            x = x.backlink.parent
            path.append(x)
        return path            

    def __eq__(self, other):
        if not isinstance(other, String):
            return False
        else:
            return self.string == other.string

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.string)

    def __str__(self):
        return self.string

class StringGraph:

    def __init__(self, string, allowed_transitions = None):
        self.graphviz = Digraph(format="png")
        self.graphviz.graph_attr.update(rank='min')
        self.initial_state = String(string, self)
        self.allowed_transitions = allowed_transitions or "idt"
        self.rendered_edges = set()
        self.rendered_nodes = set()
        self._fig = None
        self._img_plot = None


    def start_node(self):
        return self.initial_state

    def init_viz(self):

        fig = plt.figure()
        img_plot = plt.subplot(111)

        img_plot.axis("off")
        img_plot.autoscale(enable=True) 

        self._fig = fig
        self._img_plot = img_plot.imshow([[0]])

        return self._fig        

    def redraw(self, queued, visited, current, path, snapshot):

        if self.graphviz is None:
            return

        g = self.graphviz
        
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

        # Splat to matplotlib
        f = g.render()
        img = Image.open(f)
        self._img_plot.set_data(img)
        self._fig.tight_layout()
        self._fig.canvas.draw_idle()


        plt.pause(0.001) # Trigger a draw update


    

                