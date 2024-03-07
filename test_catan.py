from catan import CatanHex, CatanEdge, CatanVertex, CatanMap, Player, Settlement
from hex import Hex, Edge, Vertex, NE, E, SE, SW, W, NW
import unittest


class TestCatanMap(unittest.TestCase):

    def setUp(self):
        self.p1 = Player(0, "Nara", "red")
        self.p2 = Player(1, "Lukas", "blue")
        self.map = CatanMap()
        self.map.init_map()

    def test_build_settlement(self):
        v1 = Vertex(Hex(0, 0, 0), "N")
        v2 = Vertex(Hex(0, 0, 0), "NE")
        v3 = Vertex(Hex(0, 0, 0), "SE")
        self.p1.build_settlement(self.map, v1)
        self.assertTrue(self.map.catan_vertices[v1].has_building())
        self.assertTrue(self.map.catan_vertices[v1].has_building(self.p1))
        self.assertFalse(self.map.catan_vertices[v1].has_building(self.p2))
        self.assertFalse(self.map.may_build_settlement(self.p1, v2))
        self.assertTrue(self.map.may_build_settlement(self.p1, v3))
        
        e1 = Edge(Hex(0, 0, 0), NE)
        e2 = Edge(Hex(0, 0, 0), E)
        self.p1.build_street(self.map, e1)
        self.p1.build_street(self.map, e2)

        self.map.is_start = False
        self.assertTrue(self.map.may_build_settlement(self.p1, v3))
        self.assertFalse(self.map.may_build_settlement(self.p2, v3))
        self.assertFalse(self.map.may_build_settlement(self.p1, v2))
        self.assertFalse(self.map.may_build_settlement(self.p1, Vertex(Hex(0, 0, 0), "S")))
        
    def test_build_street(self):
        e1 = Edge(Hex(0, 0, 0), NE)
        e2 = Edge(Hex(0, 0, 0), E)
        e3 = Edge(Hex(0, 0, 0), SE)
        self.p1.build_street(self.map, e1)
        self.assertTrue(self.map.catan_edges[e1].has_building())
        self.map.is_start = False

        self.assertTrue(self.map.may_build_street(self.p1, e2))
        self.assertFalse(self.map.may_build_street(self.p1, e3))


if __name__ == "__main__":
    unittest.main()