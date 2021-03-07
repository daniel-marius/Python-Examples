# letters = [letter for letter in 'list']

letters = list(map(lambda x: x, 'list'))

number_list = [x for x in range(20) if x % 2 == 0]

obj = ["Even" if i % 2 == 0 else "Odd" for i in range(10)]

matrix = [[1, 2], [3, 4], [5, 6], [7, 8]]
transpose = [[row[i] for row in matrix] for i in range(2)]


def get_price(price):
    return price if price > 0 else 0


original_prices = [1.25, -9.45, 10.22, 3.78, -5.92, 1.16]
prices = [get_price(i) for i in original_prices]

m = [[i for i in range(5)] for _ in range(6)]

list1 = [3, 4, 5]
multiplied = [item * 3 for item in list1]

list_of_list = [[1, 2, 3], [4, 5, 6], [7, 8]]

# Flatten `list_of_list`
list2 = [y for x in list_of_list for y in x]
