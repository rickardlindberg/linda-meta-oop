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
        [CLI(), Parser(), Differ(), Summer()],
        ["Args", "example.txt"],
        [["Result", 114]]
    )
    run_gives(
        [CLI(), Parser(), Differ(), Summer()],
        ["Args", "input.txt"],
        [["Result", 1916822650]]
    )
    run_gives(
        [CLI(), Parser(), Backwards(), Summer()],
        ["Args", "example.txt"],
        [["Result", 2]]
    )
    run_gives(
        [CLI(), Parser(), Backwards(), Summer()],
        ["Args", "input.txt"],
        [["Result", 966]]
    )
