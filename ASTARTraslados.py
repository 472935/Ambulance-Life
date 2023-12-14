import re
import sys

initial_patients = 0
heuristic_chosen = 0


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


class Bucket:
    def __init__(self):
        self.vector = []
        self.size = 0

    def extract(self):
        if self.size == 0:
            raise Exception('Cannot extract element from empty bucket')

        self.size -= 1
        return self.vector.pop()

    def add(self, element):
        self.vector.append(element)
        self.size += 1

    def isempty(self):
        return self.size == 0


def heuristic1(node):
    return 0


class Bucket_Container:
    def __init__(self):
        self.size = 10000
        self.buckets = []
        for i in range(self.size):
            self.buckets.append(Bucket())

        self.min_value = 999999999  # Start with the arbitrary super large value

    def insert(self, node):
        f_val = node.cost + heuristic1(node)

        if f_val < 0:
            raise Exception('Negative f_value obtained')

        if f_val < self.min_value:
            self.min_value = f_val

        if f_val >= self.size:  # The associated bucket to the node is not created
            for i in range(f_val - (self.size - 1)):  # Add the missing buckets
                self.buckets.append(Bucket())
            self.size += f_val - (self.size - 1)  # Update size

        self.buckets[f_val].add(node)

    def extract(self):
        node = self.buckets[self.min_value].extract()
        if self.buckets[self.min_value].isempty():
            for i in range(self.min_value + 1, self.size):
                if not self.buckets[i].isempty():
                    self.min_value = i
                    return node

            self.min_value = 999999999

        return node


class Node:
    def __init__(self, c_pat, n_pat, battery, row, col, cost, parent):
        self.c = c_pat
        self.n = n_pat
        self.battery = battery
        self.row = row
        self.col = col
        self.cost = cost
        self.parent = parent

    def __repr__(self):
        # This is utilized to create the hash map where we only consider the row, col, battery, c and n
        # This is because if we want to compare two nodes their cost parent and heuristic value will be different
        return f"Node({self.c}, {self.n}, {self.battery}, {self.row}, {self.col})"

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col and self.battery == other.battery and self.c == other.c and self.n == other.n


class HashMap:
    def __init__(self, size):
        self.size = size
        self.hash_map = [[] for _ in range(self.size)]

    # We use the hash key to find the position inside the list where our value is located
    # So for example take a node, we compute the hash, we do modulo the size to find our position for nodes of that hash value
    # Then we iterate through the list to find the node with the minimum cost

    def search_hash(self, node, key):
        for node_in_hash_set in self.hash_map[key]:
            if node_in_hash_set == node:
                return node_in_hash_set
        return None

    def add_node(self, node):
        node_as_string = repr(node)
        key_to_search = hash(node_as_string) % self.size

        if (found_node := self.search_hash(node, key_to_search)) is not None:
            if found_node.cost > node.cost:
                found_node.cost = node.cost
                found_node.parent = node.parent
        else:
            self.hash_map[key_to_search].append(node)


# operators are move the ambulance to the right, left, up, down, pick up a patient, drop a patient


class closed_list:
    def __init__(self):
        self.list = []

    def add(self, node):
        self.list.append(node)

    def is_in(self, node):
        return node in self.list

    def is_empty(self):
        return len(self.list) == 0


def heurestic_value(node):
    if heuristic_chosen == 1:
        return node.total_patients + node.c + node.n
    elif heuristic_chosen == 1:
        pass


def move_right(node, map_operator, heuristic_value, patients_dictionary):
    if node.col + 1 < len(input_map[0]):
        node_next = Node(node.c, node.n, node.total_patients - 1, node.battery - map_operator[node.row][node.col + 1],
                         node.row, node.col + 1,
                         node.cost, node, 0)
        heuristic_val = heurestic_value(node_next, node)
        if map_operator[node.row][node.col + 1].isnumeric():
            return Node(node.c, node.n, node.total_patients - 1, node.total_patients - 1,
                        node.battery - map_operator[node.row][node.col + 1], node.row, node.col + 1,
                        map_operator[node.row][node.col + 1], node, heuristic_val)
        elif map_operator[node.row][node.col + 1] != 'X':
            return None
        elif map_operator[node.row][node.col + 1] == 'N' and patients_dictionary[(node.row, node.col + 1)] == 1:
            return Node(node.c, node.n + 1, node.total_patients - 1,
                        node.battery - map_operator[node.row][node.col + 1], node.row, node.col + 1,
                        node.cost + heuristic_val, node, heuristic_val)
        elif map_operator[node.row][node.col + 1] == 'C' and patients_dictionary[(node.row, node.col + 1)] == 1:
            return Node(node.c + 1, node.n, node.total_patients - 1,
                        node.battery - map_operator[node.row][node.col + 1], node.row, node.col + 1,
                        node.cost + 1 + heuristic_val, node, heuristic_val)
        elif map_operator[node.row][node.col + 1] == 'CC' or map_operator[node.row][node.col + 1] == 'CN':
            return Node(node.c, node.n, node.total_patients - 1, node.battery - 1, node.row, node.col + 1,
                        node.cost + 1 + heuristic_value, node, heuristic_value)
        elif map_operator[node.row][node.col + 1] != 'P':
            return Node(node.c, node.n, node.total_patients - 1, 50, node.row, node.col + 1,
                        node.cost + 1 + heuristic_value, node, heuristic_value)
    return None


def a_star(map_to_search, node):
    # Buckets is our closed list
    open_list_search = Bucket_Container()
    # Hash set is our closed list
    closed_list_search = closed_list()


# h = HashMap(10)
# n1 = Node("Ines",0,0,0,0,7,0)
# h.add_node(n1)
# n2 = Node("Tortuga",0,0,0,0,5,0)
# h.add_node(n2)
# n3 = Node("Ines",0,0,0,0,5,"Lolito Fdez")
# h.add_node(n3)

# b = Bucket_Container()
# n = Node(0,0,0,0,0,0,13,0)
# b.insert(n)
# n.cost=3
# b.insert(n)
# a = b.extract()
# c = b.extract()

file_to_read = sys.argv[1]
heuristic_chosen = sys.argv[2]
number_patients_infectious = 0
input_map, number_patients, parking_square = read_file("locations.csv")
initial_patients = number_patients
print(input_map)
initial_state = Node(0, 0, 50, parking_square[0], parking_square[1], 0, None, 0)
final_state = Node(0, 0, 50, parking_square[0], parking_square[1], 0, None, 0)
