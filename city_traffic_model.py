import queue



class Digraph:
    '''The network of streets is represented by a digraph.
    Nodes are Intersections, and edges are Streets. Streets are
    not merely ordered pairs of nodes; they also contain
    information about lanes and contain queues of cars waiting
    at traffic lights.'''
    
    def __init__(self, nodes=None, edges=None):
        if nodes is None:
            self.nodes = []
        else:
            self.nodes = nodes

        if edges is None:
            self.edges = []
        else:
            self.edges = edges

    def add_node(self, node):
        self.nodes.append(nodes)

    def add_edge(self, edge):
        self.edges.append(edges)



class Intersection:
    '''Intersections are the nodes in the graph. They know the
    streets that lead into the intersection (instreets) and streets
    that lead out of the intersection (outstreets).'''

    def __init__(self):
        self.instreets = []
        self.outstreets = []



class Street:
    '''Streets are the directed edges in the digraph. Despite
    their name, streets are never longer than one city block, i.e.,
    a street contains only two intersections, which are its
    endpoints. Also, streets are never bi-directional; this is
    achieved instead by two antiparallel streets. Streets contain
    information about its lanes as well as the queues
    of cars waiting at traffic lights.'''

    def __init__(self, tail, head): # Will eventually contain lane information.
        self.tail = tail
        self.head = head
        self.q = queue.Queue()
        
        if self not in tail.outstreets:
            tail.outstreets.append(self)
        if self not in head.instreets:
            head.instreets.append(self)

        
        
if __name__ == '__main__':
    A = Intersection()
    B = Intersection()
    street = Street(A, B)
    graph = Digraph([A, B], street)
