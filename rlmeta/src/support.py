class Stream:

    def __init__(self, items):
        self.items = items
        self.index = 0
        self.latest_error = None
        self.scope = None

    def operator_or(self, matchers):
        for matcher in matchers:
            backtrack_index = self.index
            try:
                return matcher(self)
            except MatchError:
                self.index = backtrack_index
        self.error("no or match")

    def operator_and(self, matchers):
        result = self.action()
        for matcher in matchers:
            result = matcher(self)
        return result

    def operator_star(self, matcher):
        results = []
        while True:
            backtrack_index = self.index
            try:
                results.append(matcher(self))
            except MatchError:
                self.index = backtrack_index
                return self.action(lambda self: [x.eval(self.runtime) for x in results])

    def operator_not(self, matcher):
        backtrack_index = self.index
        try:
            matcher(self)
        except MatchError:
            return self.action()
        finally:
            self.index = backtrack_index
        self.error("not matched")

    def action(self, fn=lambda self: None):
        return SemanticAction(self.scope, fn)

    def with_scope(self, matcher):
        current_scope = self.scope
        self.scope = {}
        try:
            return matcher(self)
        finally:
            self.scope = current_scope

    def bind(self, name, semantic_action):
        self.scope[name] = semantic_action
        return semantic_action

    def match_list(self, matcher):
        if self.index < len(self.items):
            items, index = self.items, self.index
            try:
                self.items = self.items[self.index]
                self.index = 0
                result = matcher(self)
                index += 1
            finally:
                self.items, self.index = items, index
            return result
        self.error("no list found")

    def match_call_rule(self, rules):
        name = self.items[self.index]
        if name in rules:
            matcher = rules[name]
            self.index += 1
            return matcher(self)
        else:
            self.error(f"Unknown rule {name}.")

    def match(self, fn, description):
        if self.index < len(self.items):
            item = self.items[self.index]
            if fn(item):
                self.index += 1
                return self.action(lambda self: item)
        self.error(f"expected {description}")

    def error(self, name):
        if not self.latest_error or self.index > self.latest_error[2]:
            self.latest_error = (name, self.items, self.index)
        raise MatchError(*self.latest_error)

class MatchError(Exception):

    def __init__(self, name, items, index):
        Exception.__init__(self, name)
        self.items = items
        self.index = index

class SemanticAction:

    def __init__(self, scope, fn):
        self.scope = scope
        self.fn = fn

    def eval(self, runtime):
        self.runtime = runtime
        return self.fn(self)

    def bind(self, name, value, continuation):
        self.runtime = self.runtime.bind(name, value)
        return continuation()

    def lookup(self, name):
        if name in self.scope:
            return self.scope[name].eval(self.runtime)
        else:
            return self.runtime.lookup(name)

class Runtime:

    def __init__(self, actor, extra={}):
        self.vars = extra
        self.actor = actor

    def bind(self, name, value):
        return Runtime(self.actor, dict(self.vars, **{name: value}))

    def lookup(self, name):
        if name in self.vars:
            return self.vars[name]
        elif name in self.actor._state:
            return self.actor._state[name]
        else:
            return getattr(self, name)

    def increment(self, number):
        return number + 1

    def decrement(self, number):
        return number - 1

    def collector(self):
        class collector(list):
            def __call__(self, item):
                self.append(item)
        return collector()

    def join(self, items, delimiter=""):
        return delimiter.join(
            self.join(item, delimiter) if isinstance(item, list) else str(item)
            for item in items
        )

    def indent(self, text, prefix="    "):
        return "".join(prefix+line for line in text.splitlines(True))

    def splice(self, depth, item):
        if depth == 0:
            return [item]
        else:
            return self.concat([self.splice(depth-1, subitem) for subitem in item])

    def concat(self, lists):
        return [x for xs in lists for x in xs]

class Counter:

    def __init__(self):
        self.number = 0

    def __call__(self):
        result = self.number
        self.number += 1
        return result

import sys

def read(path):
    if path == "-":
        return sys.stdin.read()
    with open(path) as f:
        return f.read()

def run_simulation(actors, extra={}, messages=[], debug=False):
    def debug_log(text):
        if debug:
            sys.stderr.write(f"{text}\n")
    if not messages:
        messages.append(["Args"]+sys.argv[1:])
    message_server(actors, messages, extra)
    return
    iteration = 0
    while messages:
        debug_log(f"Iteration {iteration}")
        for index, message in enumerate(messages):
            debug_log(f"  Message {index:2d} = {message}")
        debug_log("")
        next_messages = []
        x = {
            "put": next_messages.append,
            "spawn": actors.append,
            "write": sys.stdout.write,
            "repr": repr,
            "read": read,
            "len": len,
            "repr": repr,
            "int": int,
            "Counter": Counter,
            "exit": sys.exit,
        }
        for key, value in extra.items():
            x[key] = value
        processed = False
        errors = []
        for message in messages:
            for actor in list(actors):
                try:
                    actor.run(Stream(message)).eval(Runtime(actor, x).bind(
                        "kill",
                        lambda: actors.remove(actor)
                    ))
                except MatchError as e:
                    errors.append((actor, e))
                else:
                    processed = True
                    break
            else:
                next_messages.append(message)
        if not processed:
            for actor, error in errors:
                sys.stderr.write(f"{actor.__class__.__name__} {actor._state}\n")
                sys.stderr.write(f"  {error} at {error.index}\n")
                sys.stderr.write(f"  {error.items}\n")
                sys.stderr.write("\n")
            sys.exit("No message processed.")
        messages = next_messages
        iteration += 1
    debug_log("Actors:")
    for actor in actors:
        debug_log(f"  - {actor.__class__.__name__} {actor._state}")
    debug_log("Simulation done!")

import multiprocessing
import uuid

def message_server(actors, init_messages, extra):
    def spawn(actor):
        server, client = multiprocessing.Pipe()
        clients.append(server)
        p = multiprocessing.Process(target=actor_client, args=(actor, client, extra), daemon=True)
        p.start()
        client.close()
    def put(message):
        messages[uuid.uuid4().int] = message
    def exit():
        #sys.stderr.write(f"Done!\n")
        sys.exit()
    def response(request):
        fns = {
            "get_message_ids": lambda: list(messages.keys()),
            "get_message": lambda message_id: messages.get(message_id, None),
            "pop_message": lambda message_id: messages.pop(message_id, None) is not None,
            "spawn": spawn,
            "put": put,
            "exit": exit,
        }
        response = fns[request[0]](*request[1:])
        #sys.stderr.write(f"{request} ->\n")
        #sys.stderr.write(f"  {response}\n")
        return response
    messages = {}
    for message in init_messages:
        put(message)
    clients = []
    for actor in actors:
        spawn(actor)
    while True:
        for client in multiprocessing.connection.wait(clients):
            try:
                request = client.recv()
            except EOFError:
                clients.remove(client)
            else:
                client.send(response(request))

def actor_client(actor, server, extra):
    def put(message):
        server.send(["put", message])
        server.recv()
    def spawn(actor):
        server.send(["spawn", actor])
        server.recv()
    def exit():
        server.send(["exit"])
        server.recv()
    conditions = [1]
    while conditions:
        server.send(["get_message_ids"])
        message_ids = server.recv()
        for message_id in message_ids:
            server.send(["get_message", message_id])
            message = server.recv()
            if message:
                try:
                    action = actor.run(Stream(message))
                except MatchError:
                    pass
                else:
                    server.send(["pop_message", message_id])
                    message_popped = server.recv()
                    if message_popped:
                        x = {
                            "put": put,
                            "spawn": spawn,
                            "exit": exit,
                            "write": sys.stdout.write,
                            "repr": repr,
                            "read": read,
                            "len": len,
                            "repr": repr,
                            "int": int,
                            "Counter": Counter,
                        }
                        for key, value in extra.items():
                            x[key] = value
                        action.eval(Runtime(actor, x).bind(
                            "kill",
                            lambda: conditions.pop()
                        ))
