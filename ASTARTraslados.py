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
    def __init__(self, c_pat, n_pat, battery, row, col, cost, parent):
        self.c = c_pat
        self.n = n_pat
        self.battery = battery
        self.row = row
        self.col = col
        self.cost = cost
        self.parent = parent

    def create_next_node(self, val):
        new_node = Node(val)
        self.next = new_node
        return new_node


number_patients = 0
number_patients_infectious = 0
parking_square = 0
input_map, number_patients, parking_square = read_file("locations.csv")
print(input_map)
inital_state = Node(0, 0, 50, )
