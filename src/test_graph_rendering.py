from PIL import Image
from graphviz import Graph
from puzzle import PuzzleGraph

puzzle_graph = PuzzleGraph(3)
A = puzzle_graph.start_node()
B = A.copy()
B.shuffle(50)

g = Graph(format="png")
g.attr(fontsize='5')
g.attr(font="monospace")
g.node(str(hash(A)), str(A))
g.node(str(hash(B)), str(B))
g.edge(str(hash(A)), str(hash(B)))
fn = g.render()

image = Image.open(fn)
image.show()