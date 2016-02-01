# IMPORTS
import numpy as np
import csv
# =======

# Want:
# countries = rVec(labels_path)
# is_source (dictionary, bool)
# travel_routes = routes(labels, paths) 
# danger_edges = {edges(labels,paths) : value}
# country_capacity = -(flow.difference[country])
# country_refugees (dictionary: initial source values)

class rVec(object):
    cData = []
    def __init__(self, path):
        with open(path, 'rb') as d:
            self.f = csv.reader(d)
            # Fill vector
            self.cData = self.f.next()

    def rLabel(self, tup, weight=False):
        x = tup[0]
        y = tup[1]
        p = [self.cData[x], self.cData[y]]
        if(weight):
            p.append(1)
        return tuple(p)

class rMtx(object):
    cData = None
    cShape = None
    def __init__(self, path):
        with open(path, 'rb') as d:
            self.f = csv.reader(d)
            # Fill matrix
            mtx=[]
            for row in self.f:
                mtx.append( map(int,row) )
        self.cData = np.matrix(mtx)
        self.cShape = self.cData.shape
        assert self.cShape[0] == self.cShape[1]
    
    def rNonzero(self,weight=False):
        nz = self.cData.A.nonzero()
        if(weight):
            weights = map(self.cData.item,zip(nz[0],nz[1]))
            return zip(nz[0],nz[1],weights)
        else:
            return zip(nz[0],nz[1])

class rFlow(object):
    cFlowIn={}
    cFlowOut={}
    # We're only interested in flow for 
    # countries in scope
    def __init__(self,path_i,path_o,labels):
        read_i = csv.reader(open(path_i))
        for line in read_i:
            k = line[0]
            if k not in self.cFlowOut:
                self.cFlowOut[k]=0
            self.cFlowIn[k]=int(line[1])
        read_o = csv.reader(open(path_o))
        for line in read_o:
            k = line[0]
            if k not in self.cFlowIn:
                self.cFlowIn[k]=0
            self.cFlowOut[k]=int(line[1])

    def difference(self, key):
        return (self.cFlowOut[key]-self.cFlowIn[key])


def Routes(labels, paths):
    return map(lambda x: labels.rLabel(x,True), paths)

def Edges(labels, paths):
    return map(labels.rLabel, paths)

def Dangers(edges, risk):
    return {e: r for e in edges for r in risks}

if __name__ == "__main__":
    # execute, as main src
    labels_path = 'data/labels.csv'
    matrix_path = 'data/paths.csv'
    enter_path = 'data/enter.csv'
    exit_path = 'data/exit.csv'
    labels = rVec(labels_path)
    adjmatrix = rMtx(matrix_path)
    adjacencies = adjmatrix.rNonzero()
    weightedpaths = adjmatrix.rNonzero(True)
    routes = Routes(labels, adjacencies)
    edges = Edges(labels, adjacencies)
    flow = rFlow(enter_path,exit_path,labels)
    print flow.difference('Canada')
