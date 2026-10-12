# SPDX-License-Identifier: MIT
"""Original signed-sum and nonnegative-rank experiments for a one-based BIT."""
import itertools
import json
from pathlib import Path


class Fenwick:
    def __init__(self, values):
        self.n = len(values)
        self.tree = [0] * (self.n + 1)
        for i, value in enumerate(values, 1):
            self.add(i, value)

    def add(self, index, delta):
        if not 1 <= index <= self.n:
            raise IndexError("update index must be in 1..n")
        path = []
        while index <= self.n:
            path.append(index)
            self.tree[index] += delta
            index += index & -index
        return path

    def prefix(self, index):
        if not 0 <= index <= self.n:
            raise IndexError("prefix endpoint must be in 0..n")
        result = 0
        while index:
            result += self.tree[index]
            index -= index & -index
        return result

    def range_sum(self, left, right):
        if not 1 <= left <= right <= self.n:
            raise IndexError("require 1 <= left <= right <= n")
        return self.prefix(right) - self.prefix(left - 1)

    def select_nonnegative(self, ticket):
        """Precondition: every underlying value is a nonnegative integer.

        Find the 1-based index whose half-open prefix interval contains the
        zero-based ticket. Nonnegativity is a caller obligation, not checked by
        this compact tree (it does not also store all original values).
        """
        if not 0 <= ticket < self.prefix(self.n):
            raise ValueError("ticket outside 0..total-1")
        index = cumulative = 0
        step = 1 << (self.n.bit_length() - 1)
        while step:
            nxt = index + step
            if nxt <= self.n and cumulative + self.tree[nxt] <= ticket:
                cumulative += self.tree[nxt]
                index = nxt
            step >>= 1
        return index + 1


def query_path(index):
    path = []
    while index:
        path.append(index)
        index -= index & -index
    return path


def main():
    arrays = updates = prefixes = intervals = 0
    for n in range(1, 8):
        for values in itertools.product((-1, 0, 1), repeat=n):
            arrays += 1
            bit = Fenwick(values)
            for left in range(1, n + 1):
                for right in range(left, n + 1):
                    assert bit.range_sum(left, right) == sum(values[left-1:right])
                    intervals += 1
            for index in range(1, n + 1):
                for delta in (-2, -1, 0, 1, 2):
                    bit.add(index, delta)
                    for end in range(n + 1):
                        expected = sum(values[:end]) + (delta if index <= end else 0)
                        assert bit.prefix(end) == expected
                        prefixes += 1
                    bit.add(index, -delta)
                    updates += 1

    decompositions = update_memberships = 0
    for n in range(1, 258):
        bit = Fenwick([0] * n)
        for index in range(1, n + 1):
            blocks = [list(range(j-(j & -j)+1, j+1)) for j in query_path(index)]
            flattened = sorted(x for block in blocks for x in block)
            assert flattened == list(range(1, index+1))
            assert len(query_path(index)) == index.bit_count()
            decompositions += 1
            path = bit.add(index, 0)
            oracle = [j for j in range(1, n+1) if j-(j & -j) < index <= j]
            assert path == oracle
            update_memberships += 1

    rank_arrays = tickets = 0
    for n in range(1, 8):
        for values in itertools.product((0, 1, 2), repeat=n):
            bit = Fenwick(values)
            rank_arrays += 1
            for ticket in range(sum(values)):
                expected = next(i for i in range(1, n+1) if sum(values[:i]) > ticket)
                assert bit.select_nonnegative(ticket) == expected
                tickets += 1

    empty = Fenwick([])
    assert empty.prefix(0) == 0
    for call in [lambda: empty.add(0, 1), lambda: empty.prefix(1),
                 lambda: empty.select_nonnegative(0),
                 lambda: Fenwick([1]).add(0, 1)]:
        try:
            call()
        except (IndexError, ValueError):
            pass
        else:
            raise AssertionError("boundary did not reject")

    values = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3]
    bit = Fenwick(values)
    before = bit.tree[:]
    assert bit.prefix(13) == 61
    visits = bit.add(11, 4)
    assert visits == [11, 12, 16] and bit.prefix(13) == 65
    assert bit.range_sum(9, 13) == 34
    negative = Fenwick([2, -2, 3])
    # Its prefix [2,0,3] is not monotone. Ticket 1 reaches a wrong first-crossing
    # result if the stated nonnegative precondition is ignored.
    assert negative.select_nonnegative(1) == 3
    assert next(i for i in range(1, 4) if negative.prefix(i) > 1) == 1
    out = {
        "all_passed": True, "signed_arrays": arrays, "update_cases": updates,
        "prefix_comparisons_after_update": prefixes, "initial_interval_checks": intervals,
        "interval_decomposition_checks": decompositions,
        "update_membership_checks": update_memberships,
        "nonnegative_arrays": rank_arrays, "rank_ticket_checks": tickets,
        "main_values": values, "tree_before": before, "query13_path": query_path(13),
        "query13_before": 61, "update11_by4_path": visits,
        "tree_after": bit.tree, "query13_after": 65, "range9_13_after": 34,
        "zero_weight_example": [Fenwick([2, 0, 3, 1]).select_nonnegative(k) for k in range(6)],
        "invalid_negative_rank_example": {"values": [2, -2, 3], "ticket": 1,
                                          "algorithm": 3, "first_crossing": 1},
        "scope": "exact integer model, no wall-clock or production claims",
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))



if __name__ == "__main__":
    main()
