if __name__ == "__main__":
    import operator
    run_simulation(
        actors=[
            ArgsParser(),
            Greeter(),
            Factorial(),
        ],
        extra={
            "print": lambda text: print(f"Print: {text}\n"),
            "sub": operator.sub,
            "mul": operator.mul,
        },
        debug=True
    )
