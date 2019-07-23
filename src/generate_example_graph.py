from PIL import Image
from graphviz import Digraph

g = Digraph(format="png")
g.graph_attr.update(rank='min')

g.node("BTRHDY", "BTRHDY", shape = "doublecircle", style = "filled", color = "gray")
g.node("BRTHDY", "BRTHDY", shape = "circle")
g.node("BIRTHDY", "BIRTHDY", shape = "circle")
g.node("BIRTHDAY", "BIRTHDAY", shape = "doublecircle", style = "filled", color="green")

g.edge("BTRHDY", "BRTHDY", label = "  transpose(2,3)")
g.edge("BRTHDY", "BIRTHDY", label = "  insert(2,I)")
g.edge("BIRTHDY", "BIRTHDAY", label = "  insert(7,A)")

fn = g.render()

#image = Image.open(fn)
#image.show()