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
        self.__init_pygame()

    def __init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Settlers of Catan")
        self.main()

    def add_hex_to_map(self, hex: Hex):
        if hex not in self.hexes:
            self.hexes.append(hex)

    def draw_hexes(self) -> None:
        for hex in self.hexes:
            poly = hex.get_all_polygon_corners(self.layout)
            pygame.draw.polygon(self.screen, "DARKGREEN", poly)
            pygame.draw.polygon(self.screen, "BLACK", poly, 3)

    def main(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    p = Point(pos[0], pos[1])
                    frac_hex = p.to_fractional_hex(self.layout)
                    hex = frac_hex.round()
                    self.add_hex_to_map(hex)
                if event.type == pygame.QUIT:
                    running = False
        
            self.screen.fill("BEIGE")
            self.draw_hexes()
            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    g = Game()