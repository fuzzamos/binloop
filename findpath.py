#!/usr/bin/env python
import sys
import re
from os.path import normpath
import networkx as nx
import json
from networkx.readwrite import json_graph
from subprocess import check_output

if len(sys.argv) not in [3, 4]:
    print "Insufficient arguments"
    exit()
filename = sys.argv[1]
targetFunction = sys.argv[2]
if len(sys.argv) == 4:
    depth = int(sys.argv[3])
else:
    depth = 5

if not filename.endswith('.json'):
    try:
        lines = check_output(["objdump", "-Cd", filename]).splitlines()
    except:
        exit()

    G = nx.DiGraph()
    curFunc = None
    for l in lines:
        m = re.match(r'^([0-9a-zA-Z]+)\s+<(.*)>:$', l)
        if m != None:
            curFunc = m.group(2)
            continue
        if curFunc == None:
            continue
        m = re.match(r'^.*\bcallq\s+([0-9a-zA-Z])+\s+<(.*)>$', l)
        if m != None:
            G.add_edge(curFunc, m.group(2))
else:
    with open(filename, 'rb') as fp:
        G = json_graph.node_link_graph( json.loads(fp.read()) )

for k in nx.ego_graph(G.reverse(), targetFunction, depth, center = False):
    print " -> ".join(nx.shortest_path(G, source=k, target=targetFunction))
