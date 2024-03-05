from hex import Point, Hex, Edge, Vertex, Layout, NE, NW, W, SW, SE, E, \
                HEX_DIRECTIONS, ORIENTATION_FLAT, ORIENTATION_POINTY
import math
import unittest

class TestHexInit(unittest.TestCase):

    def test_init(self):
        self.assertRaises(AssertionError, Hex, 3, 2, -1)


class TestHexArithmetic(unittest.TestCase):

    def setUp(self):
        self.h1 = Hex(0, 0, 0)
        self.h2 = Hex(1, 0, -1)
        self.h3 = Hex(2, -1, -1)

    def test_equal(self):
        self.assertEqual(self.h1, self.h1)
        self.assertEqual(self.h2, self.h2)
        self.assertNotEqual(self.h2, self.h3)

    def test_add(self):
        self.assertEqual(self.h1 + self.h2, self.h2)
        self.assertEqual(self.h1 + Hex(1, -1, 0) + self.h2, self.h3)
        self.assertNotEqual(self.h1 + self.h2, self.h3)

    def test_sub(self):
        self.assertEqual(self.h3 - self.h3, self.h1)
        self.assertEqual(self.h3 - Hex(1, -1, 0), self.h2)
        self.assertNotEqual(self.h1 - self.h2, self.h3)

    def test_mul(self):
        self.assertEqual(self.h1 * 5, self.h1)
        self.assertEqual(self.h2 * 2, Hex(2, 0, -2))
        self.assertNotEqual(self.h3 * 2, Hex(5, -2, -3))

    def test_mixed(self):
        self.assertEqual(self.h1 + self.h2 - self.h2, self.h1)
        self.assertEqual(self.h1 * 2 - self.h1, self.h1)
        self.assertEqual(self.h3 * 2 - self.h3 * 3, self.h1 - self.h3)
        self.assertEqual(self.h2 * 0, self.h1)
        self.assertEqual(self.h3 * 1, self.h3)


class TestHexNeighbors(unittest.TestCase):

    def setUp(self):
        self.h1 = Hex(0, 0, 0)
        self.h2 = Hex(1, 0, -1)
        self.h3 = Hex(2, -1, -1)

    def test_get_neighbor(self):
        self.assertEqual(self.h2.get_neighbor(NE), self.h3)
        self.assertEqual(self.h3.get_neighbor(SW), self.h2)
        self.assertEqual(self.h2.get_neighbor(W), self.h1)
        self.assertEqual(self.h1.get_neighbor(E).get_neighbor(NE), self.h3)
        self.assertNotEqual(self.h1.get_neighbor(NE), self.h3)

    def test_is_neighbor(self):
        self.assertTrue(self.h1.is_neighbor(self.h2))
        self.assertTrue(self.h3.is_neighbor(self.h2))
        self.assertTrue(self.h3.is_neighbor(Hex(3, -1, -2)))
        self.assertFalse(self.h1.is_neighbor(self.h3))

    def test_get_all_neighbors(self):
        self.assertListEqual(self.h1.get_adjacent_hexes(), HEX_DIRECTIONS)

    def test_get_common_neighbors(self):
        self.assertListEqual(self.h1.get_common_neighbors(self.h2), [Hex(1, -1, 0), Hex(0, 1, -1)])
        self.assertListEqual(self.h2.get_common_neighbors(self.h1), [Hex(0, 1, -1), Hex(1, -1, 0)])
        self.assertListEqual(self.h1.get_common_neighbors(self.h3), [Hex(1, -1, 0), self.h2])


class testHexDrawing(unittest.TestCase):

    def setUp(self):
        self.h1 = Hex(0, 0, 0)
        self.h2 = Hex(1, -1, 0)
        self.l1 = Layout(ORIENTATION_POINTY, Point(20, 30), Point(0, 0))
        self.l2 = Layout(ORIENTATION_FLAT, Point(50, 100), Point(100, 60))

    def test_to_point(self):
        p1 = self.h1.to_point(self.l1)
        p2 = self.h2.to_point(self.l1)
        p3 = self.h2.to_point(self.l2)
        self.assertEqual(p1, Point(0, 0))
        self.assertAlmostEqual(p2.x, 20 * (math.sqrt(3) - math.sqrt(3) / 2))
        self.assertAlmostEqual(p2.y, 30 * -3 / 2)
        self.assertAlmostEqual(p3.x, 100 + 50 * 3 / 2)
        self.assertAlmostEqual(p3.y, 60 + 100 * (math.sqrt(3) / 2 - math.sqrt(3)))


class TestHexEdgesAndVertices(unittest.TestCase):

    def setUp(self):
        self.h1 = Hex(0, 0, 0)
        self.h2 = Hex(1, 0, -1)
        self.h3 = Hex(0, 1, -1)

    def test_get_edge_to(self):
        e1 = self.h1.get_edge_to(self.h2)
        e2 = self.h2.get_edge_to(self.h3)
        self.assertEqual(e1, self.h2.get_edge_to(self.h1))
        self.assertEqual(e2, Edge(self.h2, SW))

    def test_get_adjacent_edges(self):
        edges1 = self.h1.get_adjacent_edges()
        edges2 = self.h2.get_adjacent_edges()
        self.assertEqual(edges1[5], Edge(self.h1, NW))
        self.assertEqual(edges1[3], Edge(self.h1, SW))
        self.assertEqual(edges2[4], edges1[1])
        
    def test_get_adjacent_vertices(self):
        vertices1 = self.h1.get_adjacent_vertices()
        vertices2 = self.h2.get_adjacent_vertices()
        self.assertEqual(vertices1[1], Vertex(Hex(1, -1, 0), "S"))
        self.assertEqual(vertices1[4], Vertex(Hex(-1, 1, 0), "N"))
        self.assertEqual(vertices1[2], vertices2[4])
        self.assertEqual(vertices1[1], vertices2[5])


class TestEdge(unittest.TestCase):

    def test_equal(self):
        e1 = Edge(Hex(0, 0, 0), NE)
        e2 = Edge(Hex(1, -1, 0), SW)
        e3 = Edge(Hex(2, -2, 0), SE)
        e4 = Edge(Hex(2, -1, -1), NW)
        e5 = Edge(Hex(-2, 0, 2), W)
        e6 = Edge(Hex(-3, 0, 3), E)
        self.assertEqual(e1, e2)
        self.assertEqual(e3, e4)
        self.assertEqual(e5, e6)

    def test_get_adjacent_hexes(self):
        e1 = Edge(Hex(0, 0, 0), NE)
        e2 = Edge(Hex(2, -2, 0), SE)

        self.assertEqual(e1.get_adjacent_hexes(), (Hex(0, 0, 0), NE))
        self.assertEqual(e2.get_adjacent_hexes(), (Hex(2, -1, -1), Hex(2, -2, 0)))

    def test_get_adjacent_vertices(self):
        e1 = Edge(Hex(0, 0, 0), E)
        v1 = Vertex(Hex(0, 0, 0), "NE")
        v2 = Vertex(Hex(1, 0, -1), "SW")
        vertices = e1.get_adjacent_vertices()
        self.assertTrue(v1 in vertices)
        self.assertTrue(v2 in vertices)

    def test_get_adjacent_edges(self):
        e1 = Edge(Hex(0, 0, 0), E)
        e2 = Edge(Hex(0, 0, 0), NE)
        e3 = Edge(Hex(0, 0, 0), SE)
        e4 = Edge(Hex(1, 0, -1), SW)
        e5 = Edge(Hex(1, 0, -1), NW)
        adjacent_edges = e1.get_adjacent_edges()
        for edge in (e2, e3, e4, e5):
            self.assertTrue(edge in adjacent_edges)
        self.assertTrue(e1 not in adjacent_edges)
        self.assertTrue(len(adjacent_edges) == 4)


class TestVertex(unittest.TestCase):

    def test_equal(self):
        v1 = Vertex(Hex(0, 0, 0), "NW")
        v2 = Vertex(Hex(0, -1, 1), "S")
        v3 = Vertex(Hex(1, -2, 1), "S")
        v4 = Vertex(Hex(0, -1, 1), "NE")
        v5 = Vertex(Hex(-1, 1, 0), "SE")
        v6 = Vertex(Hex(-1, 2, -1), "N")
        self.assertEqual(v1, v2)
        self.assertEqual(v3, v4)
        self.assertEqual(v5, v6)

    def test_add(self):
        e1 = Edge(Hex(0, 0, 0), E)
        v1 = Vertex(Hex(0, 0, 0), "NE")
        v2  = Vertex(Hex(0, 0, 0), "SE")
        self.assertEqual(v1 + e1, v2)
        self.assertEqual(v2 + e1, v1)
        self.assertRaises(AssertionError, v1.__add__, Edge(Hex(0, 0, 0), W))

    def test_get_adjacent_hexes(self):
        v1 = Vertex(Hex(0, 0, 0), "NE")
        h1 = Hex(0, 0, 0)
        h2 = h1 + E
        h3 = h1 + NE
        adjacent_hexes = v1.get_adjacent_hexes()
        for hex in (h1, h2, h3):
            self.assertTrue(hex in adjacent_hexes)
        self.assertTrue(len(adjacent_hexes) == 3)

    def test_get_adjacent_edges(self):
        v1 = Vertex(Hex(0, 0, 0), "NE")
        e1 = Edge(Hex(0, 0, 0), NE)
        e2 = Edge(Hex(1, 0, -1), NW)
        e3 = Edge(Hex(0, 0, 0), E)
        self.assertTupleEqual(v1.get_adjacent_edges(), (e1, e2, e3))

    def test_get_adjacent_vertices(self):
        v1 = Vertex(Hex(0, 0, 0), "NE")
        v2 = Vertex(Hex(0, 0, 0), "SE")
        v3 = Vertex(Hex(1, -1, 0), "SE")
        v4 = Vertex(Hex(0, 0, 0), "N")
        adjacent_vertices = v1.get_adjacent_vertices()
        for vertex in (v2, v3, v4):
            self.assertTrue(vertex in adjacent_vertices)
        self.assertTrue(v1 not in adjacent_vertices)
        self.assertTrue(len(adjacent_vertices) == 3)

    def test_distance_to(self):
        v1 = Vertex(Hex(-2, 0, 2), "S")
        v2 = Vertex(Hex(1, -1, 0), "N")
        v3 = Vertex(Hex(0, -2, 2), "N")
        v4 = Vertex(Hex(0, -2, 2), "S")
        self.assertEqual(v1.distance_to(v2), 7)
        self.assertEqual(v3.distance_to(v4), 3)
        self.assertEqual(v1.distance_to(v3), 7)
        self.assertEqual(v1.distance_to(v4), 4)
        self.assertEqual(v2.distance_to(v3), 4)

    def test_to_point(self):
        v1 = Vertex(Hex(0, 0, 0), "N")
        v2 = Vertex(Hex(2, -2, 0), "S")
        v3 = Vertex(Hex(-2, 1, 1), "S")
        l1 = Layout(ORIENTATION_POINTY, Point(20, 30), Point(0, 0))
        l2 = Layout(ORIENTATION_FLAT, Point(50, 100), Point(100, 60))
        p1 = v1.to_point(l1)
        p2 = v2.to_point(l1)
        p3 = v3.to_point(l1)
        p4 = v1.to_point(l2)
        self.assertAlmostEqual(p1.x, 0)
        self.assertAlmostEqual(p1.y, -30)
        self.assertAlmostEqual(p2.x, math.sqrt(3) * 20)
        self.assertAlmostEqual(p2.y, -60)
        self.assertAlmostEqual(p3.x, -math.sqrt(3) * 30)
        self.assertAlmostEqual(p3.y, 5/2 * 30)
        self.assertAlmostEqual(p4.x, 100)
        self.assertAlmostEqual(p4.y, -40)

    def test_from_point(self):
        l1 = Layout(ORIENTATION_POINTY, Point(20, 20), Point(0, 0))
        p1 = Point(15, 10)
        v1 = Vertex(Hex(0, 0, 0), "SE")
        self.assertEqual(Vertex.from_point(l1, p1), v1)


if __name__ == "__main__":
    unittest.main()
