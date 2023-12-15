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


# operators are move the ambulance to the right, left, up, down
def move_right(node, map_operator, patients_dictionary):
    if node.col + 1 < len(input_map[0]):
        node_next = Node(node.c, node.n, node.battery,
                         node.row, node.col + 1,
                         node.cost, node, node.patients_position)
        heuristic_val = heuristic_value(node_next)

        if map_operator[node.row][node.col + 1] == 'X':
            return None
        # If we find a N patient we add 1 to the N patients in the van, 1 to the cost + heuristic value and remove the patient from the patients list
        elif map_operator[node.row][node.col + 1] == 'N' and [node.row, node.col + 1] in patients_dictionary:
            # This can be changed to list of list with index being the column of a patient
            patients_positions_new = node.patients_position.copy()
            for i in range(len(patients_positions_new)):
                if patients_positions_new[i] == [node.row, node.col + 1]:
                    patients_positions_new[i] = None
                    break
            return Node(node.c, node.n + 1,
                        node.battery - 1, node.row, node.col + 1,
                        node.cost + 1 + heuristic_val, node, patients_positions_new)
        # Same as N patient but we add 1 to the C patients in the van
        elif map_operator[node.row][node.col + 1] == 'C' and [node.row, node.col + 1] in patients_dictionary:
            patients_positions_new = node.patients_position.copy()
            for i in range(len(patients_positions_new)):
                if patients_positions_new[i] == [node.row, node.col + 1]:
                    patients_positions_new[i] = None
                    break
            return Node(node.c + 1, node.n,
                        node.battery - 1, node.row, node.col + 1,
                        node.cost + 1 + heuristic_val, node, patients_positions_new)
        # Care centers +1 to cost -1 battery remove all c or n patients from van
        elif map_operator[node.row][node.col + 1] == 'CC':
            return Node(0, node.n, node.battery - 1, node.row, node.col + 1,
                        node.cost + 1 + heuristic_val, node, node.patients_position)
        elif map_operator[node.row][node.col + 1] == 'CN':
            return Node(node.c, 0, node.battery - 1, node.row, node.col + 1,
                        node.cost + 1 + heuristic_val, node, node.patients_position)
        elif map_operator[node.row][node.col + 1] == 'P':
            return Node(node.c, node.n, 50, node.row, node.col + 1,
                        node.cost + heuristic_val, node, node.patients_position)
        elif map_operator[node.row][node.col + 1] == int(map_operator[node.row][node.col + 1]):
            return Node(node.c, node.n,
                        node.battery - map_operator[node.row][node.col + 1], node.row, node.col + 1,
                        node.cost + heuristic_val + map_operator[node.row][node.col + 1], node, node.patients_position)
    return None


def move_left(node, map_operator, patients_dictionary):
    if node.col - 1 > 0:
        node_next = Node(node.c, node.n, node.battery,
                         node.row, node.col - 1,
                         node.cost, node, node.patients_position)
        heuristic_val = heuristic_value(node_next)

        if map_operator[node.row][node.col - 1] == 'X':
            return None
        # If we find a N patient we add 1 to the N patients in the van, 1 to the cost + heuristic value and remove the patient from the patients list
        elif map_operator[node.row][node.col - 1] == 'N' and [node.row, node.col - 1] in patients_dictionary:
            # This can be changed to list of list with index being the column of a patient
            patients_positions_new = node.patients_position.copy()
            for i in range(len(patients_positions_new)):
                if patients_positions_new[i] == [node.row, node.col - 1]:
                    patients_positions_new[i] = None
                    break
            return Node(node.c, node.n + 1,
                        node.battery - 1, node.row, node.col - 1,
                        node.cost + 1 + heuristic_val, node, patients_positions_new)
        # Same as N patient but we add 1 to the C patients in the van
        elif map_operator[node.row][node.col - 1] == 'C' and [node.row, node.col - 1] in patients_dictionary:
            patients_positions_new = node.patients_position.copy()
            for i in range(len(patients_positions_new)):
                if patients_positions_new[i] == [node.row, node.col - 1]:
                    patients_positions_new[i] = None
                    break
            return Node(node.c + 1, node.n,
                        node.battery - 1, node.row, node.col - 1,
                        node.cost + 1 + heuristic_val, node, patients_positions_new)
        # Care centers +1 to cost -1 battery remove all c or n patients from van
        elif map_operator[node.row][node.col - 1] == 'CC':
            return Node(0, node.n, node.battery - 1, node.row, node.col - 1,
                        node.cost + 1 + heuristic_val, node, node.patients_position)
        elif map_operator[node.row][node.col - 1] == 'CN':
            return Node(node.c, 0, node.battery - 1, node.row, node.col - 1,
                        node.cost + 1 + heuristic_val, node, node.patients_position)
        elif map_operator[node.row][node.col - 1] == 'P':
            return Node(node.c, node.n, 50, node.row, node.col - 1,
                        node.cost + heuristic_val, node, node.patients_position)
        elif map_operator[node.row][node.col - 1] == int(map_operator[node.row][node.col - 1]):
            return Node(node.c, node.n,
                        node.battery - map_operator[node.row][node.col - 1], node.row, node.col - 1,
                        node.cost + heuristic_val + map_operator[node.row][node.col - 1], node, node.patients_position)
    return None


def move_up(node, map_operator, patients_dictionary):
    if node.row - 1 > 0:
        node_next = Node(node.c, node.n, node.battery,
                         node.row - 1, node.col,
                         node.cost, node, node.patients_position)
        heuristic_val = heuristic_value(node_next)

        if map_operator[node.row - 1][node.col] == 'X':
            return None
        # If we find a N patient we add 1 to the N patients in the van, 1 to the cost + heuristic value and remove the patient from the patients list
        elif map_operator[node.row - 1][node.col] == 'N' and [node.row - 1, node.col] in patients_dictionary:
            # This can be changed to list of list with index being the column of a patient
            patients_positions_new = node.patients_position.copy()
            for i in range(len(patients_positions_new)):
                if patients_positions_new[i] == [node.row - 1, node.col]:
                    patients_positions_new[i] = None
                    break
            return Node(node.c, node.n + 1,
                        node.battery - 1, node.row - 1, node.col,
                        node.cost + 1 + heuristic_val, node, patients_positions_new)
        # Same as N patient but we add 1 to the C patients in the van
        elif map_operator[node.row - 1][node.col] == 'C' and [node.row - 1, node.col] in patients_dictionary:
            patients_positions_new = node.patients_position.copy()
            for i in range(len(patients_positions_new)):
                if patients_positions_new[i] == [node.row - 1, node.col]:
                    patients_positions_new[i] = None
                    break
            return Node(node.c + 1, node.n,
                        node.battery - 1, node.row - 1, node.col,
                        node.cost + 1 + heuristic_val, node, patients_positions_new)
        # Care centers +1 to cost -1 battery remove all c or n patients from van
        elif map_operator[node.row - 1][node.col] == 'CC':
            return Node(0, node.n, node.battery - 1, node.row - 1, node.col,
                        node.cost + 1 + heuristic_val, node, node.patients_position)
        elif map_operator[node.row - 1][node.col] == 'CN':
            return Node(node.c, 0, node.battery - 1, node.row - 1, node.col,
                        node.cost + 1 + heuristic_val, node, node.patients_position)
        elif map_operator[node.row - 1][node.col] == 'P':
            return Node(node.c, node.n, 50, node.row - 1, node.col,
                        node.cost + heuristic_val, node, node.patients_position)
        elif map_operator[node.row - 1][node.col] == int(map_operator[node.row - 1][node.col]):
            return Node(node.c, node.n,
                        node.battery - map_operator[node.row - 1][node.col], node.row - 1, node.col,
                        node.cost + heuristic_val + map_operator[node.row - 1][node.col], node, node.patients_position)
    return None


def move_down(node, map_operator, patients_dictionary):
    if node.row + 1 < len(input_map):
        node_next = Node(node.c, node.n, node.battery,
                         node.row + 1, node.col,
                         node.cost, node, node.patients_position)
        heuristic_val = heuristic_value(node_next)

        if map_operator[node.row + 1][node.col] == 'X':
            return None
        # If we find a N patient we add 1 to the N patients in the van, 1 to the cost + heuristic value and remove the patient from the patients list
        elif map_operator[node.row + 1][node.col] == 'N' and [node.row + 1, node.col] in patients_dictionary:
            # This can be changed to list of list with index being the column of a patient
            patients_positions_new = node.patients_position.copy()
            for i in range(len(patients_positions_new)):
                if patients_positions_new[i] == [node.row + 1, node.col]:
                    patients_positions_new[i] = None
                    break
            return Node(node.c, node.n + 1,
                        node.battery - 1, node.row + 1, node.col,
                        node.cost + 1 + heuristic_val, node, patients_positions_new)
        # Same as N patient but we add 1 to the C patients in the van
        elif map_operator[node.row + 1][node.col] == 'C' and [node.row + 1, node.col] in patients_dictionary:
            patients_positions_new = node.patients_position.copy()
            for i in range(len(patients_positions_new)):
                if patients_positions_new[i] == [node.row + 1, node.col]:
                    patients_positions_new[i] = None
                    break
            return Node(node.c + 1, node.n,
                        node.battery - 1, node.row + 1, node.col,
                        node.cost + 1 + heuristic_val, node, patients_positions_new)
        # Care centers +1 to cost -1 battery remove all c or n patients from van
        elif map_operator[node.row + 1][node.col] == 'CC':
            return Node(0, node.n, node.battery - 1, node.row + 1, node.col,
                        node.cost + 1 + heuristic_val, node, node.patients_position)
        elif map_operator[node.row + 1][node.col] == 'CN':
            return Node(node.c, 0, node.battery - 1, node.row + 1, node.col,
                        node.cost + 1 + heuristic_val, node, node.patients_position)
        elif map_operator[node.row + 1][node.col] == 'P':
            return Node(node.c, node.n, 50, node.row + 1, node.col,
                        node.cost + heuristic_val, node, node.patients_position)
        elif map_operator[node.row + 1][node.col] == int(map_operator[node.row + 1][node.col]):
            return Node(node.c, node.n,
                        node.battery - map_operator[node.row + 1][node.col], node.row + 1, node.col,
                        node.cost + heuristic_val + map_operator[node.row + 1][node.col], node, node.patients_position)
    return None


def expand_node_operators(node):
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
final_state = Node(0, 0, 50, parking_square[0], parking_square[1], 0, None, patients_positions)
node_right = move_right(initial_state, input_map, patients_positions)
node_left_of_patient = Node(0, 0, 50, 0, 7, 0, None, patients_positions)
node_patient = move_right(node_left_of_patient, input_map, patients_positions)
node_patient.col = 7
node_patient.row = 3
node_care_center_with_patient = move_right(node_patient, input_map, patients_positions)
node_next_to_CC_with_C = Node(1, 0, 50, 3, 3, 0, None, patients_positions)
node_care_center_with_patient_cc = move_right(node_next_to_CC_with_C, input_map, patients_positions)
print(repr(node_patient))
print(repr(node_care_center_with_patient))
print(repr(node_care_center_with_patient_cc))
print("-----------PATIENT TESTS ---------")

# patient at 2, 6
node_left_of_patient = Node(0, 0, 50, 2, 5, 0, None, patients_positions)
node_patient_from_left = move_right(node_left_of_patient, input_map, patients_positions)
node_right_of_patient = Node(0, 0, 50, 2, 7, 0, None, patients_positions)
node_patient_from_right = move_left(node_right_of_patient, input_map, patients_positions)
node_up_of_patient = Node(0, 0, 50, 1, 6, 0, None, patients_positions)
node_patient_from_up = move_down(node_up_of_patient, input_map, patients_positions)
node_down_of_patient = Node(0, 0, 50, 3, 6, 0, None, patients_positions)
node_patient_from_down = move_up(node_down_of_patient, input_map, patients_positions)
print(repr(node_patient_from_up))
print(repr(node_patient_from_down))
print(repr(node_patient_from_left))
print(repr(node_patient_from_right))
print( node_patient_from_left == node_patient_from_right == node_patient_from_up == node_patient_from_down)
print("-----------COST TESTS ---------")
# two square at 2, 8
node_left_of_patient = Node(0, 0, 50, 2, 7, 0, None, patients_positions)
node_patient_from_left = move_right(node_left_of_patient, input_map, patients_positions)
node_right_of_patient = Node(0, 0, 50, 2, 9, 0, None, patients_positions)
node_patient_from_right = move_left(node_right_of_patient, input_map, patients_positions)
node_up_of_patient = Node(0, 0, 50, 1, 8, 0, None, patients_positions)
node_patient_from_up = move_down(node_up_of_patient, input_map, patients_positions)
node_down_of_patient = Node(0, 0, 50, 3, 8, 0, None, patients_positions)
node_patient_from_down = move_up(node_down_of_patient, input_map, patients_positions)
print(repr(node_patient_from_up))
print(repr(node_patient_from_down))
print(repr(node_patient_from_left))
print(repr(node_patient_from_right))
print( node_patient_from_left == node_patient_from_right == node_patient_from_up == node_patient_from_down)

print("-----------CC TESTS ---------")
# CC at 3, 4
node_left_of_cc_with_c = Node(1, 0, 50, 3, 3, 0, None, patients_positions)
node_right_of_cc_with_c = Node(1, 0, 50, 3, 5, 0, None, patients_positions)
node_up_of_cc_with_c = Node(1,0,50,2,4,0,None,patients_positions)
node_down_of_cc_with_c = Node(1,0,50,4,4,0,None,patients_positions)
node_cc_with_c_from_left = move_right(node_left_of_cc_with_c, input_map, patients_positions)
node_cc_with_c_from_right = move_left(node_right_of_cc_with_c, input_map, patients_positions)
node_cc_with_c_from_up = move_down(node_up_of_cc_with_c, input_map, patients_positions)
node_cc_with_c_from_down = move_up(node_down_of_cc_with_c, input_map, patients_positions)
print(repr(node_cc_with_c_from_left))
print(repr(node_cc_with_c_from_right))
print(repr(node_cc_with_c_from_up))
print(repr(node_cc_with_c_from_down))
print(node_cc_with_c_from_left == node_cc_with_c_from_right == node_cc_with_c_from_up == node_cc_with_c_from_down)

print("-----------CN TESTS ---------")
# CN at 3, 8
node_left_of_cn_with_n = Node(0, 7, 50, 3, 7, 0, None, patients_positions)
node_right_of_cn_with_n = Node(0, 7, 50, 3, 9, 0, None, patients_positions)
node_up_of_cn_with_n = Node(0,7,50,2,8,0,None,patients_positions)
node_down_of_cn_with_n = Node(0,7,50,4,8,0,None,patients_positions)
node_cn_with_n_from_left = move_right(node_left_of_cn_with_n, input_map, patients_positions)
node_cn_with_n_from_right = move_left(node_right_of_cn_with_n, input_map, patients_positions)
node_cn_with_n_from_up = move_down(node_up_of_cn_with_n, input_map, patients_positions)
node_cn_with_n_from_down = move_up(node_down_of_cn_with_n, input_map, patients_positions)
print(repr(node_cn_with_n_from_left))
print(repr(node_cn_with_n_from_right))
print(repr(node_cn_with_n_from_up))
print(repr(node_cn_with_n_from_down))
print(node_cn_with_n_from_left == node_cn_with_n_from_right == node_cn_with_n_from_up == node_cn_with_n_from_down)
print("-----------PARKING TESTS ---------")
#parking at 7, 3
node_with_c_and_n_left_of_parking = Node(1,1,50,7,2,0,None,patients_positions)
node_with_c_and_n_right_of_parking = Node(1,1,50,7,4,0,None,patients_positions)
node_with_c_and_n_up_of_parking = Node(1,1,50,6,3,0,None,patients_positions)
node_with_c_and_n_down_of_parking = Node(1,1,50,8,3,0,None,patients_positions)
node_parking_from_left = move_right(node_with_c_and_n_left_of_parking, input_map, patients_positions)
node_parking_from_right = move_left(node_with_c_and_n_right_of_parking, input_map, patients_positions)
node_parking_from_up = move_down(node_with_c_and_n_up_of_parking, input_map, patients_positions)
node_parking_from_down = move_up(node_with_c_and_n_down_of_parking, input_map, patients_positions)
print(repr(node_parking_from_left))
print(repr(node_parking_from_right))
print(repr(node_parking_from_up))
print(repr(node_parking_from_down))


print(node_parking_from_down == node_parking_from_up == node_parking_from_right == node_parking_from_left)
print(expand_node_operators(node_patient_from_down))