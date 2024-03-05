import pygame
import sys
from hex import Hex, Edge, Vertex, Point, Layout, ORIENTATION_POINTY
from catan import CatanMap
from catan_constants import ResourceType

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

COLORS = {
    ResourceType.BRICK: "brown", 
    ResourceType.LUMBER: "darkgreen", 
    ResourceType.ORE: "grey", 
    ResourceType.GRAIN: "yellow", 
    ResourceType.WOOL: "lightgreen", 
    ResourceType.NOTHING: "beige"
    }

class Game:

    def __init__(self, origin = Point(400, 300), size = Point(50, 50)) -> None:
        self.origin = origin
        self.size = size
        self.layout = Layout(ORIENTATION_POINTY, self.size, self.origin)
        self.hexes: list[Hex] = []
        self.edges: list[Edge] = []
        self.vertices: list[Vertex] = []
        self.map = CatanMap()
        self.map.create_random_map()
        self.__init_pygame()

    def __init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Settlers of Catan")
        self.myfont = pygame.font.SysFont("monospace", 16)
        self.main()

    def draw_hexes(self) -> None:
        for hex in self.map.hexes:
            p = hex.to_point(self.layout)
            poly = hex.get_all_polygon_corners(self.layout)
            pygame.draw.polygon(self.screen, COLORS[hex.resource_type], poly)
            pygame.draw.polygon(self.screen, "BLACK", poly, 3)
            pygame.draw.circle(self.screen, (255, 255, 255), (p.x, p.y), 20)
            number_label = self.myfont.render(str(hex.number_token), 1, (0, 0, 0))
            self.screen.blit(number_label, (p.x - 8, p.y - 8))

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
        while running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    p = Point(pos[0], pos[1])
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