from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Union
from hex import Hex, Edge, Vertex
from catan_constants import ResourceType
import random

# TODO: CatanGame sollte auf events von außen reagieren können, bzw. z.B. beim Start auf events warten

class State(Enum):
    GAME_START = 0
    ROUND_START = 1
    ROUND = 2
    GAME_END = 3


class CatanGame:

    def __init__(self, players: list[Player]) -> None:
        self.players = players
        self.current_player = players[0]
        self.dice = Dice(2)
        self.state = State.GAME_START
        self.map = CatanMap()
        self.map.init_map()
        self.game_start()

    def game_start(self) -> None:
        pass

    def next_player(self) -> None:
        self.current_player = self.players[(self.current_player.id + 1) % len(self.players)]


class CatanHex:

    def __init__(self, number_token: int, resource_type: ResourceType, has_robber: bool = False) -> None:
        self.number_token = number_token
        self.resource_type = resource_type
        self.has_robber = has_robber

    def set_robber(self, state: bool) -> None:
        self.has_robber = state


class CatanEdge:

    def set_building(self, building: Street) -> None:
        self.building = building

    def remove_building(self) -> None:
        del self.building

    def has_building(self, player: Union[Player, None] = None) -> bool:
        if player is None:
            return hasattr(self, "building")
        else:
            return hasattr(self, "building") and self.building.player == player


class CatanVertex:

    def set_building(self, building: Union[Settlement, City]) -> None:
        self.building = building

    def remove_building(self) -> None:
        del self.building

    def has_building(self, player: Union[Player, None] = None) -> bool:
        if player is None:
            return hasattr(self, "building")
        else:
            return hasattr(self, "building") and self.building.player == player
    

class CatanMap:

    def __init__(self) -> None:
        self.is_start = True
        self.catan_hexes: dict[Hex, CatanHex] = {}
        self.catan_edges: dict[Edge, CatanEdge] = {}
        self.catan_vertices: dict[Vertex, CatanVertex] = {}

    def init_map(self) -> None:
        self.create_random_map()
        self.create_edges()
        self.create_vertices()

    def build_settlement(self, settlement: Settlement, vertex: Vertex) -> None:
        self.catan_vertices[vertex].set_building(settlement)

    def build_street(self, street: Street, edge: Edge) -> None:
        self.catan_edges[edge].set_building(street)

    def may_build_settlement(self, player: Player, vertex: Vertex) -> bool:
        if vertex not in self.catan_vertices:
            return False

        if self.catan_vertices[vertex].has_building():
            return False
        
        for vertex_neighbor in vertex.get_adjacent_vertices():
            if vertex_neighbor in self.catan_vertices:
                if self.catan_vertices[vertex_neighbor].has_building():
                    return False
            
        if not self.is_start:
            player_streets = []
            for edge in vertex.get_adjacent_edges():
                if edge in self.catan_edges:
                    if self.catan_edges[edge].has_building():
                        player_streets.append(self.catan_edges[edge].building.player)
            if player not in player_streets:
                return False
            
            #TODO: If there are two streets from other players should return False

        return True

    def may_build_street(self, player: Player, edge: Edge) -> bool:
        if edge not in self.catan_edges:
            return False

        if self.catan_edges[edge].has_building():
            return False
        
        if not self.is_start:
            for edge_neighbor in edge.get_adjacent_edges():
                if edge_neighbor in self.catan_edges:
                    if self.catan_edges[edge_neighbor].has_building(player):
                        return True
            return False
                
        return True

    def has_adjacent_street(self, vertex: Vertex, player: Player) -> bool:
        for edge in vertex.get_adjacent_edges():
            if self.catan_edges[edge].has_building(player):
                return True
        return False

    def create_edges(self) -> None:
        for hex in self.catan_hexes:
            hex_edges = hex.get_adjacent_edges()
            for edge in hex_edges:
                if edge not in self.catan_edges:
                    self.catan_edges[edge] = CatanEdge()

    def create_vertices(self) -> None:
        for hex in self.catan_hexes:
            hex_vertices = hex.get_adjacent_vertices()
            for vertex in hex_vertices:
                if vertex not in self.catan_vertices:
                    self.catan_vertices[vertex] = CatanVertex()

    def create_random_map(self) -> None:
        resource_list = [ResourceType.NOTHING, 
                         ResourceType.BRICK, 
                         ResourceType.LUMBER, 
                         ResourceType.ORE, 
                         ResourceType.GRAIN, 
                         ResourceType.WOOL]
        resource_weights = [1, 3, 4, 3, 4, 4]
        number_tokens = [5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11]

        for q in range(-2, 3):
            r1 = max(-2, -q - 2)
            r2 = min(+2, -q + 2)
            for r in range(r1, r2 + 1):
                resource_type = random.choices(resource_list, weights=resource_weights)[0]
                index = resource_list.index(resource_type)
                resource_weights[index] -= 1
                if resource_weights[index] == 0:
                    del resource_weights[index]
                    del resource_list[index]
                
                if resource_type == ResourceType.NOTHING:
                    number_token = 0
                else:
                    number_token = number_tokens.pop(0)

                self.catan_hexes[Hex(q, r, - q - r)] = CatanHex(number_token, resource_type)


@dataclass
class Player:
    id: int
    name: str
    color: Union[str, tuple[int, int, int]]

    def __post_init__(self) -> None:
        self.settlements: list[Settlement] = [Settlement(self) for _ in range(5)]
        self.citys: list[City] = [City(self) for _ in range(4)]
        self.streets: list[Street] = [Street(self) for _ in range(15)]
        self.resources: dict[ResourceType, int] = {
            ResourceType.BRICK: 0, 
            ResourceType.LUMBER: 0, 
            ResourceType.ORE: 0, 
            ResourceType.GRAIN: 0, 
            ResourceType.WOOL: 0
            }
        self.development_cards: list[DevelopmentCard] = []
        self.victory_points: int = 0

    def roll_dice(self, dice: Dice) -> None:
        dice.roll()

    def build_settlement(self, map: CatanMap, building_spot: Vertex) -> None:
        if self.settlements != [] and map.may_build_settlement(self, building_spot):
            map.build_settlement(self.settlements.pop(), building_spot)

    def build_street(self, map: CatanMap, building_spot: Edge) -> None:
        if self.streets != [] and map.may_build_street(self, building_spot):
            map.build_street(self.streets.pop(), building_spot)


@dataclass
class Building:
    player: Player


class Settlement(Building):
    
    def __post_init__(self):
        self.resource_factor = 1


class City(Building):
    
    def __post_init__(self):
        self.resource_factor = 2


class Street(Building):
    pass


class Dice:

    def __init__(self, num_dice: int = 2) -> None:
        self.dice = [1 for _ in range(num_dice)]

    def __repr__(self) -> str:
        return str(self.get_dice_values())

    def roll(self) -> None:
        for i in range(len(self.dice)):
            self.dice[i] = random.randint(1, 6)
            
    def get_dice_values(self) -> list[int]:
        return self.dice
    
    def get_total_value(self) -> int:
        return sum(self.get_dice_values())
    

class DevelopmentCard:
    pass