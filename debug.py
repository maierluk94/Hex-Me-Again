import pygame
import sys
from hex import Hex, Edge, Vertex, Point, Layout, ORIENTATION_POINTY, NE, E, SE, SW, W, NW
from catan import CatanMap, CatanGame, Player
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
        self.game = CatanGame([Player(0, "Nara", "red"), Player(1, "Lukas", "blue")])
        self.map = self.game.map
        self.debug()
        self.__init_pygame()

    def __init_pygame(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Settlers of Catan")
        self.myfont = pygame.font.SysFont("monospace", 16)
        self.main()

    def debug(self):
        v1 = Vertex(Hex(0, 0, 0), "N")
        self.game.players[0].build_settlement(self.map, v1)
        v2 = Vertex(Hex(0, 0, 0), "S")
        self.game.players[1].build_settlement(self.map, v2)
        e1 = Edge(Hex(0, 0, 0), NE)
        self.game.players[0].build_street(self.map, e1)
        e2 = Edge(Hex(0, 1, -1), W)
        self.game.players[1].build_street(self.map, e2)
        self.map.is_start = False

    def draw_hexes(self) -> None:
        for hex in self.map.catan_hexes:
            p = hex.to_point(self.layout)
            poly = hex.get_all_polygon_corners(self.layout)
            pygame.draw.polygon(self.screen, COLORS[self.map.catan_hexes[hex].resource_type], poly)
            pygame.draw.polygon(self.screen, "black", poly, 3)
            if not self.map.catan_hexes[hex].number_token == 0:
                pygame.draw.circle(self.screen, (255, 255, 255), (p.x, p.y), 20)
                number_label = self.myfont.render(str(self.map.catan_hexes[hex].number_token), 1, (0, 0, 0))
                self.screen.blit(number_label, (p.x - 8, p.y - 8))

    def draw_edges(self) -> None:
        for edge in self.map.catan_edges:
            if self.map.may_build_street(self.game.current_player, edge):
                vertices = edge.get_adjacent_vertices()
                p1 = vertices[0].to_point(self.layout)
                p2 = vertices[1].to_point(self.layout)
                pygame.draw.line(self.screen, "white", (p1.x, p1.y), (p2.x, p2.y), 5)

    def draw_vertices(self) -> None:
        for vertex in self.map.catan_vertices:
            if self.map.may_build_settlement(self.game.current_player, vertex):
                p = vertex.to_point(self.layout)
                pygame.draw.circle(self.screen, "white", (p.x, p.y), 10)

    def draw_settlements(self) -> None:
        for vertex in self.map.catan_vertices:
            catan_vertex = self.map.catan_vertices[vertex]
            if catan_vertex.has_building():
                p = vertex.to_point(self.layout)
                pygame.draw.circle(self.screen, catan_vertex.building.player.color, (p.x, p.y), 10)

    def draw_streets(self) -> None:
        for edge in self.map.catan_edges:
            catan_edge = self.map.catan_edges[edge]
            if catan_edge.has_building():
                vertices = edge.get_adjacent_vertices()
                p1 = vertices[0].to_point(self.layout)
                p2 = vertices[1].to_point(self.layout)
                pygame.draw.line(self.screen, catan_edge.building.player.color, (p1.x, p1.y), (p2.x, p2.y), 5)

    def draw_circle(self, pos) -> None:
        pygame.draw.circle(self.screen, self.game.current_player.color, (pos[0], pos[1]), 10)

    def draw_line(self, pos) -> None:
        pygame.draw.line(self.screen, self.game.current_player.color, (pos[0] - 20, pos[1]), (pos[0] + 20, pos[1]), 5)

    def main(self) -> None:
        running = True
        mode = ""
        button1 = Button((255,0,0), 50, 200, 100, 50, 'Settlement')
        button2 = Button((255,0,0), 50, 260, 100, 50, 'Street')
        button3 = Button((255,0,0), 50, 320, 100, 50, 'Next Player')

        while running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if mode == "":
                        if button1.is_over(pygame.mouse.get_pos()):
                            mode = "settlement"
                        if button2.is_over(pygame.mouse.get_pos()):
                            mode = "street"
                        if button3.is_over(pygame.mouse.get_pos()):
                            self.game.next_player()
                            mode = ""
                    elif mode == "settlement":
                        pos = pygame.mouse.get_pos()
                        p = Point(pos[0], pos[1])
                        vertex = Vertex.from_point(self.layout, p)
                        self.game.current_player.build_settlement(self.map, vertex)
                        mode = ""
                    elif mode == "street":
                        pos = pygame.mouse.get_pos()
                        p = Point(pos[0], pos[1])
                        edge = Edge.from_point(self.layout, p)
                        self.game.current_player.build_street(self.map, edge)
                        mode = ""
                if event.type == pygame.QUIT:
                    running = False
        
            self.screen.fill("beige")
            button1.draw(self.screen, (0, 0, 0))
            button2.draw(self.screen, (0, 0, 0))
            button3.draw(self.screen, (0, 0, 0))
            self.draw_hexes()
            self.draw_streets()
            self.draw_settlements()
            if mode == "settlement":
                self.draw_vertices()
                self.draw_circle(pygame.mouse.get_pos())
            if mode == "street":
                self.draw_edges()
                self.draw_line(pygame.mouse.get_pos())
            pygame.display.flip()

        pygame.quit()
        sys.exit()


class Button:
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw(self, screen, outline=None):
        if outline:
            pygame.draw.rect(screen, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0)
            
        pygame.draw.rect(screen, self.color, (self.x,self.y,self.width,self.height),0)
        
        if self.text != '':
            font = pygame.font.SysFont(None, 20)
            text = font.render(self.text, 1, (0,0,0))
            screen.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def is_over(self, pos):
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
        return False


if __name__ == "__main__":
    g = Game()