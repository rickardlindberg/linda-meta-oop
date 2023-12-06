import operator

def doMap(mapSpec, number):
    if isinstance(number, list):
        result = []
        for start, size in number:
            result.extend(mapRange(start, size, mapSpec))
        return result
    else:
        for target, source, size in mapSpec:
            if number >= source and number <= (source+size):
                return number - source + target
        return number

def mapRange(start, size, mapSpec):
    result = []
    left = [[start, size]]
    for spec_target, spec_source, spec_size in mapSpec:
        next_left = []
        for start, size in left:
            x, y = mapRangeSingle(start, size, spec_target, spec_source, spec_size)
            next_left.extend(x)
            result.extend(y)
        left = next_left
    return result+left

def mapRangeSingle(start, size, spec_target, spec_source, spec_size, debug=False):
    left = []
    result = []
    end = start + size
    spec_end = spec_source + spec_size

    # [spec_source, spec_source+spec_size]
    # [start, end]


    overlap_start = min(end, max(start, spec_source))
    overlap_end = max(start, min(spec_end, end))

    overlap_size = overlap_end - overlap_start

    left_size = overlap_start - start
    right_size = size - overlap_size - left_size

    #if debug:
    #    raise ValueError((left_size, overlap_size, right_size))

    if left_size > 0:
        left.append([start, left_size])
    if overlap_size > 0:
        result.append([overlap_start+spec_target-spec_source, overlap_size])
    if right_size > 0:
        left.append([overlap_start+overlap_size, right_size])

    assert left_size+overlap_size+right_size == size

    return left, result

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

    x = mapRange(0, 10, [(20, 0, 5)])
    assert x == [[20, 5], [5, 5]], x

    x = mapRange(10, 10, [(20, 6, 5)])
    # 6 -> 20
    # 7 -> 21
    # 8 -> 22
    # 9 -> 23
    # 10 -> 24
    assert x == [[24, 1], [11, 9]], x

    x = mapRangeSingle(0, 10, 100, 5, 5, debug=True)
    # 5 -> 100
    # 6 -> 101
    # 7 -> 102
    # 8 -> 103
    # 9 -> 104
    assert x == ([[0, 5]], [[100, 5]]), x

    run_gives(
        [CLI(), AlmanacParser(), SeederRange(), LocationMapper(), LocationMinimizerRange()],
        ["Args", "example1.txt"],
        [['Result', 46]]
    )
    run_gives(
        [CLI(), AlmanacParser(), SeederRange(), LocationMapper(), LocationMinimizerRange()],
        ["Args", "input1.txt"],
        [['Result', 20191102]]
    )
