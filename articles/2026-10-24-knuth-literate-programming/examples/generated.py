def sum_positive(values):
    total = 0
    for value in values:
        if value > 0:
            total += value
    return total
values = [3, -2, 5, 0]
print(sum_positive(values))
