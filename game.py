import sys
import math
from enum import Enum
import random
from operator import attrgetter

class Cell:
    def __init__(self, cell_index, richness, neighbors):
        self.cell_index = cell_index
        self.richness = richness
        self.neighbors = neighbors

    def get_richess_neighbor(self):
        max(c.cell_index for c in self.neighbors)

class Tree:
    def __init__(self, cell_index, size, is_mine, is_dormant):
        self.cell_index = cell_index
        self.size = size
        self.is_mine = is_mine
        self.is_dormant = is_dormant

class ActionType(Enum):
    WAIT = "WAIT"
    SEED = "SEED"
    GROW = "GROW"
    COMPLETE = "COMPLETE"

class Action:
    def __init__(self, type, target_cell_id=None, origin_cell_id=None):
        self.type = type
        self.target_cell_id = target_cell_id
        self.origin_cell_id = origin_cell_id

    def __str__(self):
        if self.type == ActionType.WAIT:
            return 'WAIT'
        elif self.type == ActionType.SEED:
            return f'SEED {self.origin_cell_id} {self.target_cell_id}'
        else:
            return f'{self.type.name} {self.target_cell_id}'

    @staticmethod
    def parse(action_string):
        split = action_string.split(' ')
        if split[0] == ActionType.WAIT.name:
            return Action(ActionType.WAIT)
        if split[0] == ActionType.SEED.name:
            return Action(ActionType.SEED, int(split[2]), int(split[1]))
        if split[0] == ActionType.GROW.name:
            return Action(ActionType.GROW, int(split[1]))
        if split[0] == ActionType.COMPLETE.name:
            return Action(ActionType.COMPLETE, int(split[1]))

class Game:
    def __init__(self):
        self.day = 0
        self.sun_direction = 0
        self.nutrients = 0
        self.board = []
        self.trees = []
        self.possible_actions = []
        self.my_sun = 0
        self.my_score = 0
        self.opponents_sun = 0
        self.opponent_score = 0
        self.opponent_is_waiting = 0

    def check_valid_complete_actions(actions):
        pass

    def plant_seed(self, seed_actions):
        target_cell_ids = [action.target_cell_id for action in seed_actions]
        target_cells = [cell for cell in self.board if cell.cell_index in target_cell_ids]
        richess_cell_for_seed = max(target_cells, key=attrgetter('richness'))
        #print('\n'+str(richess_cell_for_seed.cell_index), file=sys.stderr)

        return next(action for action in seed_actions if action.target_cell_id == richess_cell_for_seed.cell_index)

    def grow_tree(self, grow_actions):
        target_cell_ids = [action.target_cell_id for action in grow_actions]
        grow_cells = [cell for cell in self.board if cell.cell_index in target_cell_ids]
        #TODO: Check if any is size 2 and prioritize to grow that
        richess_cell_for_grow = max(grow_cells, key=attrgetter('richness'))

        return next(action for action in grow_actions if action.target_cell_id == richess_cell_for_grow.cell_index)

    def compute_next_action(self):
        my_trees = [tree for tree in self.trees if tree.is_mine]
        #CAN WE COMPLETE A TREE
        complete_actions = [action for action in self.possible_actions if action.type == ActionType.COMPLETE]
        if len(complete_actions) > 0:
            #TODO: Prioritize based on richness asdasd
            return complete_actions[0]  

        if len(my_trees) > 3:
            grow_actions = [action for action in self.possible_actions if action.type == ActionType.GROW]
            if len(grow_actions) > 0:
                return self.grow_tree(grow_actions)

        #PLANT SEED
        seed_actions = [action for action in self.possible_actions if action.type == ActionType.SEED]
        if len(seed_actions) > 0:
            return self.plant_seed(seed_actions)

        #Check if any of my trees are in cells with richness 3, AND I can afford to grow ANY.
        #Check if I can afford to grow size 2 -> 3.
        # rich_3_cells = [cell.cell_index for cell in self.board if cell.richness == 3]
        # trees_on_rich_3_cell = [tree for tree in my_trees if tree.cell_index in rich_3_cells]
        # if trees_on_rich_3_cell and any(a.type == ActionType.GROW and a.target_cell_id == trees_on_rich_3_cell[0].cell_index for a in self.possible_actions):
        #     return next(action for action in self.possible_actions if action.type == ActionType.GROW and action.target_cell_id == trees_on_rich_3_cell[0].cell_index)


        return self.possible_actions[0]


number_of_cells = int(input())
game = Game()
for i in range(number_of_cells):
    cell_index, richness, neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5 = [int(j) for j in input().split()]
    game.board.append(Cell(cell_index, richness, [neigh_0, neigh_1, neigh_2, neigh_3, neigh_4, neigh_5]))

while True:
    _day = int(input())
    game.day = _day
    game.sun_direction = _day % 6
    nutrients = int(input())
    game.nutrients = nutrients
    sun, score = [int(i) for i in input().split()]
    game.my_sun = sun
    game.my_score = score
    opp_sun, opp_score, opp_is_waiting = [int(i) for i in input().split()]
    game.opponent_sun = opp_sun
    game.opponent_score = opp_score
    game.opponent_is_waiting = opp_is_waiting
    number_of_trees = int(input())
    game.trees.clear()
    for i in range(number_of_trees):
        inputs = input().split()
        cell_index = int(inputs[0])
        size = int(inputs[1])
        is_mine = inputs[2] != "0"
        is_dormant = inputs[3] != "0"
        game.trees.append(Tree(cell_index, size, is_mine == 1, is_dormant))

    number_of_possible_actions = int(input())
    game.possible_actions.clear()
    for i in range(number_of_possible_actions):
        possible_action = input()
        print(possible_action, file=sys.stderr)
        game.possible_actions.append(Action.parse(possible_action))

    print(game.compute_next_action())