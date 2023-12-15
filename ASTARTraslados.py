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




class Bucket:
    def __init__(self):
        self.vector = []

    def extract(self):
        if len(self.vector) == 0:
            raise Exception('Cannot extract element from empty bucket')

        return self.vector.pop()

    def add(self, element):
        self.vector.append(element)

    def isempty(self):
        return len(self.vector) == 0

    def remove(self, node):
        if self.isempty():
            raise Exception("Cannot remove a node from an empty bucket")

        for i in range(len(self.vector)):
            if self.vector[i] == node:
                self.vector.pop(i)
                return

        raise Exception("node is not in the bucket")


def heuristic1(node):
    return 0


class Bucket_Container:
    def __init__(self, initial_size):
        self.size = initial_size
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

    def update_min_value(self):
        "Checks if min_value should be updated after removing a node, if so, change the min value to the next lowest possible value."
        if self.buckets[self.min_value].isempty():
            for i in range(self.min_value + 1, self.size):
                if not self.buckets[i].isempty():
                    self.min_value = i
                    return

            self.min_value = 999999999

    def extract(self):
        if self.min_value == 999999999:  # There isnt any node in buckets
            return None

        node = self.buckets[self.min_value].extract()
        # if self.buckets[self.min_value].isempty():
        #     for i in range(self.min_value + 1, self.size):
        #         if not self.buckets[i].isempty():
        #             self.min_value = i
        #             return node
        #
        #     self.min_value = 999999999
        self.update_min_value()
        return node

    def remove(self, node):
        if node.cost >= self.size:
            raise Exception('Node to remove is out of the range of the bucket container')

        self.buckets[node.cost].remove(node)

        if node.cost == self.min_value:
            self.update_min_value()


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

    def path(self, p=None):
        if p is None:
            p = []
        p.append(self)
        if self.parent is None:
            return p

        return self.parent.path(p)

    def __repr__(self):
        # This is utilized to create the hash map where we only consider the row, col, battery, c and n
        # This is because if we want to compare two nodes their cost parent and heuristic value will be different
        return f"Node({self.c}, {self.n}, {self.battery}, {self.row}, {self.col}, {self.patients_position})"

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col and self.battery == other.battery and self.c == other.c and self.n == other.n and self.patients_position == other.patients_position

    def check_backtrack(self):
        other = self.parent.parent
        return self.row == other.row and self.col == other.col and self.c == other.c and self.n == other.n and self.patients_position == other.patients_position


    def expand(self):
        generated = [move_right(self, input_map, patients_positions), move_left(self, input_map, patients_positions),
                     move_up(self, input_map, patients_positions), move_down(self, input_map, patients_positions)]
        return [i for i in generated if i is not None]


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

    def contains_node(self, node):
        "Checks if a node is in the hash_map, if so: it returns the node when present with greater cost and removes it from the hash_map, or 2 when the node was present with lower cost (in this case it is not removed). If the node was not present it returns 0"
        node_as_string = repr(node)
        key_to_search = hash(node_as_string) % self.size
        for i in range(len(self.hash_map[key_to_search])):
            current_node = self.hash_map[key_to_search][i]
            if current_node == node:
                if current_node.cost > node.cost:  # To indicate that the node should be reopened

                    return self.hash_map[key_to_search].pop(i)
                    # When a node has to be reopened we can add it directly to open list without checking if there is another node with lower cost in open.
                    # Since it is impossible that it was in open and closed at the same time

                return 2  # The node should not be expanded because it was already expanded with lower cost.

        return 0  # The node should be opened because is not in closed list. We will need to check if it is already in the open list.

    def remove(self, node):
        node_as_string = repr(node)
        key_to_search = hash(node_as_string) % self.size
        for i in range(len(self.hash_map[key_to_search])):
            current_node = self.hash_map[key_to_search][i]
            if current_node == node:
                self.hash_map[key_to_search].pop(i)
                return
        raise Exception('Node not found')

        # operators are move the ambulance to the right, left, up, down, pick up a patient, drop a patient


def a_star(open_map: HashMap, closed_map: HashMap, buckets: Bucket_Container, start_node: Node, goal_nodes):
    buckets.insert(start_node)
    open_map.add_node(start_node)

    while True:
        best_node = buckets.extract()

        if best_node is None:  # Open list empty before finding goal
            return "No path possible"

        open_map.remove(best_node)

        #print("Battery:",best_node.battery,"Cost:",best_node.cost, "Total patients:", best_node.patients_position)
        print(best_node)

        if best_node in goal_nodes:
            return best_node.path()

        generated_nodes = best_node.expand()
        for node in generated_nodes:
            found = closed_map.contains_node(node)
            if type(found) is Node:  # We are in the case when the node was in closed list with greater cost,
                # in this case after removing the node from closed (done by contains_node method), we will add the node we generated to open_map and buckets,
                # we don't need to check if already present since one node can not be in open and closed at the same time
                open_map.add_node(node)
                buckets.insert(node)

            elif found == 0:  # Node is not in the closed list, we have to check if it is already present in open before adding.
                in_open_map = open_map.contains_node(node)

                if type(in_open_map) is int and in_open_map == 2:  # Do not add node to open list because is already in the open map with lower cost
                    continue

                else:
                    # Node is not present or is present with a greater cost

                    if type(in_open_map) is Node:  # Node was in open map with greater cost: contains node removed it,
                        # Now we have to also remove the old cost node from the buckets.
                        buckets.remove(in_open_map)

                    # Introduce the node if it was not in open / introduce the node with the updated cost after removing it from open and buckets
                    open_map.add_node(node)
                    buckets.insert(node)


def heurestic_value(node):
    if heuristic_chosen == 1:
        return node.total_patients + node.c + node.n
    elif heuristic_chosen == 2:
        pass


# operators are move the ambulance to the right, left, up, down
def cell_move(node, node_parent, map_operator, patients_dictionary):

    node_next = Node(node.c, node.n, node.battery,
                     node.row, node.col,
                     node.cost, node_parent, node.patients_position)
    if map_operator[node.row][node.col] == 'X' or node.battery == 0 or node.parent.parent is not None and node.check_backtrack():
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
                    node.cost + 1, node_parent, patients_positions_new)
    # Same as N patient but we add 1 to the C patients in the van
    elif map_operator[node.row][node.col] == 'C' and [node.row, node.col] in patients_dictionary and node.n <= 8 and node.c <= 2 and node.c + node.n <=10:
        patients_positions_new = node.patients_position.copy()
        for i in range(len(patients_positions_new)):
            if patients_positions_new[i] == [node.row, node.col]:
                patients_positions_new[i] = None
                break
        return Node(node.c + 1, node.n,
                    node.battery - 1, node.row, node.col,
                    node.cost + 1, node_parent, patients_positions_new)
    # Care centers +1 to cost -1 battery remove all c or n patients from van
    elif map_operator[node.row][node.col] == 'CC':
        return Node(0, node.n, node.battery - 1, node.row, node.col,
                    node.cost + 1, node_parent, node.patients_position)
    elif map_operator[node.row][node.col] == 'CN' and node.c == 0:
        return Node(node.c, 0, node.battery - 1, node.row, node.col,
                    node.cost + 1, node_parent, node.patients_position)
    elif map_operator[node.row][node.col] == 'P':
        return Node(node.c, node.n, 50, node.row, node.col,
                    node.cost + 1, node_parent, node.patients_position)
    elif isinstance(map_operator[node.row][node.col], int):
        return Node(node.c, node.n,
                    node.battery - map_operator[node.row][node.col], node.row, node.col,
                    node.cost + map_operator[node.row][node.col], node_parent, node.patients_position)

def move_right(node, map_operator, patients_dictionary):
    if node.col + 1 < len(input_map[0]):
        node_to_expand = Node(node.c, node.n, node.battery, node.row, node.col + 1, node.cost, node, node.patients_position)
        return cell_move(node_to_expand, node, map_operator, patients_dictionary)
    return None


def move_left(node, map_operator, patients_dictionary):
    if node.col - 1 >= 0:
        node_to_expand = Node(node.c, node.n, node.battery, node.row, node.col - 1, node.cost, node,
                                 node.patients_position)
        return cell_move(node_to_expand, node, map_operator, patients_dictionary)
    return None


def move_up(node, map_operator, patients_dictionary):
    if node.row - 1 >= 0:
        node_to_expand = Node(node.c, node.n, node.battery, node.row - 1, node.col, node.cost, node,
                                 node.patients_position)
        return cell_move(node_to_expand, node, map_operator, patients_dictionary)
    return None


def move_down(node, map_operator, patients_dictionary):
    if node.row + 1 < len(input_map):
        node_to_expand = Node(node.c, node.n, node.battery, node.row + 1, node.col, node.cost, node,
                                 node.patients_position)
        return cell_move(node_to_expand, node, map_operator, patients_dictionary)
    return None


def expand(node):
    return [move_right(node, input_map, patients_positions), move_left(node, input_map, patients_positions),
            move_up(node, input_map, patients_positions), move_down(node, input_map, patients_positions)]


# h = HashMap(5)
# h2 = HashMap(5)
# n1 = Node("Ines", 0, 0, 0, 0, 7, 0)
# h.add_node(n1)
# n2 = Node("Tortuga", 0, 0, 0, 0, 5, 0)
# h.add_node(n2)
# n3 = Node("Ines", 0, 0, 0, 0, 5, "Lolito Fdez")
# h.add_node(n3)
#
# lolito = HashMap(3)
# m = Node("Mono", 0, 0, 0, 0, 3, 0)
# lolito.add_node(m)
# m_mayor = Node("Mono", 0, 0, 0, 0, 8, 0)
# m_menor = Node("Mono", 0, 0, 0, 0, 2, 0)
# a = lolito.contains_node(m_mayor)
# b = lolito.contains_node(m_menor)
# k = Node("Araña", 0, 0, 0, 0, 3, 0)
# c = lolito.contains_node(k)

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

input_map, patients_positions, parking_square = read_file(file_to_read)
initial_patients = len(patients_positions)

initial_state = Node(0, 0, 50, parking_square[0], parking_square[1], 0, None, patients_positions)
final_state = Node(0, 0, 50, parking_square[0], parking_square[1], 0, None, [None for _ in range(initial_patients)])

open_map = HashMap(100)
closed_map = HashMap(100)
buckets = Bucket_Container(100)

path = a_star(open_map, closed_map, buckets, initial_state, [final_state])

print("Camino")

print(path)
