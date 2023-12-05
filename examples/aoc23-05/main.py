import operator

def doMap(mapSpec, number):
    for target, source, size in mapSpec:
        if number >= source and number <= (source+size):
            return number - source + target
    return number

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
            "range": lambda x: list(range(x)),
            "append": lambda items, item: items.append(item),
            "doMap": doMap,
            "Mapper": Mapper,
            "LocationMinimizer": LocationMinimizer,
            "PartCollector": PartCollector,
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
        [CLI(), AlmanacParser()],
        ["Args", "example1.txt"],
        [['Seeds', 79, 14, 55, 13]]
    )
    run_gives(
        [CLI(), AlmanacParser(), Seeder()],
        ["Args", "example1.txt"],
        [['Location', 0, 82], ['Location', 1, 43], ['Location', 2, 86], ['Location', 3, 35]]
    )
    run_gives(
        [CLI(), AlmanacParser(), Seeder(), LocationMapper(), LocationMinimizer()],
        ["Args", "input1.txt"],
        [['Result', 600279879]]
    )
    run_gives(
        [CLI(), AlmanacParser(), SeederRange(), LocationMapper(), LocationMinimizer()],
        ["Args", "example1.txt"],
        [['Result', 46]]
    )
