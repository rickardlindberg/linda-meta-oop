if __name__ == "__main__":
    run_simulation(
        [
            Cli(),
            Parser(),
            CodeGenerator(),
        ],
        {
            "SUPPORT": SUPPORT,
            "SequenceWriter": SequenceWriter,
            "add": lambda x, y: x+y,
        }
    )
