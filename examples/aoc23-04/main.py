import operator

def points(winning, gotten):
    y = countMatching(winning, gotten)
    if y > 0:
        return 2**(y-1)
    else:
        return 0

def countMatching(winning, gotten):
    y = 0
    for x in gotten:
        if x in winning:
            y += 1
    return y

def patch(cards, count, adder):
    xs = []
    for i in range(count):
        y, z = cards[i]
        xs.append([y+adder, z])
    return xs+cards[count:]

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
            "points": points,
            "countMatching": countMatching,
            "patch": patch,
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
        [ScorecardParser()],
        ["File", "Card 1: 41 48 83 86 17 | 83 86  6 31 17  9 48 53\n"],
        [["Scorecards",
            ["Card",
                1,
                ["Winning", 41, 48, 83, 86, 17],
                ["Gotten", 83, 86, 6, 31, 17, 9, 48, 53]]]]
    )
    run_gives(
        [CLI(), ScorecardParser(), PointCounter()],
        ["Args", "example1.txt"],
        [["Result", 13]]
    )
    run_gives(
        [CLI(), ScorecardParser(), PointCounter()],
        ["Args", "input1.txt"],
        [["Result", 21088]]
    )
    assert patch([[1, 1], [1, 1], [1, 1]], 2, 1) == [[2, 1], [2, 1], [1, 1]]
    run_gives(
        [CLI(), ScorecardParser(), CardCounter()],
        ["Args", "example1.txt"],
        [["Result", 30]]
    )
    run_gives(
        [CLI(), ScorecardParser(), CardCounter()],
        ["Args", "input1.txt"],
        [["Result", 6874754]]
    )
