import pygame
import sys
from hex import Hex, Edge, Vertex, Point, Layout, ORIENTATION_POINTY

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class Game:

    def __init__(self, origin = Point(400, 400), size = Point(50, 50)) -> None:
        self.origin = origin
        self.size = size
        self.layout = Layout(ORIENTATION_POINTY, self.size, self.origin)
        self.hexes: list[Hex] = []
        self.edges: list[Edge] = []
        self.vertices: list[Vertex] = []
        self.__init_pygame()

    def __init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Settlers of Catan")
        self.main()

    def add_hex_to_map(self, hex: Hex):
        if hex not in self.hexes:
            self.hexes.append(hex)

    def add_edge_to_map(self, edge: Edge):
        if edge not in self.edges:
            self.edges.append(edge)

    def add_vertex_to_map(self, vertex: Vertex):
        if vertex not in self.vertices:
            self.vertices.append(vertex)

    def draw_hexes(self) -> None:
        for hex in self.hexes:
            poly = hex.get_all_polygon_corners(self.layout)
            pygame.draw.polygon(self.screen, "DARKGREEN", poly)
            pygame.draw.polygon(self.screen, "BLACK", poly, 3)

    def draw_edges(self) -> None:
        for edge in self.edges:
            vertices = edge.get_adjacent_vertices()
            p1 = vertices[0].to_point(self.layout)
            p2 = vertices[1].to_point(self.layout)
            pygame.draw.line(self.screen, "GREY", (p1.x, p1.y), (p2.x, p2.y), 5)

    def draw_vertices(self) -> None:
        for vertex in self.vertices:
            p = vertex.to_point(self.layout)
            pygame.draw.circle(self.screen, "GREY", (p.x, p.y), 10)

    def main(self) -> None:
        running = True
        mode = "hex"
        while running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    p = Point(pos[0], pos[1])
                    if mode == "hex":
                        frac_hex = p.to_fractional_hex(self.layout)
                        hex = frac_hex.round()
                        self.add_hex_to_map(hex)
                    elif mode == "edge":
                        self.add_edge_to_map(Edge.from_point(self.layout, p))
                    elif mode == "vertex":
                        self.add_vertex_to_map(Vertex.from_point(self.layout, p))
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_h:
                        mode = "hex"
                    elif event.key == pygame.K_e:
                        mode = "edge"
                    elif event.key == pygame.K_v:
                        mode = "vertex"
                if event.type == pygame.QUIT:
                    running = False
        
            self.screen.fill("BEIGE")
            self.draw_hexes()
            self.draw_edges()
            self.draw_vertices()
            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    g = Game()