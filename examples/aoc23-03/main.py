import operator

def countIfOverlap(number, set1, set2):
    for x in set1:
        if x in set2:
            return number
    return 0

def getRatio(row, col, numbers):
    x = []
    for number in numbers:
        if [row, col] in number[1:]:
            x.append(number[0])
    if len(x) == 2:
        return x[0] * x[1]
    else:
        return 0

def run(actors, message):
    return run_simulation(
        actors=actors,
        extra={
            "add": operator.add,
            "sub": operator.sub,
            "mul": operator.mul,
            "sum": sum,
            "max": max,
            "append": lambda items, item: items.append(item),
            "countIfOverlap": countIfOverlap,
            "getRatio": getRatio,
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
        [GridParser()],
        ["File", "*\n*.\n"],
        [["Grid",
            [["*", 0, 0]],
            [["*", 1, 0], [".", 1, 1]]]]
    )
    run_gives(
        [EngineParser()],
        ["Grid",
            [["1", 0, 0]],
            [["*", 1, 0], [".", 1, 1]]],
        [["Engine",
            ["Numbers", [1, [0, 0]]],
            ["Symbols", ["*", 1, 0]]]]
    )
    run_gives(
        [EngineParser()],
        ["Grid",
            [["1", 0, 0], ["2", 0, 1]]],
        [["Engine",
            ["Numbers", [12, [0, 0], [0, 1]]],
            ["Symbols"]]]
    )
    run_gives(
        [ExpandAdjecant()],
        ["Engine",
            ["Numbers", [12, [0, 0], [0, 1]]],
            ["Symbols", ["*", 2, 2]]],
        [["FlatEngine",
            ["Numbers", [12, [-1, -1], [-1, 0],
                             [ 0, -1],
                             [ 1, -1], [ 1, 0],
                                                [-1, 1], [-1, 2],
                                                         [ 0, 2],
                                                [ 1, 1], [ 1, 2]]],

            ["Symbols", ["*", 2, 2]]]]
    )
    run_gives(
        [ExpandAdjecant()],
        ["Engine",
            ["Numbers", [1, [0, 0]]],
            ["Symbols", ["*", 2, 2]]],
        [["FlatEngine",
            ["Numbers", [1, [-1, -1], [-1, 0], [-1, 1],
                            [ 0, -1],          [ 0, 1],
                            [ 1, -1], [ 1, 0], [ 1, 1]]],
            ["Symbols", ["*", 2, 2]]]]
    )
    run_gives(
        [ExpandAdjecant()],
        ["Engine",
            ["Numbers", [123, [0, 0], [0, 1], [0, 2]]],
            ["Symbols", ["*", 2, 2]]],
        [["FlatEngine",
            ["Numbers", [123, [-1, -1], [-1, 0],
                              [ 0, -1],
                              [ 1, -1], [ 1, 0],
                                                 [-1, 1],

                                                 [ 1, 1],
                                                          [-1, 2], [-1, 3],
                                                                   [ 0, 3],
                                                          [ 1, 2], [ 1, 3],]],


            ["Symbols", ["*", 2, 2]]]]
    )
    run_gives(
        [CLI(), GridParser(), EngineParser(), ExpandAdjecant(), PartSummer()],
        ["Args", "example1.txt"],
        [["Result", 4361]]
    )
    run_gives(
        [CLI(), GridParser(), EngineParser(), ExpandAdjecant(), PartSummer()],
        ["Args", "input1.txt"],
        [["Result", 520019]]
    )
    run_gives(
        [CLI(), GridParser(), EngineParser(), ExpandAdjecant(), GearSummer()],
        ["Args", "example1.txt"],
        [["Result", 467835]]
    )
    run_gives(
        [CLI(), GridParser(), EngineParser(), ExpandAdjecant(), GearSummer()],
        ["Args", "input1.txt"],
        [["Result", 75519888]]
    )
    print()
    print("OK!")
