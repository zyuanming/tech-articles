# Original teaching example: Python 3 standard library, integral capacities.
names = ['s', 'a', 'b', 't']
g = [[] for _ in names]
original = []
def add(u, v, capacity):
    forward = [v, capacity, len(g[v])]
    backward = [u, 0, len(g[u])]
    g[u].append(forward)
    g[v].append(backward)
    original.append((u, v, capacity, forward))

for u, v in [(0, 1), (0, 2), (1, 2), (1, 3), (2, 3)]:
    add(u, v, 1)

def find_path(u, seen):
    if u == 3:
        return []
    seen.add(u)
    for j, (v, room, _) in enumerate(g[u]):
        if room > 0 and v not in seen:
            tail = find_path(v, seen)
            if tail is not None:
                return [(u, j)] + tail
    return None

total = 0
while True:
    path = find_path(0, set())
    if path is None:
        break
    delta = min(g[u][j][1] for u, j in path)
    route = [names[0]] + [names[g[u][j][0]] for u, j in path]
    for u, j in path:
        v, _, reverse_index = g[u][j]
        g[u][j][1] -= delta
        g[v][reverse_index][1] += delta
    total += delta
    print(' -> '.join(route), '+', delta)

print('maximum flow:', total)
for u, v, capacity, edge in original:
    print(names[u] + ' -> ' + names[v], capacity - edge[1])
assert total == 2
assert [capacity-edge[1] for _,_,capacity,edge in original] == [1,1,0,1,1]
