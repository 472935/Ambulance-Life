import re
import sys
import time
heuristic_chosen = 0


class Relevant_Locations:  # To store parking position, cn position, cc position
    def __init__(self, p_pos, cn_pos, cc_pos, mapa):
        self.parking_pos = p_pos
        self.cn_pos = cn_pos
        self.cc_pos = cc_pos
        self.mapa = mapa



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
                elif costs[i] == 'CN':
                    cn_value = [row_number, i]
                elif costs[i] == 'CC':
                    cc_value = [row_number, i]
            row_number += 1

            mapa.append(costs)
    for i in range(len(mapa)):
        if len(mapa[i]) != len(mapa[0]):
            print("Error: The map is not rectangular")
            exit(1)

    return patients_positions_map, Relevant_Locations(p_value, cn_value, cc_value, mapa)


def write_ouput(filename, map_to_search, solution_path,total_time, expanded_nodes):
    with open(filename + ".output", 'w') as f:
        if solution_path == "No path possible":
            print(solution_path, file = f)
            f.close()
            return
        for i in range(len(solution_path),0,-1):
            print("(" + str(solution_path[i-1].row) + "," + str(solution_path[i-1].col) + "):" + str(map_to_search[solution_path[i-1].row][solution_path[i-1].col]) + ":" + str(solution_path[i-1].battery), file = f)
    f.close()
    with open(filename + ".stat", 'w') as f:
        print("Total time: " + str(total_time), file = f)
        print("Total cost: " + str(solution_path[0].cost), file = f)
        print("Plan length: " + str(len(solution_path)), file = f)
        print("Expanded nodes: " + str(expanded_nodes), file = f)
    f.close()


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


def manhattan_distance(node, pos):
    return abs(node.row - pos[0]) + abs(node.col - pos[1])

def distance(position1,position2):
    return abs(position1[0] - position2[0]) + abs(position1[1] - position2[1])

def heuristic1(node, relevant_locations):
    if node.c > 0:
        return manhattan_distance(node, relevant_locations.cc_pos)

    for position in node.patients_position:
        if position is not None:
            return manhattan_distance(node, position)

    if node.n > 0:
        return manhattan_distance(node, relevant_locations.cn_pos)

    return manhattan_distance(node, relevant_locations.parking_pos)

def heuristic2(node, relevant_locations):
    if len(node.patients_position) == 0 and node.c == 0 and node.n == 0:
        return manhattan_distance(node, relevant_locations.parking_pos)
    max_dist = manhattan_distance(node,node.patients_position[0])
    for position in node.patients_position:
        new_dist = manhattan_distance(node, position)
        if new_dist > max_dist:
            max_dist = new_dist
    return max_dist

def heuristic3(node, relevant_locations):
    distance_to_c = 100
    sum = 0
    if node.c > 0:
        return manhattan_distance(node, relevant_locations.cc_pos)
    for i in range(len(node.patients_position)):
        for j in range(len(node.patients_position)):
            if i != j:
                sum += distance(node.patients_position[i], node.patients_position[j])
    return sum

def get_min_distance(pos, positions_vector):
    if len(positions_vector) == 0:
        return None, positions_vector

    min_dist = distance(pos, positions_vector[0])
    min_index = 0
    for i in range(1, len(positions_vector)):
        new_dist = distance(pos, positions_vector[i])
        if new_dist < min_dist:
            min_index = i
            min_dist = new_dist

    return min_dist, positions_vector.pop(min_index)

def heuristic4(node, relevant_locations):
    positions_vector = node.patients_position.copy()
    sum = 0

    if node.c > 0:
        return manhattan_distance(node, relevant_locations.cc_pos)

    pos = [node.row, node.col]
    for i in range(len(positions_vector)):
        minimums = get_min_distance(pos, positions_vector)
        pos = minimums[1]
        sum += minimums[0]

    if node.c > 0:
        sum + distance(pos, relevant_locations.cc_pos)

    elif node.n > 0:
        sum + distance(pos, relevant_locations.cn_pos)

    return sum + distance(pos, relevant_locations.parking_pos)




def heuristic(node, relevant_locations):
    if heuristic_chosen == 1:
        return heuristic1(node, relevant_locations)
    elif heuristic_chosen == 2:
        return heuristic2(node, relevant_locations)
    elif heuristic_chosen == 3:
        return heuristic3(node, relevant_locations)
    elif heuristic_chosen == 4:
        return heuristic4(node, relevant_locations)

class Bucket_Container:
    def __init__(self, initial_size):
        self.size = initial_size
        self.buckets = []
        for i in range(self.size):
            self.buckets.append(Bucket())

        self.min_value = 999999999  # Start with the arbitrary super large value

    def insert(self, node, r_v):
        f_val = node.cost + heuristic(node, r_v)

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

        self.update_min_value()
        return node

    def remove(self, node, r_v):
        f_val = node.cost + heuristic(node, r_v)

        if f_val >= self.size:
            raise Exception('Node to remove is out of the range of the bucket container')

        self.buckets[f_val].remove(node)

        if f_val == self.min_value:
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

    def check_backtrack(self):  # Prevents making a loop without picking or leaving a patient in the middle.
        if self.parent is None or self.parent.parent is None:
            return False

        other = self.parent.parent
        while other is not None:
            if self.c != other.c or self.n != other.n or other.battery < self.battery:  # If somewhere in the middle I pick or leave a patient there is no bad loop
                return False

            if self.row == other.row and self.col == other.col and self.c == other.c and self.n == other.n:
                return True

            other = other.parent

        return False


    def expand(self, r_v):
        generated = get_movement(self, r_v)
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



def a_star(open_map: HashMap, closed_map: HashMap, buckets: Bucket_Container, start_node: Node, goal_nodes, r_v: Relevant_Locations):

    expanded_count = 0

    buckets.insert(start_node, r_v)
    open_map.add_node(start_node)

    while True:
        best_node = buckets.extract()

        if best_node is None:  # Open list empty before finding goal
            return "No path possible", expanded_count

        open_map.remove(best_node)

        closed_map.add_node(best_node)

        if best_node in goal_nodes:
            return best_node.path(), expanded_count

        generated_nodes = best_node.expand(r_v)
        expanded_count += 1
        for node in generated_nodes:
            found = closed_map.contains_node(node)
            if type(found) is Node:  # We are in the case when the node was in closed list with greater cost,
                # in this case after removing the node from closed (done by contains_node method), we will add the node we generated to open_map and buckets,
                # we don't need to check if already present since one node can not be in open and closed at the same time
                open_map.add_node(node)
                buckets.insert(node, r_v)

            elif found == 0:  # Node is not in the closed list, we have to check if it is already present in open before adding.
                in_open_map = open_map.contains_node(node)

                if type(in_open_map) is int and in_open_map == 2:  # Do not add node to open list because is already in the open map with lower cost
                    continue

                else:
                    # Node is not present or is present with a greater cost

                    if type(in_open_map) is Node:  # Node was in open map with greater cost: contains node removed it,
                        # Now we have to also remove the old cost node from the buckets.
                        buckets.remove(in_open_map, r_v)

                    # Introduce the node if it was not in open / introduce the node with the updated cost after removing it from open and buckets
                    open_map.add_node(node)
                    buckets.insert(node, r_v)


# operators are move the ambulance to the right, left, up, down
def cell_move(node, node_parent, r_v: Relevant_Locations):
    gen_node = None

    if r_v.mapa[node.row][node.col] == 'X' or node.battery == 0 or node.check_backtrack():
        return None
    # If we find an N patient we add 1 to the N patients in the van, 1 to the cost + heuristic value and remove the patient from the patients list
    elif r_v.mapa[node.row][node.col] == 'N' and [node.row, node.col] in node.patients_position and node.c == 0 and node.c + node.n<10:
        # This can be changed to list of list with index being the column of a patient
        patients_positions_new = node.patients_position.copy()
        for i in range(len(patients_positions_new)):
            if patients_positions_new[i] == [node.row, node.col]:
                patients_positions_new.pop(i)
                break
        gen_node = Node(node.c, node.n + 1,
                    node.battery - 1, node.row, node.col,
                    node.cost + 1, node_parent, patients_positions_new)
    #Case the we pass over a N patient without picking him up
    elif r_v.mapa[node.row][node.col] == 'N':
        gen_node = Node(node.c, node.n,
                    node.battery - 1, node.row, node.col,
                    node.cost + 1, node_parent, node.patients_position)
    # Same as N patient but we add 1 to the C patients in the van
    elif r_v.mapa[node.row][node.col] == 'C' and [node.row, node.col] in node.patients_position and node.n <= 8 and node.c < 2 and node.c + node.n < 10:
        patients_positions_new = node.patients_position.copy()
        for i in range(len(patients_positions_new)):
            if patients_positions_new[i] == [node.row, node.col]:
                patients_positions_new.pop(i)
                break
        gen_node = Node(node.c + 1, node.n,
                    node.battery - 1, node.row, node.col,
                    node.cost + 1, node_parent, patients_positions_new)
    #Case that we pass over a C patient and we don't have the conditions to pick him up
    elif r_v.mapa[node.row][node.col] == 'C':
        gen_node = Node(node.c, node.n,
                    node.battery - 1, node.row, node.col,
                    node.cost + 1, node_parent, node.patients_position)
    # Care centers +1 to cost -1 battery remove all c or n patients from van
    elif r_v.mapa[node.row][node.col] == 'CC':
        gen_node = Node(0, node.n, node.battery -
                        1, node.row, node.col,
                    node.cost + 1, node_parent, node.patients_position)
    elif r_v.mapa[node.row][node.col] == 'CN' and node.c == 0:
        gen_node = Node(node.c, 0, node.battery - 1, node.row, node.col,
                    node.cost + 1, node_parent, node.patients_position)
        #Case that we pass over a CN center and we can't drop off the N patients
    elif r_v.mapa[node.row][node.col] == 'CN':
        gen_node = Node(node.c, node.n, node.battery - 1, node.row, node.col,
                    node.cost + 1, node_parent, node.patients_position)
    elif r_v.mapa[node.row][node.col] == 'P':
        gen_node = Node(node.c, node.n, 50, node.row, node.col,
                    node.cost + 1, node_parent, node.patients_position)
    elif isinstance(r_v.mapa[node.row][node.col], int):
        gen_node = Node(node.c, node.n,
                    node.battery - r_v.mapa[node.row][node.col], node.row, node.col,
                    node.cost + r_v.mapa[node.row][node.col], node_parent, node.patients_position)

    if type(gen_node) is Node and manhattan_distance(gen_node, r_v.parking_pos) <= gen_node.battery:
        return gen_node

def get_movement(node, r_v: Relevant_Locations):  # Claculate all the positions where we could move and return the
    gen_nodes = []
    for i in range(-1,2,1):
        for j in range(-1,2,1):
            if abs(i) + abs(j) == 1 and 0 <= node.col + j < len(r_v.mapa[0]) and 0 <= node.row + i < len(r_v.mapa):
                node_to_expand = Node(node.c, node.n, node.battery, node.row + i, node.col + j, node.cost, node, node.patients_position)
                processed_node = cell_move(node_to_expand, node, r_v)
                gen_nodes.append(processed_node)

    return gen_nodes



begin = time.time()
file_to_read = sys.argv[1]
heuristic_chosen = int(sys.argv[2])
number_patients_infectious = 0

patients_positions, relevant_pos = read_file(file_to_read)
initial_patients = len(patients_positions)

parking_square = relevant_pos.parking_pos

initial_state = Node(0, 0, 50, parking_square[0], parking_square[1], 0, None, patients_positions)
final_state = Node(0, 0, 50, parking_square[0], parking_square[1], 0, None, [])

open_map = HashMap(100000)
closed_map = HashMap(100000)
buckets = Bucket_Container(10000)

path, expanded_nodes = a_star(open_map, closed_map, buckets, initial_state, [final_state], relevant_pos)

end = time.time()
write_ouput(file_to_read[:-4] + "-" + str(heuristic_chosen), relevant_pos.mapa, path, end-begin, expanded_nodes)
