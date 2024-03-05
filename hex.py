"""Collection of classes needed to define hexagons and their edges and vertices
using cube coordinates for easy math operations.

Based on https://www.redblobgames.com/grids/hexagons/."""
from __future__ import annotations
from dataclasses import dataclass
import collections
import math

Orientation = collections.namedtuple("Orientation", \
              ["f0", "f1", "f2", "f3", "b0", "b1", "b2", "b3", "start_angle"])
Layout = collections.namedtuple("Layout", ["orientation", "size", "origin"])

ORIENTATION_POINTY = Orientation(math.sqrt(3.0), math.sqrt(3.0) / 2.0, 0.0, 3.0 / 2.0, \
                                 math.sqrt(3.0) / 3.0, -1.0 / 3.0, 0.0, 2.0 / 3.0, 0.5)
ORIENTATION_FLAT = Orientation(3.0 / 2.0, 0.0, math.sqrt(3.0) / 2.0, math.sqrt(3.0), \
                               2.0 / 3.0, 0.0, -1.0 / 3.0, math.sqrt(3.0) / 3.0, 0.0)

@dataclass
class Point:
    """Representation of a point on the screen. Needed for drawing purposes."""

    x: float
    y: float

    def __add__(self, other: Point) -> Point:
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Point) -> Point:
        return Point(self.x - other.x, self.y - other.y)
    
    def __truediv__(self, f: float) -> Point:
        return Point(self.x / f, self.y / f)

    def amount(self) -> int:
        return int(abs(self.x) + abs(self.y))

    def to_hex(self, layout: Layout) -> Hex:
        """Returns the hex at the position of the point."""
        return self.to_fractional_hex(layout).round()

    def to_fractional_hex(self, layout: Layout) -> FractionalHex:
        """Returns the fractional hex at the position of the point."""
        M = layout.orientation
        size = layout.size
        origin = layout.origin
        pt = Point((self.x - origin.x) / size.x, (self.y - origin.y) / size.y)
        q = M.b0 * pt.x + M.b1 * pt.y
        r = M.b2 * pt.x + M.b3 * pt.y
        return FractionalHex(q, r, -q - r)
    
    def to_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)


@dataclass
class Hex:
    """Represents a hex using cube coordinates."""

    q: int
    r: int
    s: int

    def __post_init__(self) -> None:
        assert self.q + self.r + self.s == 0, "q + r + s must be 0"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Hex):
            return NotImplemented
        return self.q == other.q and self.r == other.r and self.s == other.s

    def __add__(self, other: Hex) -> Hex:
        return Hex(self.q + other.q, self.r + other.r, self.s + other.s)
    
    def __sub__(self, other: Hex) -> Hex:
        return Hex(self.q - other.q, self.r - other.r, self.s - other.s)

    def __mul__(self, k: int) -> Hex:
        return Hex(self.q * k, self.r * k, self.s * k)
    
    def get_length(self) -> int:
        """Returns the distance from the origin."""
        return (abs(self.q) + abs(self.r) + abs(self.s)) // 2
    
    def distance_to(self, h: Hex) -> int:
        """Returns the distance to another hex."""
        return (self - h).get_length()
    
    def get_neighbor(self, hex_direction: Hex) -> Hex:
        """Returns the adjacent hex in the given direction."""
        assert hex_direction in HEX_DIRECTIONS, "hex_direction not from HEX_DIRECTIONS"
        return self + hex_direction
    
    def get_common_neighbors(self, h: Hex) -> list[Hex]:
        """Returns the common neighbors of this and another hex."""
        return [neighbor for neighbor in self.get_adjacent_hexes() if h.is_neighbor(neighbor)]
        
    def is_neighbor(self, h: Hex) -> bool:
        return self.distance_to(h) == 1
    
    def get_edge_to(self, h: Hex) -> Edge:
        """Returns the edge to a neighboring hex."""
        assert self.is_neighbor(h), "Can only get the edge to an adjecent hex"
        return Edge(self, h - self)

    def get_adjacent_hexes(self) -> list[Hex]:   
        """Returns all neighboring hexagons as a list."""
        return [self.get_neighbor(direction) for direction in HEX_DIRECTIONS]

    def get_adjacent_edges(self) -> list[Edge]:
        """Returns all adjacent edges as a list."""
        return [Edge(self, direction) for direction in HEX_DIRECTIONS]

    def get_adjacent_vertices(self) -> list[Vertex]:
        """Returns all adjacent vertices as a list, starting North."""
        return [Vertex(self, direction) for direction in VERTEX_DIRECTIONS]
    
    def get_polygon_corner(self, layout: Layout, direction: int) -> Point:
        """Returns a corner position of a hex as a point."""
        center = self.to_point(layout)
        offset = self._corner_offset(layout, direction)
        corner = Point(center.x + offset.x, center.y + offset.y)
        return corner
    
    def get_all_polygon_corners(self, layout: Layout) -> list[tuple]:
        """Returns all corner positions of a hex. Useful for drawing."""
        return [self.get_polygon_corner(layout, i).to_tuple() for i in range(0, 6)]
    
    def to_point(self, layout: Layout) -> Point:
        """Returns the center position of the hex as a point."""
        M = layout.orientation
        size = layout.size
        origin = layout.origin
        x = (M.f0 * self.q + M.f1 * self.r) * size.x
        y = (M.f2 * self.q + M.f3 * self.r) * size.y
        return Point(x + origin.x, y + origin.y)    

    def _corner_offset(self, layout: Layout, corner: int) -> Point:
        M = layout.orientation
        size = layout.size
        angle = 2.0 * math.pi * (M.start_angle - corner) / 6.0
        return Point(size.x * math.cos(angle), size.y * math.sin(angle))


@dataclass
class FractionalHex:
    """A fractional hex may use float as positions.
    Useful for converting the position of a point to the closest hex."""

    q: float
    r: float
    s: float

    def __post_init__(self) -> None:
        assert math.isclose(self.q + self.r + self.s, 0), "q + r + s must be 0"

    def round(self) -> Hex:
        """"Rounds to the nearest hex."""
        qi = int(round(self.q))
        ri = int(round(self.r))
        si = int(round(self.s))
        q_diff = abs(qi - self.q)
        r_diff = abs(ri - self.r)
        s_diff = abs(si - self.s)
        if q_diff > r_diff and q_diff > s_diff:
            qi = -ri - si
        else:
            if r_diff > s_diff:
                ri = -qi - si
            else:
                si = -qi - ri
        return Hex(qi, ri, si)


@dataclass
class Edge:
    """Represents the edge of a hexagon. Each hexagon points to 3 edges,
    in NW, NE and E directions."""

    h: Hex
    direction: Hex

    def __post_init__(self) -> None:
        if self.direction == W:
            self.h = self.h.get_neighbor(W)
            self.direction = E
        elif self.direction == SW:
            self.h = self.h.get_neighbor(SW)
            self.direction = NE
        elif self.direction == SE:
            self.h = self.h.get_neighbor(SE)
            self.direction = NW

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Edge):
            return NotImplemented
        if self.h == other.h and self.direction == other.direction:
            return True
        return False
    
    def get_adjacent_hexes(self) -> tuple[Hex, Hex]:
        """Returns the two adjacent hexes as a tuple."""
        return (self.h, self.h + self.direction)

    def get_adjacent_vertices(self) -> tuple[Vertex, Vertex]:
       """Returns the two adjacent vertices as a tuple."""
       v = Vertex(self.h, VERTEX_DIRECTIONS[HEX_DIRECTIONS.index(self.direction)])
       w = Vertex(self.h, VERTEX_DIRECTIONS[(HEX_DIRECTIONS.index(self.direction) + 1) % 6])
       return (v, w)
    
    def get_adjacent_edges(self) -> list[Edge]:
        """Returns the four adjacent edges as a list."""
        edges = []
        for v in self.get_adjacent_vertices():
            v_edges = v.get_adjacent_edges()
            for e in v_edges:
                if e != self:
                    edges.append(e)
        return edges

    def to_point(self, layout) -> Point:
        """Returns the position of the center of the edge."""
        vertices = self.get_adjacent_vertices()
        return ((vertices[0].to_point(layout) + vertices[1].to_point(layout)) / 2)
    
    @classmethod
    def from_point(self, layout: Layout, p: Point) -> Edge:
        """Creates an edge from its approximate center position."""
        h = p.to_hex(layout)
        h_edges = h.get_adjacent_edges()
        return min(h_edges, key=lambda e: (e.to_point(layout) - p).amount())


@dataclass
class Vertex:
    """Represents the vertex of a hexagon. Each hexagon points to 2 vertices,
    the top (N) and bottom (S) in pointy top orientation. 
    
    Allowed directions: N, NW, SW, S, SE, SW"""

    h: Hex
    direction: str
    
    def __post_init__(self) -> None:
        assert self.direction in VERTEX_DIRECTIONS, "Invalid direction"

        if self.direction == "NW":
            self.h = self.h + NW
            self.direction = "S"
        elif self.direction == "NE":
            self.h = self.h + NE
            self.direction = "S"
        elif self.direction == "SW":
            self.h = self.h + SW
            self.direction = "N"
        elif self.direction == "SE":
            self.h = self.h + SE
            self.direction = "N"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vertex):
            return NotImplemented
        if self.h == other.h and self.direction == other.direction:
            return True
        return False
    
    def __add__(self, other: Edge) -> Vertex:
        e_vertices = other.get_adjacent_vertices()
        assert self in e_vertices, "Can only add an adjacent edge to a vertex"
        for vertex in e_vertices:
            if vertex != self:
                return vertex
        raise ValueError("No adjacent vertex found")
    
    def get_adjacent_hexes(self) -> list[Hex]:
        if self.direction == "N":
            return [self.h, self.h + NE, self.h + NW]
        else: 
            return [self.h, self.h + SE, self.h + SW]

    def get_adjacent_edges(self) -> tuple[Edge, Edge, Edge]:
        """Returns the three adjacent edges."""
        if self.direction == "N":
            return (Edge(self.h, NW), Edge(self.h, NE), Edge(self.h + NE, W))
        else:
            return (Edge(self.h, SW), Edge(self.h, SE), Edge(self.h + SE, W))
    
    def get_adjacent_vertices(self) -> tuple[Vertex, ...]:
        """Returns the closest three vertices."""
        edges = self.get_adjacent_edges()
        return tuple(self + e for e in edges)

    def distance_to(self, v: Vertex) -> int:
        """Calculate the distance to another vertex."""
        if self.direction != v.direction:
            # Need to find the closest hex after taking one step
            adjacent_hexes = self.get_adjacent_hexes()
            adjacent_hexes.remove(self.h)
            closest_hex = min(adjacent_hexes, key=lambda h: h.distance_to(v.h))
            return closest_hex.distance_to(v.h) * 2 + 1
        else:
            return self.h.distance_to(v.h) * 2
                    
    def to_point(self, layout: Layout) -> Point:
        """Returns the position of the vertex as a point."""
        h_point = self.h.to_point(layout)
        if self.direction == "N":
            return Point(h_point.x, h_point.y - layout.size.y)
        else:
            return Point(h_point.x, h_point.y + layout.size.y)
    
    @classmethod
    def from_point(cls, layout: Layout, p: Point) -> Vertex:
        """Creates a vertex from its approximate position."""
        h = p.to_hex(layout)
        h_vertices = h.get_adjacent_vertices()
        return min(h_vertices, key=lambda v: (v.to_point(layout) - p).amount())
    

# Directions in pointy top orientation
E = Hex(1, 0, -1)
NE = Hex(1, -1, 0)
NW = Hex(0, -1, 1)
W = Hex(-1, 0, 1)
SW = Hex(-1, 1, 0)
SE = Hex(0, 1, -1)
HEX_DIRECTIONS = [NE, E, SE, SW, W, NW]
VERTEX_DIRECTIONS = ["N", "NE", "SE", "S", "SW", "NW"]
