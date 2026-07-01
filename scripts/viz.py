from graphviz import Digraph
import csv

dot = Digraph(comment='Graph', format='png')
dot.attr(rankdir='BT', nodesep='0.5')

with open('out/edge.csv', 'r') as f:
    for src, dst in csv.reader(f):
        dot.node(src, src)
        dot.node(dst, dst)
        dot.edge(src, dst)

dot.render('out/graph')  # Opens automatically
