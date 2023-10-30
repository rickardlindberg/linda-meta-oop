if __name__ == "__main__":
    import operator
    import functools
    messages = [["Start"]]
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
            "sub": lambda things: functools.reduce(operator.sub, things),
            "mul": lambda things: functools.reduce(operator.mul, things, 1),
        })
        while messages:
            message = messages.pop(0)
            rules["Examples.run"].run(Stream(message)).eval(runtime)
        messages = next_messages
        iteration += 1
