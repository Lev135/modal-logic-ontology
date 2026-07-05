from graphviz import Digraph
from collections import defaultdict
import csv

dot = Digraph(comment='Graph', format='png')
dot.attr(
    rankdir='BT',
    nodesep='0.5',
    ranksep='0.8',
    mclimit='15.0',
    newrank='true',
    # concentrate='true'
)

dot.attr('edge',
    color='#000000C0',
    # penwidth='1.0',
    arrowsize='0.8',
    arrowhead='vee'
)

with open('out/node.csv', 'r') as f:
    for name, color in csv.reader(f):
        dot.node(name, name, color="black", fillcolor=color, style="filled")

with open('out/edge.csv', 'r') as f:
    for src, dst in csv.reader(f):
        dot.edge(src, dst)

dot.render('out/graph')  # Opens automatically
