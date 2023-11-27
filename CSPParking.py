def read_file(file_name:str)->list:
    file_input = open(file_name, "r")

    #read rows and columns 
    dimensions = file_input.readline()
    #read electrical connection location
    electrical_connection = file_input.readline()
    ambulances = []
    x=True
    while (x):
    #read the parking lot 
        ambulances.append(file_input.readline())
        if ambulances[-1] == '':
            ambulances.pop()
            x=False
    file_input.close()
    return dimensions, electrical_connection, ambulances
    

class grid:
    def __init__(self, n, m):
        self.n = n
        self.m = m
      
str_dimensions, electric, ambulances = read_file("Lab_2/files/parking1")
dimensions = str_dimensions.split("x")
print(dimensions)
g = grid(int(dimensions[0]), int(dimensions[1]))


