dict1 = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6}
double_dict1 = {k: v * 2 for (k, v) in dict1.items()}

numbers = range(10)
new_dict_comp = {n: n ** 2 for n in numbers if n % 2 == 0}

# Initialize `fahrenheit` dictionary
fahrenheit = {'t1': -30, 't2': -20, 't3': -10, 't4': 0}

# Get the corresponding `celsius` values
celsius = list(map(lambda x: (float(5) / 9) * (x - 32), fahrenheit.values()))

# Create the `celsius` dictionary
celsius_dict = dict(zip(fahrenheit.keys(), celsius))

# Get the corresponding `celsius` values and create the new dictionary
celsius2 = {k: (float(5) / 9) * (v - 32) for (k, v) in fahrenheit.items()}

# Check for items greater than 2
dict1_cond = {k: v for (k, v) in dict1.items() if v > 2}

dict1_doubleCond = {k: v for (k, v) in dict1.items() if v > 2 if v % 2 == 0}

# dict1_tripleCond = {k: v for (k, v) in dict1.items() if v > 2 if v % 2 == 0 if v % 3 == 0}

# Identify odd and even entries
dict1_tripleCond = {k: ('even' if v % 2 == 0 else 'odd') for (k, v) in dict1.items()}

nested_dict = {'first': {'a': 1}, 'second': {'b': 2}}
float_dict = {outer_k: {float(inner_v) for (inner_k, inner_v) in outer_v.items()} for (outer_k, outer_v) in
              nested_dict.items()}
print(float_dict)
