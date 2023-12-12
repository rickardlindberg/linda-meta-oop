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
        [CLI(), Parser(), CountArrangements()],
        ["Args", "example.txt"],
        [['PlacementCounts', 1, 4, 1, 1, 4, 10]]
    )
    run_gives(
        [CLI(), Parser(), CountArrangements(), Summer()],
        ["Args", "input.txt"],
        [['Result', 7344]]
    )
