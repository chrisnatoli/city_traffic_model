import queue
import numpy as np



class DisconnectedPathError(Exception): pass
class NotAtFrontOfQueueError(Exception): pass
class CannotCutStreetError(Exception): pass
class LatticeDimensionsError(Exception): pass



class StreetNetwork:
    '''The system of streets and intersections is represented by a
    digraph. Nodes are Intersections, and edges are Streets. Streets
    are not merely ordered pairs of nodes but full Street objects.
    StreetNetworks also know a list of cars that move within them. If
    the StreetNetwork is a square lattice, then it knows the 2d arrays
    of intersections and north/east/south/west-bound streets.'''
    
    def __init__(self, intersections, streets, cars,
                 lattice=None, north_streets=None, east_streets=None,
                 south_streets=None, west_streets=None):
        '''Construct a street network as a simple digraph given the
        nodes and edges.'''

        self.intersections = intersections
        self.streets = streets
        self.cars = cars
        
        self.lattice = lattice
        self.north_streets = north_streets
        self.east_streets = east_streets
        self.south_streets = south_streets
        self.west_streets = west_streets

    @classmethod
    def empty(cls):
        '''Construct a street network with no nodes, edges, or
        cars, i.e., with empty lists.'''

        return cls([], [], [])

    @classmethod
    def no_cars(cls, intersections, streets):
        '''Construct a street network with no cars, but nodes and
        edges are given.'''
        
        return cls(intersections, streets, [])

    @classmethod
    def square_lattice(cls, height, width,
                       north_weights=None, east_weights=None,
                       south_weights=None, west_weights=None):
        '''Construct a street network on top of a square lattice
        (i.e., a grid), given the width (number of intersections going
        horizontally) and height (number of intersections going
        vertically) of the lattice.  All streets are
        bidirectional. The weights can be preset by giving 2d arrays
        of numbers, e.g., north_weights contains the weights of all
        northbound streets. If they are not given, then the
        constructor uses weights of 1.'''
        
        if north_weights is None: north_weights = np.ones((height-1, width)) 
        if east_weights is None: east_weights = np.ones((height, width-1)) 
        if south_weights is None: south_weights = np.ones((height-1, width)) 
        if west_weights is None: west_weights = np.ones((height, width-1)) 

        # First check that the dimensions of the weights arrays match
        # the given width and height.
        weights = { 'north':north_weights, 'east':east_weights,
                    'south':south_weights, 'west':west_weights }
        for name in weights:
            if name == 'north' or name == 'south':
                h = height - 1
                w = width
            elif name == 'east' or name == 'west':
                h = height
                w = width - 1
            
            if len(weights[name]) != h:
                raise LatticeDimensionsError(
                    'There are {} rows of {}_weights but there should be {}'
                    .format(len(weights[name]), name, h))

            if any([ (len(row) != w) for row in weights[name] ]):
                raise LatticeDimensionsError(
                    'A row in {}_weights has length {} but it should be {}'
                    .format(name,
                            [ len(row) for row in weights[name]
                              if len(row) != w ][0],
                            w))

        # Construct a 2d array of nodes.
        nodes = [ [ Intersection((i,j)) for j in range(width) ] 
                  for i in range(height) ]

        # Construct 2d arrays of streets in each of the four cardinal
        # directions, using the given weights. The street labels are
        # 'Direction: (a,b)->(c,d)' where (a,b) are the coordinates of
        # the tail and (c,d) are the coordinates of the head.
        south_streets = [ Street(nodes[i][j], nodes[i+1][j],
                                 weights['south'][i][j],
                                 'South: ({},{})->({},{})'.format(i,j,i+1,j))
                          for i in range(height-1) for j in range(width) ]
        north_streets = [ Street(nodes[i+1][j], nodes[i][j],
                                 weights['south'][i][j],
                                 'North: ({},{})->({},{})'.format(i+1,j,i,j))
                          for i in range(height-1) for j in range(width) ]
        east_streets = [ Street(nodes[i][j], nodes[i][j+1],
                                weights['east'][i][j],
                                 'East: ({},{})->({},{})'.format(i,j,i,j+1))
                         for i in range(height) for j in range(width-1) ]
        west_streets = [ Street(nodes[i][j+1], nodes[i][j],
                                weights['west'][i][j],
                                 'West: ({},{})->({},{})'.format(i,j+1,i,j))
                         for i in range(height) for j in range(width-1) ]
        streets = north_streets + east_streets + south_streets + west_streets
        
        flattened_nodes = []
        for row in nodes:
            flattened_nodes.extend(row)
        return cls(flattened_nodes, streets, [],
                   nodes, north_streets, east_streets,
                   south_streets, west_streets)

    def cut_street(self, street):
        '''Cleanly removes a given street from the network.'''

        if not street.q.empty:
            raise CannotCutStreetError(
                'Street {} has the following cars in its queue: {}.'
                .format(street, street.q.queue))

        self.streets.remove(street)
        street.tail.outstreets.remove(street)
        street.head.instreets.remove(street)

    def shortest_path(self, source, destination):
        '''Uses Dijkstra's algorithm to compute the shortest path in
        the network from the source to the destination. Returns a
        path, which is just a list of streets.'''
        
        # Initalize.
        nodes = []
        distance = dict()
        previous_step = dict()
        distance[source] = 0
        for node in self.intersections:
            if node != source:
                distance[node] = float('inf')
            previous_step[node] = None
            nodes.append(node)
        
        # Label the nodes with the least total distance from the
        # source as well as the previous step, i.e., the edge before
        # it that gives that least distance.
        while True:
            node = min([ node for node in nodes ], key=distance.get)
            if node == destination:
                break
            nodes.remove(node)
            
            for outstreet in node.outstreets:
                neighbor = outstreet.head
                alternative = distance[node] + outstreet.weight
                if alternative < distance[neighbor]:
                    distance[neighbor] = alternative
                    previous_step[neighbor] = outstreet

        # Backtrack from destination to source to build shortest path.
        path = []
        node = destination
        while previous_step[node] is not None:
            outstreet = previous_step[node]
            path.insert(0, outstreet)
            node = outstreet.tail
        
        if path == []:
            raise DisconnectedPathError(
                'There is no path whatsoever from {} to {}.'
                .format(source, destination))

        return path
        

class Intersection:
    '''Intersections are the nodes in the graph. They know the streets
    that lead into the intersection (instreets) and streets that lead
    out of the intersection (outstreets).'''

    def __init__(self, label=None):
        self.label = label
        self.instreets = []
        self.outstreets = []

    def __str__(self):
        if self.label is None:
            return '<{}.{} object at {}>'.format(
                self.__class__.__module__,
                self.__class__.__name__,
                hex(id(self)))
        else:
            return self.label



class Street:
    '''Streets are the weighted directed edges in the digraph. Despite
    their name, streets are never longer than one city block, i.e., a
    street is a segment that contains only two intersections, which
    are its endpoints. Also, streets are never bi-directional; this is
    achieved instead by two antiparallel streets. Streets contain
    information about its lanes as well as the queue of cars waiting
    at traffic lights.'''
    
    def __init__(self, tail, head, weight=1, label=None):
        # Will eventually contain lane information.
        self.tail = tail
        self.head = head
        self.weight = weight
        self.label = label
        self.q = queue.Queue()
        
        tail.outstreets.append(self)
        head.instreets.append(self)

    def __str__(self):
        if self.label is None:
            return '<{}.{} object at {}>'.format(
                self.__class__.__module__,
                self.__class__.__name__,
                hex(id(self)))
        else:
            return self.label



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
            raise DisconnectedPathError(
                ('The car {} attempted to move from {} to {}, but'
                 +'these streets were not joined by an intersection.')
                .format(self, self.location, next_street))
        if self != self.location.q.queue[0]:
            raise NotAtFrontOfQueueError(
                'The car {} could not leave the queue because it was'
                +'not at the front of the queue.')

        self.location.q.get()
        next_street.q.put(self)
        self.location = next_street
