from collections import namedtuple
from graphviz import Digraph
import nltk
from english import letters, word_set

class String:

    Backlink = namedtuple("Backlink", ["edit_description", "parent", "cost"])

    def __init__(self, string, graph, backlink = None):
        assert type(string) == str
        self.string = string
        self.graph = graph
        self.length = len(string)
        self.backlink = backlink
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

    def add_to_graphviz(self):
        self.add_node_to_graphviz()
        self.add_backlink_to_graphviz()

    def add_node_to_graphviz(self):
        
        if self.graph is None or self.graph.graphviz is None:
            return

        g = self.graph.graphviz
        
        is_root = self.backlink is None
        is_goal = self.is_goal()

        if is_goal:
            g.node(self.string, self.string, shape = "doublecircle", style = "filled", color = "green")
        elif is_root:
            g.node(self.string, self.string, shape = "doublecircle", style = "filled", color = "gray")
        else:
            g.node(self.string, self.string, shape = "circle")

    def add_backlink_to_graphviz(self):

        if self.graph is None or self.graph.graphviz is None:
            return

        g = self.graph.graphviz
        
        is_root = self.backlink is None

        if not is_root:
            g.edge(self.backlink.parent.string, self.string, label = self.backlink.edit_description)   

    def is_goal(self):
        return self.string.lower() in word_set

    def is_root(self):
        return self.backlink is None

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
        self.graphviz = Digraph(format="svg")
        self.graphviz.graph_attr.update(rank='min')
        self.initial_state = String(string, self)
        self.allowed_transitions = allowed_transitions or "idt"
        self.rendered_edges = set()
        self.rendered_nodes = set()


    def start_node(self):
        return self.initial_state

    def redraw(self, filename, queued, visited, current, path, snapshot):

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
                    g.edge(node.backlink.parent.string, node.string, color = "yellow", label = node.backlink.edit_description)

        # Add the backlink between the current node and its previous if it hasn't already been rendered
        if not current.is_root():
            current_backedge = (current.backlink.parent.string, current.string)
            if current_backedge not in self.rendered_edges:
                g.edge(current_backedge[0], current_backedge[1], label = current.backlink.edit_description)

        # Queue Rendering?


        g.render(filename)



    

                