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
        [CLI(), HandParser(), CardRanker(), CardSorter()],
        ["Args", "example.txt"],
        [['SortedHands',
            ['RankedHand', 765, 1, 3, 2, 10, 3, 13],
            ['RankedHand', 220, 2, 13, 10, 11, 11, 10],
            ['RankedHand', 28, 2, 13, 13, 6, 7, 7],
            ['RankedHand', 684, 3, 10, 5, 5, 11, 5],
            ['RankedHand', 483, 3, 12, 12, 12, 11, 14],
        ]]
    )
    run_gives(
        [CLI(), HandParser(), CardRanker(), CardSorter(), CalculateWinnings()],
        ["Args", "example.txt"],
        [['Result', 6440]]
    )
    run_gives(
        [CLI(), HandParser(), CardRanker(), CardSorter(), CalculateWinnings()],
        ["Args", "input.txt"],
        [['Result', 253910319]]
    )
    run_gives(
        [CLI(), HandParser(), CardRankerJoker(), CardSorter(), CalculateWinnings()],
        ["Args", "example.txt"],
        [['Result', 5905]]
    )
    run_gives(
        [CLI(), HandParser(), CardRankerJoker(), CardSorter(), CalculateWinnings()],
        ["Args", "input.txt"],
        [['Result', 254083736]]
    )
