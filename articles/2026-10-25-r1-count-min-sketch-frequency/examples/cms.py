"""Original educational Count-Min core. CC0-1.0. Integer nonnegative updates."""
class CountMin:
    def __init__(self, width, hashes):
        hashes = tuple(hashes)
        if type(width) is not int or width <= 0 or not hashes:
            raise ValueError('positive width and nonempty hashes required')
        self.width = width
        self.hashes = hashes
        self.rows = [[0] * width for _ in self.hashes]
        self.total = 0

    def positions(self, key):
        cols = [h(key) for h in self.hashes]
        if any(type(c) is not int or not 0 <= c < self.width for c in cols):
            raise ValueError('hash result outside table')
        return cols

    def add(self, key, amount=1):
        if type(amount) is not int or amount < 0:
            raise ValueError('nonnegative integer update required')
        cols = self.positions(key)
        for row, col in zip(self.rows, cols):
            row[col] += amount
        self.total += amount

    def query(self, key):
        cols = self.positions(key)
        return min(row[col] for row, col in zip(self.rows, cols))

    def merge(self, other):
        # Same callable objects are a deliberately strict teaching check.
        if self.width != other.width or self.hashes != other.hashes:
            raise ValueError('identical hash configuration required')
        for a, b in zip(self.rows, other.rows):
            for col in range(self.width):
                a[col] += b[col]
        self.total += other.total

MAPPING = {'A': (0, 1, 2), 'B': (0, 2, 3),
           'C': (2, 1, 3), 'D': (3, 0, 2), 'E': (0, 1, 2)}
HASHES = tuple((lambda key, j=j: MAPPING[key][j]) for j in range(3))
STREAM = list('ABACABDACABA')

def demo():
    from collections import Counter
    sketch = CountMin(4, HASHES)
    states = []
    for key in STREAM:
        sketch.add(key)
        states.append([r[:] for r in sketch.rows])
    exact = Counter(STREAM)
    return dict(stream=STREAM, mapping=MAPPING, states=states,
                table=sketch.rows, total=sketch.total,
                exact={k: exact[k] for k in MAPPING},
                estimates={k: sketch.query(k) for k in MAPPING},
                candidates={k: [r[c] for r,c in zip(sketch.rows,sketch.positions(k))] for k in MAPPING})
