from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from hex import Hex, Edge, Vertex
from catan_constants import ResourceType
import random


@dataclass
class CatanHex(Hex):
    number_token: int
    resource_type: ResourceType
    has_robber: bool = False

    def __post_init__(self) -> None:
        super().__post_init__()

    def __eq__(self, other: object) -> bool:
        return super().__eq__(other)

    def set_robber(self, state: bool) -> None:
        self.has_robber = state


class CatanMap:

    def __init__(self) -> None:
        self.hexes: list[CatanHex] = []

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

                self.hexes.append(CatanHex(q, r, -q - r, number_token, resource_type))