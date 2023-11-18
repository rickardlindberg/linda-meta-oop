if __name__ == "__main__":
    run_simulation(
        [
            Cli(),
            Parser(),
            Optimizer(),
            CodeGenerator(),
            StdoutWriter(),
        ],
        {
            "SUPPORT": SUPPORT,
            "PartCollector": PartCollector,
        },
    )
