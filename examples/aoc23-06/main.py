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
    run_gives(
        [CLI(), RecordParserBetterKerning(), MarginCalculator(), MarginProduct()],
        ["Args", "example.txt"],
        [['Result', 71503]]
    )
    run_gives(
        [CLI(), RecordParserBetterKerning(), MarginCalculator(), MarginProduct()],
        ["Args", "input.txt"],
        [['Result', 23654842]]
    )
