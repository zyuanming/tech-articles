"""Original closure experiments; Python standard library; no engine/UI involved."""
import json
import platform
import random


def make_score(bonus):
    def score(points):
        return points + bonus
    return score


def call_with_other_bonus(fn, points):
    bonus = 1000
    return fn(points)


def make_counter(start=0):
    count = start
    def add():
        nonlocal count
        count += 1
        return count
    def read():
        return count
    return add, read


def late_buttons():
    buttons = []
    for label in ['A', 'B', 'C']:
        def click():
            return label
        buttons.append(click)
    return buttons


def default_buttons():
    buttons = []
    for label in ['A', 'B', 'C']:
        def click(saved=label):
            return saved
        buttons.append(click)
    return buttons


def button_factory(label):
    def click():
        return label
    return click


def cell_for(fn, name):
    return dict(zip(fn.__code__.co_freevars, fn.__closure__ or ()))[name]


# A teaching representation of code+environment; not CPython's memory layout.
def explicit_score_code(env, points):
    return points + env['bonus']


def make_explicit_score(bonus):
    return explicit_score_code, {'bonus': bonus}


def call_pair(pair, points):
    code, env = pair
    return code(env, points)


def main():
    easy, hard = make_score(10), make_score(100)
    assert [easy(7), hard(7), call_with_other_bonus(easy, 7)] == [17, 107, 17]
    introspection = {
        'free_names': list(easy.__code__.co_freevars),
        'same_code_object_this_run': easy.__code__ is hard.__code__,
        'same_bonus_cell': cell_for(easy, 'bonus') is cell_for(hard, 'bonus'),
        'cell_values': [cell_for(easy,'bonus').cell_contents, cell_for(hard,'bonus').cell_contents],
    }
    add_a, read_a = make_counter(0)
    add_b, read_b = make_counter(100)
    trace = []
    for name, fn in [('A+', add_a), ('A+', add_a), ('B+', add_b), ('A?',read_a), ('B?',read_b)]:
        trace.append([name, fn()])
    assert trace == [['A+',1], ['A+',2], ['B+',101], ['A?',2], ['B?',101]]
    shared = cell_for(add_a,'count') is cell_for(read_a,'count')
    separated = cell_for(add_a,'count') is not cell_for(add_b,'count')
    assert shared and separated
    alias = add_a
    assert alias() == 3 and read_a() == 3  # alias is not a new factory invocation
    late = late_buttons(); defaults = default_buttons(); factories = [button_factory(v) for v in ['A','B','C']]
    outputs = {'late':[f() for f in late], 'default':[f() for f in defaults], 'factory':[f() for f in factories]}
    assert outputs == {'late':['C','C','C'],'default':['A','B','C'],'factory':['A','B','C']}
    assert cell_for(late[0],'label') is cell_for(late[2],'label')
    assert defaults[0].__closure__ is None and defaults[0].__defaults__ == ('A',)
    bag = ['coin']
    def show(saved=bag):
        return list(saved)
    bag.append('key')
    assert show() == ['coin','key']
    mutable_default = show()
    bag = ['new bag']
    assert show() == ['coin','key']  # rebinding is different from mutating old object
    broken_error = None
    def bad_factory():
        count = 0
        def add():
            count += 1
            return count
        return add
    try:
        bad_factory()()
    except UnboundLocalError as e:
        broken_error = type(e).__name__
    assert broken_error == 'UnboundLocalError'
    pair_cases = 0
    for bonus in range(-20,21):
        for points in range(-30,31):
            assert make_score(bonus)(points) == call_pair(make_explicit_score(bonus),points) == bonus+points
            pair_cases += 1
    # Random interleavings are checked against a plain independent integer list.
    rng = random.Random(1964)
    counters = [make_counter(i*100) for i in range(5)]
    expected = [i*100 for i in range(5)]
    for _ in range(10000):
        i = rng.randrange(5)
        if rng.randrange(3):
            expected[i] += 1
            assert counters[i][0]() == expected[i]
        else:
            assert counters[i][1]() == expected[i]
    assert [read() for add,read in counters] == expected
    print(json.dumps({'python':platform.python_version(),'implementation':platform.python_implementation(),
        'scorers':[easy(7),hard(7)],'caller_bonus_does_not_replace_definition':call_with_other_bonus(easy,7),
        'introspection':introspection,'counter_trace':trace,'sibling_shared_cell':shared,
        'separate_factory_cells':separated,'alias_next':3,'loop_outputs':outputs,
        'mutable_default_after_append':mutable_default,'without_nonlocal':broken_error,
        'code_environment_pair_cases':pair_cases,'random_interleavings':10000,'seed':1964,'final_counts':expected},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
