from traffic_components import *
from nose.tools import *



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
    network2.nodes.append(A)
    network2.nodes.extend([B, C])
    network2.edges.append(AB)
    network2.edges.extend([BC, CB])

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
    assert A in network1.nodes
    assert B in network1.nodes
    assert C in network1.nodes
    assert AB in network1.edges
    assert BC in network1.edges
    assert CB in network1.edges

    # Check that network1 is the same as network2.
    assert_equal(network1.edges, network2.edges)
    assert_equal(network1.nodes, network2.nodes)



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
    assert_equal(car1.location, AB)
    car1.move()
    assert_equal(car1.location, BC)
    car1.move()
    assert_equal(car1.location, None)
    assert car1 not in BC.q.queue

    # Place car2 and car3 in BC so that car3 is blocked.
    # Try and fail to move car3.
    car2 = Car([BC], network)
    car3 = Car([BC, CB], network)
    assert_raises(NotAtFrontOfQueueError, car3.move)

    # Move car2 then car3.
    car2.move()
    assert_equal(car2.location, None)
    car3.move()
    assert_equal(car3.location, CB)
    car3.move()

    # Try a car with a disconnected path.
    car4 = Car([AB, CB], network)
    assert_raises(DisconnectedPathError, car4.move)



def test_construct_3x3_grid():
    network = StreetNetwork.square_lattice(3, 3)

    assert_equal(9, len(network.nodes))
    assert_equal(24, len(network.edges))
    
    # Check number of instreets == number of outstreets.  Also check
    # that there are four corners (identified by two
    # instreets/outstreets), four nodes at the sides of the square
    # (identified by three instreets/outstreets), and one node in the
    # center of the square (identified by four instreets/outstreets).
    corners = []
    sides = []
    center = None
    for node in network.nodes:
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

    assert_equal(35, len(network.nodes))
    assert_equal(116, len(network.edges))
    
