"""Original scalar reverse-mode AD teaching experiment. Python standard library only."""
from pathlib import Path
import argparse, csv, io, json, math

class Value:
    def __init__(self, value, parents=(), name=''):
        self.value = float(value)
        self.parents = tuple(parents)  # Preserve repeated edges, e.g. x * x.
        self.name = name
        self.grad = 0.0

    @staticmethod
    def lift(x):
        return x if isinstance(x, Value) else Value(x)

    def __add__(self, other):
        other = self.lift(other)
        return Value(self.value + other.value,
                     ((self, 1.0), (other, 1.0)))

    def __mul__(self, other):
        other = self.lift(other)
        return Value(self.value * other.value,
                     ((self, other.value), (other, self.value)))

    def half_square(self):
        return Value(self.value * self.value / 2,
                     ((self, self.value),))

    def named(self, name):
        self.name = name
        return self


def backward(output):
    order, seen = [], set()
    def visit(node):
        if node in seen:  # Object identity, never numerical value.
            return
        seen.add(node)
        for parent, _ in node.parents:
            visit(parent)
        order.append(node)
    visit(output)
    for node in order:
        node.grad = 0.0
    output.grad = 1.0
    trace = []
    for node in reversed(order):
        for parent, local_derivative in node.parents:
            contribution = node.grad * local_derivative
            parent.grad += contribution
            trace.append(dict(source=node.name, target=parent.name,
                              upstream=node.grad, local=local_derivative,
                              contribution=contribution, accumulated=parent.grad))
    return order, trace


def graph(x0, y0):
    x, y = Value(x0, name='x'), Value(y0, name='y')
    u = (x * y).named('u')
    v = (u + x).named('v')
    r = (v + Value(-10, name='constant -10')).named('r')
    loss = r.half_square().named('L')
    return x, y, u, v, r, loss


def f(x, y):
    return 0.5 * (x * y + x - 10) ** 2


def run():
    nodes = graph(2, 3)
    order, trace = backward(nodes[-1])
    main = {v.name: dict(value=v.value, gradient=v.grad) for v in nodes}
    assert [v.value for v in nodes] == [2, 3, 6, 8, -2, 2]
    assert [v.grad for v in nodes] == [-8, -4, -2, -2, -2, 1]
    backward(nodes[-1])
    assert nodes[0].grad == -8  # A second call resets, rather than doubles.
    grid = []
    for x0 in [-2, -0.5, 0, 1, 2, 3]:
        for y0 in [-3, -1, 0, 2, 3, 5]:
            a, b, *_, loss = graph(x0, y0)
            backward(loss)
            residual = x0 * y0 + x0 - 10
            exact = (residual * (y0 + 1), residual * x0)
            assert (a.grad, b.grad) == exact
            grid.append(dict(x=x0, y=y0, loss=loss.value,
                             dx=a.grad, dy=b.grad))
    x = Value(2, name='x')
    w = (x * x).named('w')
    z = (w + w).named('z')
    _, shared_trace = backward(z)
    assert (z.value, w.grad, x.grad) == (8, 2, 8)
    a, b = Value(2), Value(2)
    backward(a + b)
    assert a is not b and a.grad == b.grad == 1
    differences = []
    for k in range(1, 19):
        h = 10.0 ** -k
        estimate = (f(2+h, 3)-f(2, 3))/h
        central = (f(2+h, 3)-f(2-h, 3))/(2*h)
        differences.append(dict(h=h, estimate=estimate,
                               absolute_error=abs(estimate + 8),
                               central=central, central_error=abs(central+8),
                               rounded_input_unchanged=(2+h==2)))
    updates = []
    for eta in [0.01, 0.2]:
        new_x = 2-eta*(-8)
        updates.append(dict(step_size=eta, x=new_x, y=3,
                            before=f(2,3), after=f(new_x,3)))
    assert math.isclose(updates[0]['after'], 1.4112)
    assert math.isclose(updates[1]['after'], 9.68)
    return dict(main=main, reverse_trace=trace, topological_order=[v.name for v in order],
                shared_node=dict(x=2, w=4, z=8, w_gradient=w.grad,
                                 x_gradient=x.grad, trace=shared_trace),
                gradient_grid=grid, finite_difference=differences,
                optimization=updates,
                perturbation=dict(h=0.01, before=f(2,3), after=f(2.01,3),
                                  exact_first_order_change=-0.08),
                checks=dict(main=True, repeated_backward_reset=True,
                            repeated_edges=True, same_valued_distinct_nodes=True,
                            analytic_grid_cases=len(grid), optimization=True))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    result = run()
    (args.output/'results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(result['finite_difference'][0]))
    writer.writeheader(); writer.writerows(result['finite_difference'])
    (args.output/'finite-difference.csv').write_text(buffer.getvalue())
    lines = ['x=2, y=3 -> u=6, v=8, r=-2, L=2',
             'dL/dx=-8; dL/dy=-4',
             'shared w=x*x; z=w+w: dz/dx=8',
             '36 analytic grid cases PASS',
             'Repeated edges, distinct equal-valued nodes, and reset PASS',
             'Fixed y=3: eta=0.01 -> L=1.4112; eta=0.2 -> L=9.68']
    stdout = '\n'.join(lines)+'\n'
    (args.output/'stdout.txt').write_text(stdout)
    print(stdout, end='')

if __name__ == '__main__':
    main()
