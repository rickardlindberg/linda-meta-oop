import operator

def run(actors, message):
    return run_simulation(
        actors=actors,
        extra={
            "add": operator.add,
            "sub": operator.sub,
            "mul": operator.mul,
            "sum": sum,
            "max": max,
            "min": min,
            "abs": abs,
            "dict": dict,
        },
        debug=True,
        fail=False,
        messages=[message]
    )

def run_gives(actors, message, expected):
    actual = run(actors, message)
    assert actual == expected, f"{actual} == {expected}"

if __name__ == "__main__":
    run_gives(
        [CLI(), Parser()],
        ["Args", "example.txt"],
        [['Universe', (3, 0), (7, 1), (0, 2), (6, 4), (1, 5), (9, 6), (7, 8), (0, 9), (4, 9)]]
    )
    run_gives(
        [CLI(), Parser(), Expander(1)],
        ["Args", "example.txt"],
        [['ExpandedUniverse', (4, 0), (9, 1), (0, 2), (8, 5), (1, 6), (12, 7), (9, 10), (0, 11), (5, 11)]]
    )
    run_gives(
        [CLI(), Parser(), Expander(9), Pairer(), ShortestPathSummer()],
        ["Args", "example.txt"],
        [['Result', 1030]]
    )
    run_gives(
        [CLI(), Parser(), Expander(1), Pairer(), ShortestPathSummer()],
        ["Args", "input.txt"],
        [['Result', 9521550]]
    )
    run_gives(
        [CLI(), Parser(), Expander(1000000-1), Pairer(), ShortestPathSummer()],
        ["Args", "input.txt"],
        [['Result', 298932923702]]
    )
