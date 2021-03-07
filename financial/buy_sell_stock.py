""""
Problem Statement
=================
Given certain stock values over a period of days (d days) and a number K, the number of transactions allowed, find the
maximum profit that be obtained with at most K transactions.

Complexity
----------
* Space Complexity O(days * transactions)
* Time Complexity: Slow Solution O (days^2 * transactions), Faster Solution O(days * transaction)
"""


def max_profit(prices, k):
    if k == 0 or prices == []:
        return 0

    days = len(prices)
    num_transactions = k + 1  # 0th transaction up to and including kth transaction is considered.

    t = [[0 for _ in range(days)] for _ in range(num_transactions)]

    for transaction in range(1, num_transactions):
        max_diff = - prices[0]
        for day in range(1, days):
            t[transaction][day] = max(t[transaction][day - 1],  # No transaction
                                      prices[day] + max_diff)  # Price on that day with max diff
            max_diff = max(max_diff,
                           t[transaction - 1][day] - prices[day])  # Update max_diff

    print_actual_solution(t, prices)

    return t[-1][-1]


def max_profit_2(prices, k):
    if k == 0 or prices == []:
        return 0

    days = len(prices)
    num_transactions = k + 1

    t = [[0 for _ in range(len(prices))] for _ in range(num_transactions)]

    for transaction in range(1, num_transactions):
        for day in range(1, days):
            # This maximum value of either
            # a) No Transaction on the day. We pick the value from day - 1
            # b) Max profit made by selling on the day plus the cost of the previous transaction, considered over m days
            t[transaction][day] = max(t[transaction][day - 1],
                                      max([(prices[day] - prices[m] + t[transaction - 1][m]) for m in range(day)]))

    print_actual_solution(t, prices)
    return t[-1][-1]


def print_actual_solution(t, prices):
    transaction = len(t) - 1
    day = len(t[0]) - 1
    stack = []

    while True:
        if transaction == 0 or day == 0:
            break

        if t[transaction][day] == t[transaction][day - 1]:  # Didn't sell
            day -= 1
        else:
            stack.append(day)  # Sold
            max_diff = t[transaction][day] - prices[day]
            for k in range(day - 1, -1, -1):
                if t[transaction - 1][k] - prices[k] == max_diff:
                    stack.append(k)  # Bought
                    transaction -= 1
                    break

    for entry in range(len(stack) - 1, -1, -2):
        print("Buy on day {day} at price {price}".format(day=stack[entry], price=prices[stack[transaction]]))
        print("Sell on day {day} at price {price}".format(day=stack[entry], price=prices[stack[transaction - 1]]))


if __name__ == '__main__':
    p = [2, 5, 7, 1, 4, 3, 1, 3]
    assert 10 == max_profit(p, 3)
    # assert 10 == max_profit_2(prices, 3)
