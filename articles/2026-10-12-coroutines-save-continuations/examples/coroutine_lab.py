# SPDX-License-Identifier: MIT
"""Original bounded generator/state-machine equivalence experiment, Python 3.12.

Only the six documented actions below and this particular charge program are
modelled. This is not a Python interpreter, stack copier or coroutine library.
"""
import inspect
import itertools
import json
import platform
from pathlib import Path


def charge(log):
    log.append("进入")
    try:
        energy = 10
        gain = yield energy
        energy += gain
        gain = yield energy
        energy += gain
        return energy
    finally:
        log.append("清理")


class ChargeMachine:
    """A symbolic resume label plus saved local values, not CPython layout."""

    def __init__(self, log):
        self.phase = 0  # 0=not started, 1/2=paused, 3=closed
        self.energy = None
        self.log = log

    def state(self):
        return {0: "GEN_CREATED", 1: "GEN_SUSPENDED",
                2: "GEN_SUSPENDED", 3: "GEN_CLOSED"}[self.phase]

    def finish(self):
        if self.phase in (1, 2):
            self.log.append("清理")
        self.phase = 3

    def __next__(self):
        return self.send(None)

    def send(self, value):
        if self.phase == 3:
            raise StopIteration
        if self.phase == 0:
            if value is not None:
                raise TypeError("no receiving yield yet")
            self.log.append("进入")
            self.energy = 10
            self.phase = 1
            return self.energy
        # The toy API accepts only integers or None. None causes the program's
        # own addition to fail; this differs from an initial invalid send.
        if value is None:
            self.finish()
            raise TypeError("cannot add None to energy")
        self.energy += value
        if self.phase == 1:
            self.phase = 2
            return self.energy
        self.finish()
        raise StopIteration(self.energy)

    def close(self):
        self.finish()
        return None

    def throw(self, error):
        self.finish()
        raise error


ACTIONS = ("next", "send:-2", "send:0", "send:3", "close", "throw")


def operate(obj, action):
    try:
        if action == "next":
            value = next(obj)
        elif action.startswith("send:"):
            value = obj.send(int(action.split(":")[1]))
        elif action == "close":
            value = obj.close()
        elif action == "throw":
            value = obj.throw(ValueError("cancelled by caller"))
        else:
            raise AssertionError(action)
        return ["returned", value]
    except StopIteration as error:
        return ["StopIteration", error.value]
    except (TypeError, ValueError) as error:
        return [type(error).__name__, None]


def compare(sequence):
    lg, lm = [], []
    g, m = charge(lg), ChargeMachine(lm)
    trace = [{"action": "create", "result": None,
              "state": inspect.getgeneratorstate(g), "log": list(lg)}]
    for action in sequence:
        a, b = operate(g, action), operate(m, action)
        assert a == b, (sequence, action, a, b)
        assert inspect.getgeneratorstate(g) == m.state()
        assert lg == lm
        trace.append({"action": action, "result": a,
                      "state": inspect.getgeneratorstate(g), "log": list(lg)})
    # Close both explicitly after taking the trace; no dependence on GC timing.
    g.close()
    m.close()
    assert lg == lm
    return trace


def walk(name, count, events):
    for step in range(1, count + 1):
        events.append([name, step])
        yield step


def round_robin():
    events = []
    tasks = [walk("A", 3, events), walk("B", 3, events)]
    while tasks:
        current = tasks.pop(0)
        try:
            next(current)
        except StopIteration:
            pass
        else:
            tasks.append(current)
    assert events == [[name, i] for i in (1, 2, 3) for name in ("A", "B")]
    return events


def no_preemption():
    events = []
    def long_turn():
        for i in range(1, 5):
            events.append(["A", i])
        yield "A yields only now"
    a, b = long_turn(), walk("B", 1, events)
    next(a)
    next(b)
    a.close()
    b.close()
    assert events == [["A", 1], ["A", 2], ["A", 3], ["A", 4], ["B", 1]]
    return events


def main():
    cases = steps = 0
    for size in range(6):
        for seq in itertools.product(ACTIONS, repeat=size):
            compare(seq)
            cases += 1
            steps += size
    primary = compare(["next", "send:3", "send:5"])
    assert primary[-1]["result"] == ["StopIteration", 18]
    results = {
        "runtime": platform.python_version(), "implementation": platform.python_implementation(),
        "scope": "six actions, length 0..5, charge generator versus original finite-state model",
        "sequences": cases, "operations": steps, "all_passed": True,
        "main_trace": primary,
        "invalid_initial_send": compare(["send:3", "next", "close"]),
        "next_after_pause": compare(["next", "next"]),
        "close_before_start": compare(["close", "next"]),
        "throw_after_pause": compare(["next", "throw", "next"]),
        "round_robin": round_robin(), "no_automatic_preemption": no_preemption(),
    }
    assert cases == 9331
    print(json.dumps(results, ensure_ascii=False, indent=2))



if __name__ == "__main__":
    main()
