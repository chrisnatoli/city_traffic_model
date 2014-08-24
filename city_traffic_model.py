import queue



class DisconnectedPathError(Exception): pass
class NotAtFrontOfQueueError(Exception): pass



class Digraph:
    '''The network of streets is represented by a digraph. Nodes are
    Intersections, and edges are Streets. Streets are not merely
    ordered pairs of nodes; they also contain information about lanes
    and contain queues of cars waiting at traffic lights.'''
    
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
        self.nodes.append(node)

    def add_nodes(self, nodes):
        self.nodes.extend(nodes)

    def add_edge(self, edge):
        self.edges.append(edge)

    def add_edges(self, edges):
        self.edges.extend(edges)



class Intersection:
    '''Intersections are the nodes in the graph. They know the streets
    that lead into the intersection (instreets) and streets that lead
    out of the intersection (outstreets).'''

    def __init__(self):
        self.instreets = []
        self.outstreets = []



class Street:
    '''Streets are the directed edges in the digraph. Despite their
    name, streets are never longer than one city block, i.e., a street
    contains only two intersections, which are its endpoints. Also,
    streets are never bi-directional; this is achieved instead by two
    antiparallel streets. Streets contain information about its lanes
    as well as the queues of cars waiting at traffic lights.'''
    
    def __init__(self, tail,  head): # Will eventually contain lane information.
        if type(tail) is not Intersection:
            raise TypeError('The tail is of type {}, not Intersection.'
                            .format(type(tail)))
        if type(head) is not Intersection:
            raise TypeError('The head is of type {}, not Intersection.'
                            .format(type(tail)))

        self.tail = tail
        self.head = head
        self.q = queue.Queue()
        
        tail.outstreets.append(self)
        head.instreets.append(self)



class Car:
    '''Cars are the agents in the system. A car is contained only in
    the queues of streets. It knows its path (a path is sequence of
    streets), which contains both its source and its destionation.'''

    def __init__(self, path):
        for i, street in enumerate(path):
            if type(street) is not Street:
                raise TypeError('The type of path[{}] is {}, not Street.'
                                .format(i, type(street)))

        self.location = path[0]
        self.path = path

        self.location.q.put(self)

    def move(self):
        '''Cars move by dequeueing themselves from their current
        street and enqueueing themselves in the next street they want
        to move to. Streets do not have to handle the dequeuing.
        Assumes that a path does not contain the same street twice.'''

        # Determine the next street to move to. If there are no more
        # streets to move to, then the car has reached its destination.
        index = self.path.index(self.location) + 1
        if index >= len(self.path):
            self.location.q.get()
            self.location = None
            return
        next_street = self.path[index]
        
        if next_street not in self.location.head.outstreets:
            raise DisconnectedPathError()
        if self != self.location.q.queue[0]:
            raise NotAtFrontOfQueueError()

        self.location.q.get()
        next_street.q.put(self)
        self.location = next_street
