if __name__ == "__main__":
    run_simulation(
        [
            Cli(),
            Parser(),
            CodeGenerator(),
            StdoutWriter(),
        ],
        {
            "SUPPORT": SUPPORT,
            "PartCollector": PartCollector,
            "add": lambda x, y: x+y,
            "sub": lambda x, y: x-y,
        },
    )
