#!/usr/bin/env python
import sys
import re
from os.path import normpath
import json
import random
from subprocess import check_output

MAX_LOOPS = 25

class GraphCycleFinder(object):
    def __init__(self, graph = None):
        self.fp = None
        self.graph = graph
        self.functionFilenameMapper = {}
        self.subGraphs = None
        self.loops = []
    def deleteInvalidReferences(self):
        tmpGraph = {}
        for k, v in self.graph.iteritems():
            v2 = []
            for _ in v:
                if not _ in self.graph:
                    continue
                v2 += [_]
            if len(v2) == 0:
                continue
            tmpGraph[k] = v2
        self.graph = tmpGraph
    def deleteNonCallingNodes(self):
        tmpGraph = {}

        for k, v in self.graph.iteritems():
            if len(v) == 0:
                continue
            tmpGraph[k] = v
        self.graph = tmpGraph
    def findNodeIslands(self):

        involvedNodesPerKey = {}

        for k, v in self.graph.iteritems():
            idsToProcess = [k]
            idsProcessed = set()
            idsIncluded = set()

            while True:
                for curId in idsToProcess:
                    idsIncluded.update( self.graph[curId] )
                    idsProcessed.update( [curId] )

                idsToProcess = idsIncluded - idsProcessed
                if len(idsToProcess) == 0:
                    break
            
            involvedNodesPerKey[k] = idsIncluded

        uniqueSets = []
        for k, v in involvedNodesPerKey.iteritems():
            if v not in uniqueSets:
                uniqueSets += [v]
        self.subGraphs = []
        for us in uniqueSets:
            curSubGraph = {}
            for k, v in involvedNodesPerKey.iteritems():
                if us == v:
                    curSubGraph[k] = self.graph[k]
            self.subGraphs += [ curSubGraph ]
    def findLoopsPerSubGraph(self):
        for subGraph in self.subGraphs:
            self.findLoops( subGraph, subGraph.keys() )
    def preprocessGraph(self):
        while True:
            oldLen = len(self.graph.keys())

            self.deleteInvalidReferences()
            self.deleteNonCallingNodes()

            if oldLen == len(self.graph.keys()):
                break
        self.findNodeIslands()
    def findLoops(self, curGraph, names, chain = []):
        if not type(names) == list:
            names = [names]
        for name in names:
            if chain:
                if name in chain:
                    theloop = chain[chain.index(name):] + [name]
                    if theloop not in self.loops:
                        print ", ".join([str(s) for s in theloop])
                        if self.fp:
                            self.fp.write(", ".join([str(s) for s in theloop]) + "\n")
                        self.loops += [theloop]
                        if len(self.loops) >= MAX_LOOPS:
                            return False
                    return
            if not name in curGraph:
                continue
            calling = curGraph[name]
            if not type(calling) == list:
                calling = [calling]
            for k in calling:
                if self.findLoops(curGraph, k, chain + [name]) == False:
                    return False
        return True

if len(sys.argv) != 2:
    print "Insufficient arguments"
    exit()
filename = sys.argv[1]
try:
    lines = check_output(["objdump", "-Cd", filename]).splitlines()
except:
    exit()

functions = {}
calls = {}
curFunc = None
for l in lines:
    m = re.match(r'^([0-9a-zA-Z]+)\s+<(.*)>:$', l)
    if m != None:
        functions[m.group(2)] = int(m.group(1), 16)
        curFunc = m.group(2)
        calls[curFunc] = []
        continue
    if curFunc == None:
        continue
    m = re.match(r'^.*\bcallq\s+([0-9a-zA-Z])+\s+<(.*)>$', l)
    if m != None:
        calls[curFunc] += [m.group(2)]
print filename
g = GraphCycleFinder()
g.graph = calls
g.preprocessGraph()
g.findLoopsPerSubGraph()
