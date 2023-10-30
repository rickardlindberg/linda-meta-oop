if __name__ == "__main__":
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
            "print": lambda text: print(f"Print: {text}"),
        })
        while messages:
            message = messages.pop(0)
            rules["Examples.run"].run(Stream(message)).eval(runtime)
        messages = next_messages
        iteration += 1
