import sys
import math
from enum import Enum
import random
from operator import attrgetter

def log(*args):
    for arg in args+('\n',):
        print(arg, file=sys.stderr, end=' ', flush=True)

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

    def __str__(self):
        return f'Tree, index: {self.cell_index}. Size: {self.size}'

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

    def plant_seed(self, seed_actions):
        target_cell_ids = [action.target_cell_id for action in seed_actions]
        target_cells = [cell for cell in self.board if cell.cell_index in target_cell_ids]
        richess_cell_for_seed = max(target_cells, key=attrgetter('richness'))
        #print('\n'+str(richess_cell_for_seed.cell_index), file=sys.stderr)

        return next(action for action in seed_actions if action.target_cell_id == richess_cell_for_seed.cell_index)

    def grow_tree_best_richness(self, grow_actions):     
        cell_indexes = [action.target_cell_id for action in grow_actions]
        grow_cells = [cell for cell in self.board if cell.cell_index in cell_indexes]
        richess_cell_to_grow = max(grow_cells, key=attrgetter('richness'))
        # for action in grow_actions:
        #     print(action.target_cell_id, file=sys.stderr)
        
        return next(action for action in grow_actions if action.target_cell_id == richess_cell_to_grow.cell_index)

    def complete_best_tree(self, complete_actions):
        actions_cell_indexes = [action.target_cell_id for action in complete_actions]
        cells_for_actions = [cell for cell in self.board if cell.cell_index in actions_cell_indexes]
        richess_cell = max(cells_for_actions, key=attrgetter('richness'))
        return next(action for action in complete_actions if action.target_cell_id == richess_cell.cell_index)

    def any_richness_3_seed_action(self, seed_actions):
        richness_3_cells = [cell.cell_index for cell in self.board if cell.richness == 3]
        if any(action.target_cell_id in richness_3_cells for action in seed_actions):
            return True
        else:
            return False

    def compute_next_action(self):  
        #log(self.day)

        my_trees = [tree for tree in self.trees if tree.is_mine]
        number_of_my_seeds = len([tree for tree in my_trees if tree.size == 0])
        number_of_my_size_1_trees = len([tree for tree in my_trees if tree.size == 1])

        grow_actions = [action for action in self.possible_actions if action.type == ActionType.GROW]
        seed_actions = [action for action in self.possible_actions if action.type == ActionType.SEED]
        complete_actions = [action for action in self.possible_actions if action.type == ActionType.COMPLETE]

        #TODO: Get my trees that will have spooky shadow next day, based on opponents current trees.


        #Complete tree
        #TODO: Rework this
        if len(complete_actions) > 0 and self.day > 12:
            return self.complete_best_tree(complete_actions)

        if self.any_richness_3_seed_action(seed_actions) and self.day < 14:
            return self.plant_seed(seed_actions)

        #GROW SIZE 0 TO 1 IF POSSIBLE
        seed_indexes = [tree.cell_index for tree in my_trees if tree.size == 0]
        grow_actions_for_seeds = [action for action in grow_actions if action.target_cell_id in seed_indexes]
        if len(grow_actions_for_seeds) > 0:
            return self.grow_tree_best_richness(grow_actions_for_seeds)

        #GROW SIZE 2 TO 3 IF POSSIBLE
        size_2_tree_indexes = [tree.cell_index for tree in my_trees if tree.size == 2]
        grow_actions_for_size_2_trees = [action for action in grow_actions if action.target_cell_id in size_2_tree_indexes]
        if len(grow_actions_for_size_2_trees) > 0:
            return self.grow_tree_best_richness(grow_actions_for_size_2_trees)

        #GROW SIZE 1 TO 2 IF POSSIBLE
        size_1_tree_indexes = [tree.cell_index for tree in my_trees if tree.size == 1]
        grow_actions_for_size_1_trees = [action for action in grow_actions if action.target_cell_id in size_1_tree_indexes]
        if len(grow_actions_for_size_1_trees) > 0:
            return self.grow_tree_best_richness(grow_actions_for_size_1_trees)

        # #Grow tree IF .....
        # if len([tree for tree in self.trees if tree.size == 0]) >= 2:
        #     if len(grow_actions) > 0:
        #         #print(str(len(my_trees)), file=sys.stderr)
        #         return self.grow_tree_best_richness(grow_actions)

        #PLANT SEED IF I CAN AFFORD TO GROW THEM THE SAME DAY
        cost_to_plant_seed = number_of_my_seeds
        cost_to_grow_seed = 1 + number_of_my_size_1_trees
        if self.my_sun >= cost_to_plant_seed + cost_to_grow_seed and self.day < 14:
            return self.plant_seed(seed_actions)

        #Complete first possible
        # complete_actions = [action for action in self.possible_actions if action.type == ActionType.COMPLETE]
        # if len(complete_actions) > 0:
        #     return self.complete_best_tree(complete_actions)


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
        print('Possible action: ' + possible_action, file=sys.stderr)
        game.possible_actions.append(Action.parse(possible_action))

    print(game.compute_next_action())
   