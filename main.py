if __name__ == "__main__":
    import sys
    import operator
    messages = [["Args"]+sys.argv[1:]]
    iteration = 0
    while messages:
        print(f"Iteration {iteration}")
        for index, message in enumerate(messages):
            print(f"  Message {index:2d} = {message}")
        print()
        next_messages = []
        runtime = Runtime({
            "put": next_messages.append,
            "print": lambda text: print(f"Print: {text}\n"),
            "append": lambda xs, item: xs+[item],
            "sub": operator.sub,
            "mul": operator.mul,
        })
        while messages:
            message = messages.pop(0)
            for name, rule in rules.items():
                if name.endswith(".run"):
                    try:
                        rule.run(Stream(message)).eval(runtime)
                    except MatchError:
                        pass
                    else:
                        break
            else:
                sys.exit(f"ERROR: Message {message} not processed.")
        messages = next_messages
        iteration += 1
    print("Done!")
