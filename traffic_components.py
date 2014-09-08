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
    
    def __init__(self, intersections, streets, cars):
        '''Construct a street network as a simple digraph given the
        nodes and edges.'''

        self.intersections = intersections
        self.streets = streets
        self.cars = cars

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

    def cut_street(self, street):
        '''Cleanly removes a given street from the network.'''

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

    def __init__(self):
        self.instreets = []
        self.outstreets = []



class Street:
    '''Streets are the weighted directed edges in the digraph. Despite
    their name, streets are never longer than one city block, i.e., a
    street is a segment that contains only two intersections, which
    are its endpoints. Also, streets are never bi-directional; this is
    achieved instead by two antiparallel streets. Streets contain
    information about its lanes as well as the queue of cars waiting
    at traffic lights.'''
    
    def __init__(self, tail, head, weight=1):
        # Will eventually contain lane information.
        self.tail = tail
        self.head = head
        self.weight = weight
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
