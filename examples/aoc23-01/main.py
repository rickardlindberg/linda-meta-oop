import operator

def run(solver, message):
    return run_simulation(
        actors=[
            CLI(),
            solver(),
            Lines(),
            Numbers(),
        ],
        extra={
            "add": operator.add,
            "sum": sum,
        },
        debug=True,
        fail=False,
        messages=[message]
    )

if __name__ == "__main__":
    assert run(Solver, ["Args", "example1.txt"]) == [["Result", 142]]
    assert run(Solver, ["Args", "input.txt"]) == [["Result", 54388]]
    assert run(Solver2, ["File", "843329\n"]) == [["Result", 89]]
    assert run(Solver2, ["File", "5oneightfg\n"]) == [["Result", 58]]
    assert run(Solver2, ["File", "one\n"]) == [["Result", 11]]
    assert run(Solver2, ["File", "oneight\n"]) == [["Result", 18]]
    assert run(Solver2, ["Args", "example2.txt"]) == [["Result", 281]]
    assert run(Solver2, ["Args", "input.txt"]) == [["Result", 53515]]
    print()
    print("OK!")
