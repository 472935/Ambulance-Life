import sys
import re
from constraint import *
import csv

m = 0
n = 0

def read_file(file_name):
    with open(file_name) as file:

        size = re.match(r'(?P<rows>\d+)x(?P<cols>\d+)', file.readline())
        if size is None:
            print("Error: The first line of the file must be in the format: <rows>x<cols>")
            exit(1)
        m = int(size.group("rows"))
        n = int(size.group("cols"))

        pattern = r'[(](\d+),(\d+)[)]'  # Patern = (\d+,\d+)
        chargers = re.findall(pattern, file.readline())

        chargers_vect = []
        ambulance_vect = []
        for charger in chargers:
            charger_coords = [int(charger[0]), int(charger[1])]
            chargers_vect.append(charger_coords)

        for line in file:
            if line == '\n':
                break
            ambulance_match = re.match(r'(?P<id>\d+)-T(?P<urgent>N|S)U-(?P<charger>C|X)', line)
            if ambulance_match is None:
                print("Error: The format of the ambulances is not correct")
                exit(1)
            ambulance = Ambulance(ambulance_match.group("id"), ambulance_match.group("urgent"),
                                  ambulance_match.group("charger"))
            ambulance_vect.append(ambulance)

    return [m, n], chargers_vect, ambulance_vect


def write_file(file_name: str, solution_to_write: list, solution_num: int):
    row_to_write = []
    for _ in range(m):
        row_to_write.append(['-' for _ in range(n)])

    for i in solution_to_write:
        row_to_write[int(i[1]) // n][int(i[1]) % n] = i[0]

    with open(file_name, "w") as file_output:
        # creating a csv writer object
        csvwriter = csv.writer(file_output)
        csvwriter.writerow([str(solution_num)])

        for index_row in range(m):
            csvwriter.writerow(row_to_write[index_row])
    file_output.close()

def map_id(solution_with_id,ambulances):
    final_states = []
    for i in solution_with_id:
        for j in ambulances:
            if i[0] == j.id:
                final_states.append((str(j.id) + "-T" + str(j.urgent) + "U" + "-" + str(j.charger), i[1]))
    return final_states


class CSP:
    def __init__(self, variable, domain, constraint):
        self.variables = variable
        self.domains = domain
        self.constraints = constraint

    def __getvariables__(self):
        return self.variables


class Ambulance:
    def __init__(self, id, urgent, charger):
        self.id = id
        self.urgent = urgent
        self.charger = charger


# Functions for cosntraints
# If a TSU ambulance is placed in a row there can’t be any ambulance in front of it except if it is a TSU ambulance
def tsu_row(ambulance_tsu_row, ambulance_tnu_row):
    # if ambulance_tsu_row != ambulance_tnu_row:
    # Check first if they are close enough, and they are in the same row
    if ambulance_tnu_row > ambulance_tsu_row and ambulance_tnu_row // n == ambulance_tsu_row // n:
        return False
    return True


# An ambulance must have a free spot either to the left or right
def not_adjacent(ambulance_adjacent_i, ambulance_adjacent_j, ambulance_adjacent_k):  # No funciona par
    # First case if ambulance is in the first row or last then condition is satisfied
    # If between those two rows then check if both ambulances j and k are above and below ambulance i
    if n <= ambulance_adjacent_i < n * (m - 1) and (ambulance_adjacent_i - n) == ambulance_adjacent_j and (
            ambulance_adjacent_i + n) == ambulance_adjacent_k:
        return False
    elif ambulance_adjacent_i < n and (
            (ambulance_adjacent_i + n) == ambulance_adjacent_k or (ambulance_adjacent_i + n) == ambulance_adjacent_j):
        return False
    elif ambulance_adjacent_i >= n * (m - 1) and (
            (ambulance_adjacent_i - n) == ambulance_adjacent_k or (ambulance_adjacent_i - n) == ambulance_adjacent_j):
        return False
    return True


parking_file_path = sys.argv[1]
dimensions, electric, ambulances = read_file(parking_file_path)

# format

# dimensions, electric, ambulances = arg_parse(str_dimensions, str_electric, str_ambulances)

m = dimensions[0]
n = dimensions[1]

# For each m there is n numbers

domain_electric = [(electrical_mn[0] - 1) * n + (electrical_mn[1] - 1) for electrical_mn in electric]

problem = Problem()
# We now consider the domain values of the grid to be a singular array of integers
# (1,1) -> 1 and (1,2)-> 2 so on (2,1) -> 6 in 5*6 matrix
for ambulance in ambulances:
    # If not cooler domain is the entire grid
    if ambulance.charger == "X":
        problem.addVariable(ambulance.id, range(n * m))

    # If cooler domain is in the electrical grid
    if ambulance.charger == "C":
        problem.addVariable(ambulance.id, domain_electric)
# Now we will add the constraints
problem.addConstraint(AllDifferentConstraint(), [ambulance.id for ambulance in ambulances])
# Iterate without transposition in the variables
for ambulance_i in ambulances:  # Que pasa cuando dos ambulancias son la misma
    for ambulance_j in ambulances:
        for ambulance_k in ambulances:
            if ambulance_i.id != ambulance_j.id and ambulance_i.id != ambulance_k.id and ambulance_j.id != ambulance_k.id:
                problem.addConstraint(not_adjacent, (ambulance_i.id, ambulance_j.id, ambulance_k.id))
# Iterate without transposition in the variables with the tsu being with C in the 6th position
for ambulance1 in ambulances:
    for ambulance2 in ambulances:
        if ambulance2.urgent == "S" and ambulance1.urgent == "N":
            problem.addConstraint(tsu_row, (ambulance2.id, ambulance1.id))
        if ambulance1.charger == ambulance2.charger and int(ambulance1.id) < int(ambulance2.id) and ambulance1.urgent == ambulance2.urgent:
            # With previous else, forces ambulances of same urgency and chrger type to be placed eith increasing id order to reduce the number of combinations of solutions
            problem.addConstraint(lambda a1, a2: a1 < a2, (ambulance1.id, ambulance2.id))


solutions = problem.getSolutions()

if len(solutions) == 0:
    print("No solution found")
    exit(1)
solution_write = map_id(list(solutions[0].items()), ambulances)
write_file(parking_file_path + ".csv", solution_write, 5)

