from graphviz import Digraph
import csv

dot = Digraph(comment='Graph', format='png')
dot.attr(rankdir='BT', nodesep='0.5')

with open('out/node.csv', 'r') as f:
    for name, color in csv.reader(f):
        dot.node(name, name, color="black", fillcolor=color, style="filled")

with open('out/edge.csv', 'r') as f:
    for src, dst in csv.reader(f):
        dot.edge(src, dst)

dot.render('out/graph')  # Opens automatically
