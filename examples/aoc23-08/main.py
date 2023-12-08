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
        [Puzzle(), PrepareSolver1()],
        ["Args", "example.txt"],
        [["Result", 2]]
    )
    run_gives(
        [Puzzle(), PrepareSolver1()],
        ["Args", "example2.txt"],
        [["Result", 6]]
    )
    run_gives(
        [Puzzle(), PrepareSolver1()],
        ["Args", "input.txt"],
        [["Result", 17263]]
    )
    run_gives(
        [Puzzle(), PrepareSolver2()],
        ["Args", "example3.txt"],
        [["Result", 6]]
    )
    #run_gives(
    #    [Puzzle(), PrepareSolver2()],
    #    ["Args", "input.txt"],
    #    [["Result", 0]]
    #)
