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
        [CLI(), Parser(), ArrangementCounter("Records")],
        ["Args", "example.txt"],
        [['ArrangementCount', 1, 4, 1, 1, 4, 10]]
    )
    run_gives(
        [CLI(), Parser(), ArrangementCounter("Records"), Summer()],
        ["Args", "input.txt"],
        [['Result', 7344]]
    )
    run_gives(
        [Unfolder()],
        ["Records", ["Record", ".#", [1]]],
        [["UnfoldedRecords", ["Record", ".#?.#?.#?.#?.#", [1,1,1,1,1]]]]
    )
    run_gives(
        [CLI(), Parser(), Unfolder(), ArrangementCounter("UnfoldedRecords"), Summer()],
        ["Args", "example.txt"],
        [['Result', 525152]]
    )
    run_gives(
        [CLI(), Parser(), Unfolder(), ArrangementCounter("UnfoldedRecords"), Summer()],
        ["Args", "input.txt"],
        [['Result', 1088006519007]]
    )
