import operator

def zip(name, xs, ys):
    assert len(xs) == len(ys)
    result = []
    for i, x in enumerate(xs):
        result.append([name, x, ys[i]])
    return result

def margin(time, distance):
    margin = 0
    for ms in range(time):
        if (time-ms)*ms > distance:
            margin += 1
    return margin

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
            "zip": zip,
            "margin": margin,
            "range": lambda x: list(range(x)),
            "append": lambda items, item: items.append(item),
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
        [CLI(), RecordParser()],
        ["Args", "example.txt"],
        [['Records', ['Record', 7, 9], ['Record', 15, 40], ['Record', 30, 200]]]
    )
    run_gives(
        [CLI(), RecordParser(), MarginCalculator()],
        ["Args", "example.txt"],
        [['Margins', 4, 8, 9]]
    )
    run_gives(
        [CLI(), RecordParser(), MarginCalculator(), MarginProduct()],
        ["Args", "example.txt"],
        [['Result', 288]]
    )
    run_gives(
        [CLI(), RecordParser(), MarginCalculator(), MarginProduct()],
        ["Args", "input.txt"],
        [['Result', 303600]]
    )
