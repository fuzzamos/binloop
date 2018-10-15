#!/usr/bin/env python
import sys
import re
import networkx as nx
import json
from networkx.readwrite import json_graph
from subprocess import check_output

if len(sys.argv) != 2:
    print "Insufficient arguments"
    exit()
filename = sys.argv[1]

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
with open(filename + ".json", "wb") as fp:
    fp.write( json.dumps( json_graph.node_link_data(G) ) )
