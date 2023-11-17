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
            "SequenceWriter": SequenceWriter,
            "add": lambda x, y: x+y,
        }
    )
