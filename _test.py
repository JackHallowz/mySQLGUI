my_list = 'Command is SENSORS-ENABLE, 27.87, 60.52, 130.81, -1.00, 0.00, 0.00, 0.00, 1.93, 2.50, 0.00, 0.00'
indices = [ind for ind, ele in enumerate(my_list) if ele == 1]

# print the indices
print(indices)
