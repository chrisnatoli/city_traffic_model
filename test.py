from traffic_components import *
from traffic_map import *
from nose.tools import *
import numpy as np


def test_contruct_simple_network():
    # Construct a simple network:
    # A --> B <==> C
    # Make a duplicate that starts out empty.
    A = Intersection()
    B = Intersection()
    C = Intersection()
    AB = Street(A, B)
    BC = Street(B, C)
    CB = Street(C, B)
    network1 = StreetNetwork.no_cars([A, B, C], [AB, BC, CB])
    network2 = StreetNetwork.empty()
    network2.intersections.append(A)
    network2.intersections.extend([B, C])
    network2.streets.append(AB)
    network2.streets.extend([BC, CB])

    # Check that instreets and outstreets are correct.
    assert_equal(A.outstreets, [AB])
    assert_equal(A.instreets, [])
    assert_equal(B.outstreets, [BC])
    assert_equal(B.instreets, [AB, CB])

    # Check that the streets' endpoints are correct.
    assert_equal(AB.tail, A)
    assert_equal(AB.head, B)
    assert_equal(BC.tail, B)
    assert_equal(BC.head, C)
    assert_equal(CB.tail, C)
    assert_equal(CB.head, B)

    # Check that the network's components are correct.
    assert A in network1.intersections
    assert B in network1.intersections
    assert C in network1.intersections
    assert AB in network1.streets
    assert BC in network1.streets
    assert CB in network1.streets

    # Check that network1 is the same as network2.
    assert_equal(network1.streets, network2.streets)
    assert_equal(network1.intersections,
                 network2.intersections)

    # Cut an edge.
    network1.cut_street(CB)
    assert CB not in network1.streets
    assert CB in network2.streets
    assert BC in network1.streets

    # Fail to cut an edge that contains a car.
    car = Car([BC], network1)
    assert car in BC.q.queue
    assert_raises(CannotCutStreetError,
                  network1.cut_street(BC))
    



def test_cars_on_simple_network():
    # Construct a simple network:
    # A --> B <==> C
    A = Intersection()
    B = Intersection()
    C = Intersection()
    AB = Street(A, B)
    BC = Street(B, C)
    CB = Street(C, B)
    network = StreetNetwork.no_cars([A, B, C], [AB, BC, CB])

    # Move car1 from AB to BC. Leave it in street BC.
    car1 = Car([AB, BC], network)
    assert car1 in network.cars
    assert_equal(car1.location, AB)
    car1.move()
    assert_equal(car1.location, BC)
    car1.move()
    assert_equal(car1.location, None)
    assert car1 not in BC.q.queue
    assert car1 not in network.cars

    # Place car2 and car3 in BC so that car3 is blocked.
    # Try and fail to move car3.
    car2 = Car([BC], network)
    assert car2 in network.cars
    car3 = Car([BC, CB], network)
    assert car3 in network.cars
    assert_raises(NotAtFrontOfQueueError, car3.move)

    # Move car2 then car3.
    car2.move()
    assert_equal(car2.location, None)
    assert car2 not in network.cars
    car3.move()
    assert_equal(car3.location, CB)
    car3.move()

    # Try a car with a disconnected path.
    car4 = Car([AB, CB], network)
    assert car4 in network.cars
    assert_raises(DisconnectedPathError, car4.move)



def test_construct_3x3_grid():
    network = StreetNetwork.square_lattice(3, 3)

    assert_equal(9, len(network.intersections))
    assert_equal(24, len(network.streets))
    
    # Check number of instreets == number of outstreets.  Also check
    # that there are four corners (identified by two
    # instreets/outstreets), four nodes at the sides of the square
    # (identified by three instreets/outstreets), and one node in the
    # center of the square (identified by four instreets/outstreets).
    corners = []
    sides = []
    center = None
    for node in network.intersections:
        assert_equal(len(node.outstreets), len(node.instreets))
        
        if len(node.outstreets) == 2:
            corners.append(node)
        elif len(node.outstreets) == 3:
            sides.append(node)
        elif len(node.outstreets) == 4:
            center = node
    assert_equal(4, len(corners))
    assert_equal(4, len(sides))
    assert center is not None

    # Check that all corners are connected to exactly two sides.
    for corner in corners:
        assert corner.outstreets[0] != corner.outstreets[1]
        for outstreet in corner.outstreets:
            assert outstreet.head in sides
        
    # Check that all sides are connected to the center and exactly two
    # corners.
    for side in sides:
        heads = [ outstreet.head for outstreet in side.outstreets ]
        assert center in heads
        heads.remove(center)

        assert heads[0] != heads[1]
        for head in heads:
            assert head in corners

    # Check that the center is connected to exacty four sides.
    for outstreet in center.outstreets:
        assert outstreet.head in sides



def test_dim_5x7_grid():
    network = StreetNetwork.square_lattice(5, 7)

    assert_equal(35, len(network.intersections))
    assert_equal(116, len(network.streets))
    


def test_shortest_path():
    # The graph is as follows, with nodes in parentheses and weights
    # in arrows:
    #
    # (A) ----9----> (B) ----24----> (C)--------------
    # |  \                          ^ | ^             \
    # |   14               --------/  2  \            |
    # |    \    ----18-----/          |   --6---     19
    # |     v  /                      v         \     |
    # 15    (D)---------30---------> (E)--11--->(F)   |
    # |     /                       ^  \         \    |
    # |    5                       /    \         6   |
    # |   /    ------------20-----/      ---16---\ \  |
    # v  v    /                                   v v v
    # (G)----/---------------------44------------> (H)
    #
    # Shortest path from A to H is ADCEH.

    A = Intersection('A')
    B = Intersection('B')
    C = Intersection('C')
    D = Intersection('D')
    E = Intersection('E')
    F = Intersection('F')
    G = Intersection('G')
    H = Intersection('H')
    nodes = [A, B, C, D, E, F, G, H]
    assert_equal(A.label, 'A')

    AB = Street(A, B, 9)
    BC = Street(B, C, 24)
    DE = Street(D, E, 30)
    EF = Street(E, F, 11)
    GH = Street(G, H, 44)
    AG = Street(A, G, 15)
    AD = Street(A, D, 14)
    DG = Street(D, G, 5)
    DC = Street(D, C, 18)
    CE = Street(C, E, 2)
    FC = Street(F, C, 6)
    CH = Street(C, H, 19)
    GE = Street(G, E, 20)
    EH = Street(E, H, 16)
    FH = Street(F, H, 6)
    edges = [AB, BC, DE, EF, GH, AG, AD,
             DG, DC, CE, FC, CH, GE, EH, FH]

    # Confirm the shortest path and that the reverse path is impossible.
    network = StreetNetwork.no_cars(nodes, edges)
    assert_equal([AD, DC, CE, EH],
                 network.shortest_path(A, H))
    assert_raises(DisconnectedPathError, network.shortest_path, H, A)

    # Replace CH with a shorter one so that it is now in the shortest path.
    network.cut_street(CH)
    CH = Street(C, H, 17)
    network.streets.append(CH)
    assert_equal([AD, DC, CH],
                 network.shortest_path(A, H))

    # Replace CH with another one of different length, so that the
    # path ADCH has the same length as ADCEH. Note that it
    # consistently picks the former, which is determined by the order
    # in which Dijsktra's algorithm looks at neighbors, which is in
    # turn determined by the order in which streets were connected to
    # intersections.
    network.cut_street(CH)
    CH = Street(C, H, 18)
    network.streets.append(CH)
    assert_equal([AD, DC, CH],
                 network.shortest_path(A, H))



def test_grid_with_weights():
    height = 6
    width = 5

    north_weights = np.ones((height-1, width))
    east_weights = np.ones((height, width-1))
    south_weights = np.ones((height-1, width))

    west_weights = np.ones((height, width))
    assert_raises(LatticeDimensionsError,
                  StreetNetwork.square_lattice,
                  width, height,
                  north_weights, east_weights,
                  south_weights, west_weights)
                                               
    west_weights = np.ones((height, width-1))
    network = StreetNetwork.square_lattice(height, width,
                                           north_weights, east_weights,
                                           south_weights, west_weights)
    for street in network.streets:
        assert_equal(street.weight, 1)

    west_weights = 2 * np.ones((height, width-1))
    network = StreetNetwork.square_lattice(height, width,
                                           north_weights, east_weights,
                                           south_weights, west_weights)
    for street in network.streets:
        if 'West' in street.label:
            assert_equal(street.weight, 2)
        else:
            assert_equal(street.weight, 1)

    node_labels = [ node.label for node in network.intersections ]
    for i in range(height):
        for j in range(width):
            assert (i,j) in node_labels



def test_traffic_map():
    network = StreetNetwork.square_lattice(5, 7)

    TrafficMap(network).draw()
