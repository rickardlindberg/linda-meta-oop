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
    print()
    print("OK!")
