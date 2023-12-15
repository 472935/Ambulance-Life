import re
import sys

heuristic_chosen = 0


def read_file(filename):
    mapa = []
    total_patients = 0
    patients_positions_map = []
    pattern = r'\b\w+\b'
    row_number = 0
    # costs are the tiles of the map if it is a number it is a cost, if it is a letter it is
    with open(filename) as file:
        for line in file:

            costs = re.findall(pattern, line)
            for i in range(len(costs)):
                if costs[i].isnumeric():
                    costs[i] = int(costs[i])
                elif costs[i] == 'N' or costs[i] == 'C':
                    total_patients += 1
                    patients_positions_map.append([row_number, i])
                elif costs[i] == 'P':
                    p_value = [row_number, i]
            row_number += 1

            mapa.append(costs)

    return mapa, patients_positions_map, p_value


def heuristic_value(node) -> int:
    if heuristic_chosen == 1:
        return len(node.patients_position) + node.c + node.n
    else:
        print("Heuristic not chosen")
        exit(1)


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


class Bucket_Container:
    def __init__(self):
        self.size = 10000
        self.buckets = []
        for i in range(self.size):
            self.buckets.append(Bucket())

        self.min_value = 999999999  # Start with the arbitrary super large value

    def insert(self, node):
        f_val = node.cost + heuristic_value(node)

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
    def __init__(self, c_pat, n_pat, battery, row, col, cost, parent, patients_position):
        self.c = c_pat
        self.n = n_pat
        self.battery = battery
        self.row = row
        self.col = col
        self.cost = cost
        self.parent = parent
        self.patients_position = patients_position

    def __repr__(self):
        # This is utilized to create the hash map where we only consider the row, col, battery, c and n
        # This is because if we want to compare two nodes their cost parent and heuristic value will be different
        return f"Node({self.c}, {self.n}, {self.battery}, {self.row}, {self.col}, {self.patients_position})"

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col and self.battery == other.battery and self.c == other.c and self.n == other.n
    def expand(self):
        return [move_right(self, input_map, patients_positions), move_left(self, input_map, patients_positions),
                move_up(self, input_map, patients_positions), move_down(self, input_map, patients_positions)]

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

def check_backtrack(node1, node2):
    return node1.n == node2.n and node1.c == node2.c and node1.row == node2.row and node1.col == node2.col and node1.patients_position == node2.patients_position


# operators are move the ambulance to the right, left, up, down
def cell_move(node, map_operator,patients_dictionary):
    node_next = Node(node.c, node.n, node.battery,
                     node.row, node.col,
                     node.cost, node, node.patients_position)
    heuristic_val = heuristic_value(node_next)
    if map_operator[node.row][node.col] == 'X' or node.battery == 0 and node.parent.parent != node:
        return None
    # If we find an N patient we add 1 to the N patients in the van, 1 to the cost + heuristic value and remove the patient from the patients list
    elif map_operator[node.row][node.col] == 'N' and [node.row, node.col] in patients_dictionary and node.c == 0 and node.c + node.n <=10:
        # This can be changed to list of list with index being the column of a patient
        patients_positions_new = node.patients_position.copy()
        for i in range(len(patients_positions_new)):
            if patients_positions_new[i] == [node.row, node.col]:
                patients_positions_new[i] = None
                break
        return Node(node.c, node.n + 1,
                    node.battery - 1, node.row, node.col,
                    node.cost + 1 + heuristic_val, node, patients_positions_new)
    # Same as N patient but we add 1 to the C patients in the van
    elif map_operator[node.row][node.col] == 'C' and [node.row, node.col] in patients_dictionary and node.n <= 8 and node.c <= 2 and node.c + node.n <=10:
        patients_positions_new = node.patients_position.copy()
        for i in range(len(patients_positions_new)):
            if patients_positions_new[i] == [node.row, node.col]:
                patients_positions_new[i] = None
                break
        return Node(node.c + 1, node.n,
                    node.battery - 1, node.row, node.col,
                    node.cost + 1 + heuristic_val, node, patients_positions_new)
    # Care centers +1 to cost -1 battery remove all c or n patients from van
    elif map_operator[node.row][node.col] == 'CC':
        return Node(0, node.n, node.battery - 1, node.row, node.col,
                    node.cost + 1 + heuristic_val, node, node.patients_position)
    elif map_operator[node.row][node.col] == 'CN' and node.c == 0:
        return Node(node.c, 0, node.battery - 1, node.row, node.col,
                    node.cost + 1 + heuristic_val, node, node.patients_position)
    elif map_operator[node.row][node.col] == 'P':
        return Node(node.c, node.n, 50, node.row, node.col,
                    node.cost + heuristic_val, node, node.patients_position)
    elif map_operator[node.row][node.col] == int(map_operator[node.row][node.col]):
        return Node(node.c, node.n,
                    node.battery - map_operator[node.row][node.col], node.row, node.col,
                    node.cost + heuristic_val + map_operator[node.row][node.col], node, node.patients_position)

def move_right(node, map_operator, patients_dictionary):
    if node.col + 1 < len(input_map[0]):
        node_to_expand = Node(node.c, node.n, node.battery, node.row, node.col + 1, node.cost, node, node.patients_position)
        return cell_move(node_to_expand, map_operator, patients_dictionary)
    return None


def move_left(node, map_operator, patients_dictionary):
    if node.col - 1 > 0:
        node_to_expand = Node(node.c, node.n, node.battery, node.row, node.col - 1, node.cost, node,
                                 node.patients_position)
        return cell_move(node_to_expand, map_operator, patients_dictionary)
    return None


def move_up(node, map_operator, patients_dictionary):
    if node.row - 1 > 0:
        node_to_expand = Node(node.c, node.n, node.battery, node.row - 1, node.col, node.cost, node,
                                 node.patients_position)
        return cell_move(node_to_expand, map_operator, patients_dictionary)
    return None


def move_down(node, map_operator, patients_dictionary):
    if node.row + 1 < len(input_map):
        node_to_expand = Node(node.c, node.n, node.battery, node.row + 1, node.col, node.cost, node,
                                 node.patients_position)
        return cell_move(node_to_expand, map_operator, patients_dictionary)
    return None


def expand(node):
    return [move_right(node, input_map, patients_positions), move_left(node, input_map, patients_positions),
            move_up(node, input_map, patients_positions), move_down(node, input_map, patients_positions)]


def a_star(map_to_search, node):
    # Buckets is our closed list
    open_list_search = Bucket_Container()
    # Hash set is our closed list


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
heuristic_chosen = int(sys.argv[2])
number_patients_infectious = 0

input_map, patients_positions, parking_square = read_file("locations.csv")
initial_patients = len(patients_positions)
print(input_map)
initial_state = Node(0, 0, 50, parking_square[0], parking_square[1], 0, None, patients_positions)