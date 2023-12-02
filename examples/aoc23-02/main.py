import operator

def run(actors, message):
    return run_simulation(
        actors=actors,
        extra={
            "add": operator.add,
            "sum": sum,
            "max": max,
            "mul": operator.mul,
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
        [GameParser()],
        ["File", "Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green\n"],
        [
            ['Games',
                ['Game', 1,
                    ['Subset', ['Cubes', 3, 'blue'], ['Cubes', 4, 'red']],
                    ['Subset', ['Cubes', 1, 'red'], ['Cubes', 2, 'green'], ['Cubes', 6, 'blue']],
                    ['Subset', ['Cubes', 2, 'green']]]
            ]
        ]
    )
    run_gives(
        [GameMaxer()],
        ['Games',
            ['Game', 1,
                ['Subset', ['Cubes', 3, 'blue'], ['Cubes', 4, 'red']],
                ['Subset', ['Cubes', 1, 'red'], ['Cubes', 2, 'green'], ['Cubes', 6, 'blue']],
                ['Subset', ['Cubes', 2, 'green']]]
        ],
        [
            ['MaxedGames',
                ['Game', 1, 4, 2, 6]
            ]
        ]
    )
    run_gives(
        [GameFilterer()],
        ['MaxedGames',
            ['Game', 1, 4, 2, 6],
            ['Game', 2, 4, 2, 22],
        ],
        [
            ['FilteredGames', 1]
        ]
    )
    run_gives(
        [CLI(), GameParser(), GameMaxer(), GameFilterer(), FilterSummary()],
        ['Args', 'example1.txt'],
        [['Result', 8]]
    )
    run_gives(
        [CLI(), GameParser(), GameMaxer(), GameFilterer(), FilterSummary()],
        ['Args', 'input1.txt'],
        [['Result', 2416]]
    )
    run_gives(
        [CLI(), GameParser(), GameMaxer(), GamePower(), FilterSummary()],
        ['Args', 'example1.txt'],
        [['Result', 2286]]
    )
    run_gives(
        [CLI(), GameParser(), GameMaxer(), GamePower(), FilterSummary()],
        ['Args', 'input1.txt'],
        [['Result', 63307]]
    )
    print()
    print("OK!")
