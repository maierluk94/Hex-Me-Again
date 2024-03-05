from catan import CatanHex, CatanEdge, CatanVertex
import unittest

class TestCatanHex(unittest.TestCase):

    def test_equal(self):
        h1 = CatanHex(1, 0, -1, 8, 0)
        h2 = CatanHex(1, 0, -1, 4, 3)
        self.assertEqual(h1, h2)


if __name__ == "__main__":
    unittest.main()