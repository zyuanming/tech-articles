# Original semantic and address-count teaching experiment; not an ECS benchmark.
pos = {10: (0., 0.), 20: (2., 1.), 30: (5., 0.), 40: (3., 3.)}
vel = {10: (2., 0.), 20: (0., 2.), 40: (-1., 1.)}
health = {20: 100, 30: 50}
for entity in sorted(pos.keys() & vel.keys()):
    x, y = pos[entity]
    vx, vy = vel[entity]
    pos[entity] = (x + vx*.5, y + vy*.5)
print('positions:', pos)
assert pos == {10:(1.,0.),20:(2.,2.),30:(5.,0.),40:(2.5,3.5)}

# Hypothetical aligned addresses. Count unique 64-byte lines touched by reads.
aos = {address//64 for i in range(8) for address in range(i*64, i*64+16)}
soa = {address//64 for address in range(128)}
print('AoS lines:', len(aos), 'bytes:', len(aos)*64)
print('SoA lines:', len(soa), 'bytes:', len(soa)*64)
assert (len(aos), len(soa)) == (8, 2)
