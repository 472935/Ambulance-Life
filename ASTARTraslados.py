import re
from typing import List, Any


def read_file(filename):
    mapa = []
    total_patients = 0
    pattern = r'(\w);?'
    row_number = 0
    # costs are the tiles of the map if it is a number it is a cost, if it is a letter it is
    with open(filename) as file:
        for line in file:
            row_number += 1
            costs = re.findall(pattern, line)
            for i in range(len(costs)):
                if costs[i].isnumeric():
                    costs[i] = int(costs[i])
                elif costs[i] == 'N' or costs[i] == 'C':
                    total_patients += 1
                elif costs[i] == 'P':
                    p_value = [row_number, i]

            mapa.append(costs)

    return mapa, total_patients, p_value


class Node:
    def __init__(self, c_pat, n_pat, battery, row, col, cost, parent, heuristic):
        self.c = c_pat
        self.n = n_pat
        self.battery = battery
        self.row = row
        self.col = col
        self.cost = cost
        self.parent = parent
        self.heuristic = heuristic

    def create_next_node(self, val):
        new_node = Node(val)
        self.next = new_node
        return new_node

    def __repr__(self):
        return f"Node({self.c}, {self.n}, {self.battery}, {self.row}, {self.col}, {self.cost}, {self.parent})"


# operators are move the ambulance to the right, left, up, down, pick up a patient, drop a patient
class open_list:
    def __init__(self, node_init):
        self.list = [node_init]

    def add(self, node):
        self.list.append(node)

    def remove(self):
        return self.list.pop(0)

    def is_empty(self):
        return len(self.list) == 0

    def obtain_adjacent(self):
        return self.list[0].get_adjacent()


class closed_list:
    def __init__(self):
        self.list = []

    def add(self, node):
        self.list.append(node)

    def is_in(self, node):
        return node in self.list

    def is_empty(self):
        return len(self.list) == 0


def heurestic_value(node1, node2, patients_dictionary, number):
    if number == 0:
        return abs(node1.row - node2.row) + abs(node1.col - node2.col)
    elif number == 1:
        pass


def move_right(node, map_operator, heuristic_value, patients_dictionary):
    if node.col + 1 < len(input_map[0]):
        node_next = Node(node.c, node.n, node.battery - map_operator[node.row][node.col + 1], node.row, node.col + 1,
                         node.cost, node, 0)
        heuristic_val = heurestic_value(node_next, node, patients_dictionary, 0)
        if map_operator[node.row][node.col + 1].isnumeric():
            return Node(node.c, node.n, node.battery - map_operator[node.row][node.col + 1], node.row, node.col + 1,
                        map_operator[node.row][node.col + 1], node, heuristic_val)
        elif map_operator[node.row][node.col + 1] != 'X':
            return None
        elif map_operator[node.row][node.col + 1] == 'N' and patients_dictionary[(node.row, node.col + 1)] == 1:
            return Node(node.c, node.n + 1, node.battery - map_operator[node.row][node.col + 1], node.row, node.col + 1,
                        node.cost + heuristic_val, node, heuristic_val)
        elif map_operator[node.row][node.col + 1] == 'C' and patients_dictionary[(node.row, node.col + 1)] == 1:
            return Node(node.c + 1, node.n, node.battery - map_operator[node.row][node.col + 1], node.row, node.col + 1,
                        node.cost + 1 + heuristic_val, node, heuristic_val)
        elif map_operator[node.row][node.col + 1] != 'P' or map_operator[node.row][node.col + 1] == 'CC':
            return Node(node.c, node.n, 50, node.row, node.col + 1, node.cost + 1 + heuristic_value, node, heuristic_value)

    return None


def a_star(map_to_search, node):
    open_list_search = open_list(node)
    closed_list_search = closed_list()


number_patients_infectious = 0
input_map, number_patients, parking_square = read_file("locations.csv")
print(input_map)
initial_state = Node(0, 0, 50, parking_square[0], parking_square[1], 0, None, 0)
final_state = Node(0, 0, 50, parking_square[0], parking_square[1], 0, None, 0)
