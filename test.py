from city_traffic_model import *
from nose.tools import *

def test_fail():
    assert 1 != 0

def test_success():
    assert 1 == 1

def divide(a,b):
    return a / b

def test_error():
    assert_raises(ZeroDivisionError, divide, 1, 0)

def test_contruct_simple_graph():
    # Construct a simple graph:
    # A --> B <==> C
    # Make a duplicate called graph2.
    A = Intersection()
    B = Intersection()
    C = Intersection()
    AB = Street(A, B)
    BC = Street(B, C)
    CB = Street(C, B)
    graph1 = Digraph([A, B, C], [AB, BC, CB])
    graph2 = Digraph()
    graph2.add_node(A)
    graph2.add_nodes([B, C])
    graph2.add_edge(AB)
    graph2.add_edges([BC, CB])

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

    # Check that the graph's components are correct.
    assert A in graph1.nodes
    assert B in graph1.nodes
    assert C in graph1.nodes
    assert AB in graph1.edges
    assert BC in graph1.edges
    assert CB in graph1.edges

    # Check that graph1 is the same as graph2.
    assert_equal(graph1.edges, graph2.edges)
    assert_equal(graph1.nodes, graph2.nodes)

    # Try to construct a street with endpoints of the wrong type.
    assert_raises(TypeError, Street, A, 'B')
    assert_raises(TypeError, Street, 'A', AB)


def test_cars_on_simple_graph():
    # Construct a simple graph:
    # A --> B <==> C
    A = Intersection()
    B = Intersection()
    C = Intersection()
    AB = Street(A, B)
    BC = Street(B, C)
    CB = Street(C, B)
    graph = Digraph([A, B, C], [AB, BC, CB])

    # Move car1 from AB to BC. Leave it in street BC.
    car1 = Car([AB, BC])
    assert_equal(car1.location, AB)
    car1.move()
    assert_equal(car1.location, BC)
    car1.move()
    assert_equal(car1.location, None)
    assert car1 not in BC.q.queue

    # Place car2 and car3 in BC so that car3 is blocked.
    # Try and fail to move car3.
    car2 = Car([BC])
    car3 = Car([BC, CB])
    assert_raises(NotAtFrontOfQueueError, car3.move)

    # Move car2 then car3.
    car2.move()
    assert_equal(car2.location, None)
    car3.move()
    assert_equal(car3.location, CB)
    car3.move()

    # Try a car with a disconnected path.
    car4 = Car([AB, CB])
    assert_raises(DisconnectedPathError, car4.move)
