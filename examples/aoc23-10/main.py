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
        [Parser()],
        ["File", "S7\nLJ\n"],
        [['Map',
            ['Node', 0, 0, "START"],
            ['Node', 1, 0, (0, 0), (1, 1)],
            ['Node', 0, 1, (0, 0), (1, 1)],
            ['Node', 1, 1, (1, 0), (0, 1)]
        ]]
    )
    run_gives(
        [Flattener()],
        ['Map',
            ['Node', 0, 0, "START"],
            ['Node', 1, 0, (0, 0), (1, 1)],
            ['Node', 0, 1, (0, 0), (1, 1)],
            ['Node', 1, 1, (1, 0), (0, 1)]],
        [['Grid', {
            (0, 0): "START",
            (1, 0): [(0, 0), (1, 1)],
            (0, 1): [(0, 0), (1, 1)],
            (1, 1): [(1, 0), (0, 1)]
        }]]
    )
    run_gives(
        [CLI(), Parser(), Flattener(), StepMaximizer()],
        ["Args", "input.txt"],
        [['Result', 6786]]
    )
