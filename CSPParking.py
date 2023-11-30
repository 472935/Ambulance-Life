from typing import Tuple
from typing import List
import sys
from constraint import ∗

def read_file(file_name: str) -> Tuple[str, str, List[str]]:
    file_input = open(file_name, "r")

    # read rows and columns
    return_dimensions = file_input.readline()
    # read electrical connection location
    return_electrical_connection = file_input.readline()
    return_ambulances = []
    x = True
    while x:
        # read the parking lot
        return_ambulances.append(file_input.readline())
        if return_ambulances[-1] == '':
            return_ambulances.pop()
            x = False
    file_input.close()
    return return_dimensions, return_electrical_connection, return_ambulances


def arg_parse(arg_dimensions: str, arg_electric: str) -> Tuple[list, list]:
    # format the dimensions into a list of m and n
    arg_dimensions = arg_dimensions.split("x")
    # remove the \n
    arg_dimensions[1] = arg_dimensions[1][0]
    arg_dimensions = [int(i) for i in arg_dimensions]
    arg_electric = arg_electric.split(" ")
    arg_electric.pop(0)
    arg_electric = [[int(i[3]), int(i[1])] for i in arg_electric]
    return arg_dimensions, arg_electric

class CSP:
    def __init__(self, variable, domain, constraint):
        self.variables = variable
        self.domains = domain
        self.constraints = constraint

    def __getvariables__(self):
        return self.variables

class grid:
    def __init__(self, n, m, electric_values):
        # m is the number of rows
        #n is the number of columns
        self.n = n
        self.m = m
        self.grid = [[' ' for _ in range(n)] for _ in range(m)]
        for i in electric_values:
            self.grid[i[1]-1][i[0]-1] = 'E'

    def __getgrid__(self):
        return self.grid


parking_file_path = sys.argv[1]
str_dimensions, str_electric, str_ambulances = read_file(parking_file_path)
print(str_ambulances)
# format
print(str_electric)
dimensions, electric = arg_parse(str_dimensions, str_electric)
print(dimensions)
print(electric)
g = grid(dimensions[0], dimensions[1], electric)
string_grid = g.__getgrid__()
print(string_grid)
print(string_grid[0][0])
print(string_grid[4][1])


