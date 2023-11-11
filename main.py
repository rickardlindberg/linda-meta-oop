if __name__ == "__main__":
    import operator
    run_simulation({
        "print": lambda text: print(f"Print: {text}\n"),
        "sub": operator.sub,
        "mul": operator.mul,
    })
