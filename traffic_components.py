import queue



class DisconnectedPathError(Exception): pass
class NotAtFrontOfQueueError(Exception): pass



class StreetNetwork:
    '''The system of streets and intersections is represented by a
    digraph. Nodes are Intersections, and edges are Streets. Streets
    are not merely ordered pairs of nodes; they also contain
    information about lanes and contain queues of cars waiting at
    traffic lights. Street networks also know the cars that move
    within them.'''
    
    def __init__(self, nodes, edges, cars):
        '''Construct a street network as a simple digraph given the
        nodes and edges.'''

        self.nodes = nodes
        self.edges = edges
        self.cars = cars

    @classmethod
    def empty(cls):
        '''Construct a street network with no nodes, edges, or
        cars, i.e., with empty lists.'''

        return cls([], [], [])

    @classmethod
    def no_cars(cls, nodes, edges):
        '''Construct a street network with no cars, but nodes and
        edges are given.'''
        
        return cls(nodes, edges, [])

    @classmethod
    def square_lattice(cls, width, height):
        '''Construct a street network on top of a square lattice
        (i.e., a grid), given the width and height of the lattice.
        All streets are bidirectional.'''
        
        nodes = [ [ Intersection() for i in range(width) ] 
                  for j in range(height) ]
        flattened_nodes = []
        for row in nodes:
            flattened_nodes.extend(row)

        horizontal_streets = [ Street(nodes[i][j], nodes[i][j+1])
                               for i in range(height)
                               for j in range(width - 1) ]
        vertical_streets = [ Street(nodes[i][j], nodes[i+1][j] )
                             for i in range(height - 1)
                             for j in range(width) ]
        streets = horizontal_streets + vertical_streets
        reverse_streets = [ Street(street.head, street.tail)
                            for street in streets ]
        streets.extend(reverse_streets)
        
        return cls(flattened_nodes, streets, [])

    def cut_edge(self, edge):
        '''Removes a given street from the network.'''
        self.edges.remove(edge)
        edge.tail.outstreets.remove(edge)
        edge.head.instreets.remove(edge)



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
        self.tail = tail
        self.head = head
        self.q = queue.Queue()
        
        tail.outstreets.append(self)
        head.instreets.append(self)



class Car:
    '''Cars are the agents in the system. A car is contained only in
    the queues of streets. It knows its path (a path is sequence of
    streets), which contains both its source and its destionation.
    It also knows the street network it belongs to.'''

    def __init__(self, path, network):
        self.location = path[0]
        self.path = path
        self.network = network

        self.location.q.put(self)
        self.network.cars.append(self)

    def move(self):
        '''Cars move by dequeueing themselves from their current
        street and enqueueing themselves in the next street they want
        to move to. Streets do not have to handle the dequeuing.
        Assumes that a path does not contain the same street twice.'''

        # Determine the next street to move to. If there are no more
        # streets to move to, then the car has reaches its destination
        # and leaves the system.
        index = self.path.index(self.location) + 1
        if index >= len(self.path):
            self.location.q.get()
            self.location = None
            self.network.cars.remove(self)
            return
        next_street = self.path[index]
        
        if next_street not in self.location.head.outstreets:
            raise DisconnectedPathError()
        if self != self.location.q.queue[0]:
            raise NotAtFrontOfQueueError()

        self.location.q.get()
        next_street.q.put(self)
        self.location = next_street
