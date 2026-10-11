import random

def reservoir(stream, k, rng):
    if k < 0:
        raise ValueError("k must be nonnegative")
    result = []
    for i, item in enumerate(stream, 1):
        if i <= k:
            result.append(item)
        else:
            j = rng.randrange(i)
            if j < k:
                result[j] = item
    return result

rng = random.Random(2026)
counts = [0] * 10
for _ in range(100_000):
    for item in reservoir(range(10), 3, rng):
        counts[item] += 1
print(counts)
