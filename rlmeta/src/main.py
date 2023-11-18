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
        },
    )
