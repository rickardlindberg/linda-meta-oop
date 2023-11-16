SUPPORT = 'class Stream:\n\n    def __init__(self, items):\n        self.items = items\n        self.index = 0\n        self.latest_error = None\n        self.scope = None\n\n    def operator_or(self, matchers):\n        for matcher in matchers:\n            backtrack_index = self.index\n            try:\n                return matcher(self)\n            except MatchError:\n                self.index = backtrack_index\n        self.error("no or match")\n\n    def operator_and(self, matchers):\n        result = self.action()\n        for matcher in matchers:\n            result = matcher(self)\n        return result\n\n    def operator_star(self, matcher):\n        results = []\n        while True:\n            backtrack_index = self.index\n            try:\n                results.append(matcher(self))\n            except MatchError:\n                self.index = backtrack_index\n                return self.action(lambda self: [x.eval(self.runtime) for x in results])\n\n    def operator_not(self, matcher):\n        backtrack_index = self.index\n        try:\n            matcher(self)\n        except MatchError:\n            return self.action()\n        finally:\n            self.index = backtrack_index\n        self.error("not matched")\n\n    def action(self, fn=lambda self: None):\n        return SemanticAction(self.scope, fn)\n\n    def with_scope(self, matcher):\n        current_scope = self.scope\n        self.scope = {}\n        try:\n            return matcher(self)\n        finally:\n            self.scope = current_scope\n\n    def bind(self, name, semantic_action):\n        self.scope[name] = semantic_action\n        return semantic_action\n\n    def match_list(self, matcher):\n        if self.index < len(self.items):\n            items, index = self.items, self.index\n            try:\n                self.items = self.items[self.index]\n                self.index = 0\n                result = matcher(self)\n                index += 1\n            finally:\n                self.items, self.index = items, index\n            return result\n        self.error("no list found")\n\n    def match_call_rule(self, rules):\n        name = self.items[self.index]\n        if name in rules:\n            matcher = rules[name]\n            self.index += 1\n            return matcher(self)\n        else:\n            self.error(f"Unknown rule {name}.")\n\n    def match(self, fn, description):\n        if self.index < len(self.items):\n            item = self.items[self.index]\n            if fn(item):\n                self.index += 1\n                return self.action(lambda self: item)\n        self.error(f"expected {description}")\n\n    def error(self, name):\n        if not self.latest_error or self.index > self.latest_error[2]:\n            self.latest_error = (name, self.items, self.index)\n        raise MatchError(*self.latest_error)\n\nclass MatchError(Exception):\n\n    def __init__(self, name, items, index):\n        Exception.__init__(self, name)\n        self.items = items\n        self.index = index\n\nclass SemanticAction:\n\n    def __init__(self, scope, fn):\n        self.scope = scope\n        self.fn = fn\n\n    def eval(self, runtime):\n        self.runtime = runtime\n        return self.fn(self)\n\n    def bind(self, name, value, continuation):\n        self.runtime = self.runtime.bind(name, value)\n        return continuation()\n\n    def lookup(self, name):\n        if name in self.scope:\n            return self.scope[name].eval(self.runtime)\n        else:\n            return self.runtime.lookup(name)\n\nclass Runtime:\n\n    def __init__(self, extra={}):\n        self.vars = extra\n\n    def bind(self, name, value):\n        return Runtime(dict(self.vars, **{name: value}))\n\n    def lookup(self, name):\n        if name in self.vars:\n            return self.vars[name]\n        else:\n            return getattr(self, name)\n\n    def append(self, list, thing):\n        list.append(thing)\n\n    def join(self, items, delimiter=""):\n        return delimiter.join(\n            self.join(item, delimiter) if isinstance(item, list) else str(item)\n            for item in items\n        )\n\n    def indent(self, text, prefix="    "):\n        return "".join(prefix+line for line in text.splitlines(True))\n\n    def splice(self, depth, item):\n        if depth == 0:\n            return [item]\n        else:\n            return self.concat([self.splice(depth-1, subitem) for subitem in item])\n\n    def concat(self, lists):\n        return [x for xs in lists for x in xs]\n\ndef run_simulation(actors, extra={}, messages=[], debug=False):\n    import sys\n    def debug_log(text):\n        if debug:\n            sys.stderr.write(f"{text}\\n")\n    def read(path):\n        if path == "-":\n            return sys.stdin.read()\n        with open(path) as f:\n            return f.read()\n    if not messages:\n        messages.append(["Args"]+sys.argv[1:])\n    iteration = 0\n    while messages:\n        debug_log(f"Iteration {iteration}")\n        for index, message in enumerate(messages):\n            debug_log(f"  Message {index:2d} = {message}")\n        debug_log("")\n        next_messages = []\n        x = {\n            "put": next_messages.append,\n            "spawn": actors.append,\n            "write": sys.stdout.write,\n            "repr": repr,\n            "read": read,\n            "len": len,\n            "repr": repr,\n            "int": int,\n        }\n        for key, value in extra.items():\n            x[key] = value\n        runtime = Runtime(x)\n        processed = False\n        for message in messages:\n            for actor in actors:\n                try:\n                    actor.run(Stream(message)).eval(runtime)\n                except MatchError:\n                    pass\n                else:\n                    processed = True\n                    break\n            else:\n                next_messages.append(message)\n        if not processed:\n            sys.exit("No message processed.")\n        messages = next_messages\n        iteration += 1\n    debug_log("Simulation done!")\n'
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

    def __init__(self, extra={}):
        self.vars = extra

    def bind(self, name, value):
        return Runtime(dict(self.vars, **{name: value}))

    def lookup(self, name):
        if name in self.vars:
            return self.vars[name]
        else:
            return getattr(self, name)

    def append(self, list, thing):
        list.append(thing)

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

def run_simulation(actors, extra={}, messages=[], debug=False):
    import sys
    def debug_log(text):
        if debug:
            sys.stderr.write(f"{text}\n")
    def read(path):
        if path == "-":
            return sys.stdin.read()
        with open(path) as f:
            return f.read()
    if not messages:
        messages.append(["Args"]+sys.argv[1:])
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
        }
        for key, value in extra.items():
            x[key] = value
        runtime = Runtime(x)
        processed = False
        for message in messages:
            for actor in actors:
                try:
                    actor.run(Stream(message)).eval(runtime)
                except MatchError:
                    pass
                else:
                    processed = True
                    break
            else:
                next_messages.append(message)
        if not processed:
            sys.exit("No message processed.")
        messages = next_messages
        iteration += 1
    debug_log("Simulation done!")
class Cli:
    def __init__(self, n=None):
        self._state = {'n': n}
        self._rules = {
            'run': self._matcher_15,
            'arg': self._matcher_48,
            'part': self._matcher_52,
        }
    def run(self, stream):
        return self._rules['run'](stream)
    def _matcher_0(self, stream):
        return stream.match(lambda item: item == 'Args', "'Args'")
    def _matcher_1(self, stream):
        return stream.match(lambda item: True, 'any')
    def _matcher_2(self, stream):
        return stream.operator_not(self._matcher_1)
    def _matcher_3(self, stream):
        return stream.action(lambda self: self.lookup('put')(
            self.lookup('concat')([
                self.lookup('splice')(0, 'Args'),
                self.lookup('splice')(0, '--compile'),
                self.lookup('splice')(0, '-')
            ])
        ))
    def _matcher_4(self, stream):
        return stream.operator_and([
            self._matcher_0,
            self._matcher_2,
            self._matcher_3
        ])
    def _matcher_5(self, stream):
        return stream.with_scope(self._matcher_4)
    def _matcher_6(self, stream):
        return stream.match(lambda item: item == 'Args', "'Args'")
    def _matcher_7(self, stream):
        return self._rules['arg'](stream)
    def _matcher_8(self, stream):
        return stream.operator_star(self._matcher_7)
    def _matcher_9(self, stream):
        return stream.bind('xs', self._matcher_8(stream))
    def _matcher_10(self, stream):
        return stream.match(lambda item: True, 'any')
    def _matcher_11(self, stream):
        return stream.operator_not(self._matcher_10)
    def _matcher_12(self, stream):
        return stream.action(lambda self: self.bind('parts', self.lookup('concat')([
        
        ]), lambda: self.bind('', self.lookup('xs'), lambda: self.lookup('spawn')(
            self.lookup('SequenceWriter')(
                0
            )
        ))))
    def _matcher_13(self, stream):
        return stream.operator_and([
            self._matcher_6,
            self._matcher_9,
            self._matcher_11,
            self._matcher_12
        ])
    def _matcher_14(self, stream):
        return stream.with_scope(self._matcher_13)
    def _matcher_15(self, stream):
        return stream.operator_or([
            self._matcher_5,
            self._matcher_14
        ])
    def _matcher_16(self, stream):
        return stream.match(lambda item: item == '--support', "'--support'")
    def _matcher_17(self, stream):
        return self._rules['part'](stream)
    def _matcher_18(self, stream):
        return stream.bind('p', self._matcher_17(stream))
    def _matcher_19(self, stream):
        return stream.action(lambda self: self.lookup('put')(
            self.lookup('concat')([
                self.lookup('splice')(0, 'Part'),
                self.lookup('splice')(0, self.lookup('p')),
                self.lookup('splice')(0, self.lookup('SUPPORT'))
            ])
        ))
    def _matcher_20(self, stream):
        return stream.operator_and([
            self._matcher_16,
            self._matcher_18,
            self._matcher_19
        ])
    def _matcher_21(self, stream):
        return stream.with_scope(self._matcher_20)
    def _matcher_22(self, stream):
        return stream.match(lambda item: item == '--copy', "'--copy'")
    def _matcher_23(self, stream):
        return stream.match(lambda item: True, 'any')
    def _matcher_24(self, stream):
        return stream.bind('path', self._matcher_23(stream))
    def _matcher_25(self, stream):
        return self._rules['part'](stream)
    def _matcher_26(self, stream):
        return stream.bind('p', self._matcher_25(stream))
    def _matcher_27(self, stream):
        return stream.action(lambda self: self.lookup('put')(
            self.lookup('concat')([
                self.lookup('splice')(0, 'Part'),
                self.lookup('splice')(0, self.lookup('p')),
                self.lookup('splice')(0, self.lookup('read')(
                    self.lookup('path')
                ))
            ])
        ))
    def _matcher_28(self, stream):
        return stream.operator_and([
            self._matcher_22,
            self._matcher_24,
            self._matcher_26,
            self._matcher_27
        ])
    def _matcher_29(self, stream):
        return stream.with_scope(self._matcher_28)
    def _matcher_30(self, stream):
        return stream.match(lambda item: item == '--embed', "'--embed'")
    def _matcher_31(self, stream):
        return stream.match(lambda item: True, 'any')
    def _matcher_32(self, stream):
        return stream.bind('name', self._matcher_31(stream))
    def _matcher_33(self, stream):
        return stream.match(lambda item: True, 'any')
    def _matcher_34(self, stream):
        return stream.bind('path', self._matcher_33(stream))
    def _matcher_35(self, stream):
        return self._rules['part'](stream)
    def _matcher_36(self, stream):
        return stream.bind('p', self._matcher_35(stream))
    def _matcher_37(self, stream):
        return stream.action(lambda self: self.lookup('put')(
            self.lookup('concat')([
                self.lookup('splice')(0, 'Part'),
                self.lookup('splice')(0, self.lookup('p')),
                self.lookup('splice')(0, self.lookup('join')([
                    self.lookup('name'),
                    ' = ',
                    self.lookup('repr')(
                        self.lookup('read')(
                            self.lookup('path')
                        )
                    ),
                    '\n'
                ]))
            ])
        ))
    def _matcher_38(self, stream):
        return stream.operator_and([
            self._matcher_30,
            self._matcher_32,
            self._matcher_34,
            self._matcher_36,
            self._matcher_37
        ])
    def _matcher_39(self, stream):
        return stream.with_scope(self._matcher_38)
    def _matcher_40(self, stream):
        return stream.match(lambda item: item == '--compile', "'--compile'")
    def _matcher_41(self, stream):
        return stream.match(lambda item: True, 'any')
    def _matcher_42(self, stream):
        return stream.bind('path', self._matcher_41(stream))
    def _matcher_43(self, stream):
        return self._rules['part'](stream)
    def _matcher_44(self, stream):
        return stream.bind('p', self._matcher_43(stream))
    def _matcher_45(self, stream):
        return stream.action(lambda self: self.lookup('put')(
            self.lookup('concat')([
                self.lookup('splice')(0, 'SourceCode'),
                self.lookup('splice')(0, self.lookup('p')),
                self.lookup('splice')(0, self.lookup('read')(
                    self.lookup('path')
                ))
            ])
        ))
    def _matcher_46(self, stream):
        return stream.operator_and([
            self._matcher_40,
            self._matcher_42,
            self._matcher_44,
            self._matcher_45
        ])
    def _matcher_47(self, stream):
        return stream.with_scope(self._matcher_46)
    def _matcher_48(self, stream):
        return stream.operator_or([
            self._matcher_21,
            self._matcher_29,
            self._matcher_39,
            self._matcher_47
        ])
    def _matcher_49(self, stream):
        return stream.action(lambda self: self.bind('id', self.lookup('len')(
            self.lookup('parts')
        ), lambda: self.bind('', self.lookup('append')(
            self.lookup('parts'),
            0
        ), lambda: self.lookup('id'))))
    def _matcher_50(self, stream):
        return stream.operator_and([
            self._matcher_49
        ])
    def _matcher_51(self, stream):
        return stream.with_scope(self._matcher_50)
    def _matcher_52(self, stream):
        return stream.operator_or([
            self._matcher_51
        ])
class SequenceWriter:
    def __init__(self, n=None):
        self._state = {'n': n}
        self._rules = {
            'run': self._matcher_10,
        }
    def run(self, stream):
        return self._rules['run'](stream)
    def _matcher_0(self, stream):
        return stream.match(lambda item: item == 'Part', "'Part'")
    def _matcher_1(self, stream):
        return stream.match(lambda item: item == self._state['n'], 'state')
    def _matcher_2(self, stream):
        return stream.bind('n', self._matcher_1(stream))
    def _matcher_3(self, stream):
        return stream.match(lambda item: True, 'any')
    def _matcher_4(self, stream):
        return stream.bind('x', self._matcher_3(stream))
    def _matcher_5(self, stream):
        return stream.match(lambda item: True, 'any')
    def _matcher_6(self, stream):
        return stream.operator_not(self._matcher_5)
    def _matcher_7(self, stream):
        return stream.action(lambda self: self.bind('', self.lookup('write')(
            self.lookup('x')
        ), lambda: self.lookup('spawn')(
            self.lookup('SequenceWriter')(
                self.lookup('add')(
                    self.lookup('n'),
                    1
                )
            )
        )))
    def _matcher_8(self, stream):
        return stream.operator_and([
            self._matcher_0,
            self._matcher_2,
            self._matcher_4,
            self._matcher_6,
            self._matcher_7
        ])
    def _matcher_9(self, stream):
        return stream.with_scope(self._matcher_8)
    def _matcher_10(self, stream):
        return stream.operator_or([
            self._matcher_9
        ])
class Parser:
    def __init__(self, n=None):
        self._state = {'n': n}
        self._rules = {
            'run': self._matcher_10,
            'file': self._matcher_24,
            'actor': self._matcher_39,
            'rule': self._matcher_50,
            'choice': self._matcher_73,
            'sequence': self._matcher_82,
            'expr': self._matcher_108,
            'expr1': self._matcher_150,
            'expr2': self._matcher_219,
            'matchChar': self._matcher_225,
            'maybeAction': self._matcher_234,
            'actionExpr': self._matcher_264,
            'hostExpr': self._matcher_318,
            'hostListItem': self._matcher_329,
            'var': self._matcher_342,
            'string': self._matcher_359,
            'char': self._matcher_372,
            'innerChar': self._matcher_381,
            'escape': self._matcher_402,
            'number': self._matcher_411,
            'name': self._matcher_421,
            'nameStart': self._matcher_428,
            'nameChar': self._matcher_438,
            'space': self._matcher_451,
        }
    def run(self, stream):
        return self._rules['run'](stream)
    def _matcher_0(self, stream):
        return stream.match(lambda item: item == 'SourceCode', "'SourceCode'")
    def _matcher_1(self, stream):
        return stream.match(lambda item: True, 'any')
    def _matcher_2(self, stream):
        return stream.bind('p', self._matcher_1(stream))
    def _matcher_3(self, stream):
        return self._rules['file'](stream)
    def _matcher_4(self, stream):
        return stream.bind('x', self._matcher_3(stream))
    def _matcher_5(self, stream):
        return stream.operator_and([
            self._matcher_4
        ])
    def _matcher_6(self, stream):
        return stream.match_list(self._matcher_5)
    def _matcher_7(self, stream):
        return stream.action(lambda self: self.lookup('put')(
            self.lookup('concat')([
                self.lookup('splice')(0, 'Ast'),
                self.lookup('splice')(0, self.lookup('p')),
                self.lookup('splice')(0, self.lookup('x'))
            ])
        ))
    def _matcher_8(self, stream):
        return stream.operator_and([
            self._matcher_0,
            self._matcher_2,
            self._matcher_6,
            self._matcher_7
        ])
    def _matcher_9(self, stream):
        return stream.with_scope(self._matcher_8)
    def _matcher_10(self, stream):
        return stream.operator_or([
            self._matcher_9
        ])
    def _matcher_11(self, stream):
        return self._rules['space'](stream)
    def _matcher_12(self, stream):
        return self._rules['actor'](stream)
    def _matcher_13(self, stream):
        return stream.operator_and([
            self._matcher_11,
            self._matcher_12
        ])
    def _matcher_14(self, stream):
        return stream.with_scope(self._matcher_13)
    def _matcher_15(self, stream):
        return stream.operator_or([
            self._matcher_14
        ])
    def _matcher_16(self, stream):
        return stream.operator_star(self._matcher_15)
    def _matcher_17(self, stream):
        return stream.bind('xs', self._matcher_16(stream))
    def _matcher_18(self, stream):
        return self._rules['space'](stream)
    def _matcher_19(self, stream):
        return stream.match(lambda item: True, 'any')
    def _matcher_20(self, stream):
        return stream.operator_not(self._matcher_19)
    def _matcher_21(self, stream):
        return stream.action(lambda self: self.lookup('xs'))
    def _matcher_22(self, stream):
        return stream.operator_and([
            self._matcher_17,
            self._matcher_18,
            self._matcher_20,
            self._matcher_21
        ])
    def _matcher_23(self, stream):
        return stream.with_scope(self._matcher_22)
    def _matcher_24(self, stream):
        return stream.operator_or([
            self._matcher_23
        ])
    def _matcher_25(self, stream):
        return self._rules['name'](stream)
    def _matcher_26(self, stream):
        return stream.bind('x', self._matcher_25(stream))
    def _matcher_27(self, stream):
        return self._rules['space'](stream)
    def _matcher_28(self, stream):
        return stream.match(lambda item: item == '{', "'{'")
    def _matcher_29(self, stream):
        return stream.operator_and([
            self._matcher_28
        ])
    def _matcher_30(self, stream):
        return self._rules['rule'](stream)
    def _matcher_31(self, stream):
        return stream.operator_star(self._matcher_30)
    def _matcher_32(self, stream):
        return stream.bind('ys', self._matcher_31(stream))
    def _matcher_33(self, stream):
        return self._rules['space'](stream)
    def _matcher_34(self, stream):
        return stream.match(lambda item: item == '}', "'}'")
    def _matcher_35(self, stream):
        return stream.operator_and([
            self._matcher_34
        ])
    def _matcher_36(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'Actor'),
            self.lookup('splice')(0, self.lookup('x')),
            self.lookup('splice')(1, self.lookup('ys'))
        ]))
    def _matcher_37(self, stream):
        return stream.operator_and([
            self._matcher_26,
            self._matcher_27,
            self._matcher_29,
            self._matcher_32,
            self._matcher_33,
            self._matcher_35,
            self._matcher_36
        ])
    def _matcher_38(self, stream):
        return stream.with_scope(self._matcher_37)
    def _matcher_39(self, stream):
        return stream.operator_or([
            self._matcher_38
        ])
    def _matcher_40(self, stream):
        return self._rules['name'](stream)
    def _matcher_41(self, stream):
        return stream.bind('x', self._matcher_40(stream))
    def _matcher_42(self, stream):
        return self._rules['space'](stream)
    def _matcher_43(self, stream):
        return stream.match(lambda item: item == '=', "'='")
    def _matcher_44(self, stream):
        return stream.operator_and([
            self._matcher_43
        ])
    def _matcher_45(self, stream):
        return self._rules['choice'](stream)
    def _matcher_46(self, stream):
        return stream.bind('y', self._matcher_45(stream))
    def _matcher_47(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'Rule'),
            self.lookup('splice')(0, self.lookup('x')),
            self.lookup('splice')(0, self.lookup('y'))
        ]))
    def _matcher_48(self, stream):
        return stream.operator_and([
            self._matcher_41,
            self._matcher_42,
            self._matcher_44,
            self._matcher_46,
            self._matcher_47
        ])
    def _matcher_49(self, stream):
        return stream.with_scope(self._matcher_48)
    def _matcher_50(self, stream):
        return stream.operator_or([
            self._matcher_49
        ])
    def _matcher_51(self, stream):
        return self._rules['space'](stream)
    def _matcher_52(self, stream):
        return stream.match(lambda item: item == '|', "'|'")
    def _matcher_53(self, stream):
        return stream.operator_and([
            self._matcher_52
        ])
    def _matcher_54(self, stream):
        return stream.operator_and([
            self._matcher_51,
            self._matcher_53
        ])
    def _matcher_55(self, stream):
        return stream.with_scope(self._matcher_54)
    def _matcher_56(self, stream):
        return stream.operator_or([
            self._matcher_55
        ])
    def _matcher_57(self, stream):
        return stream.operator_and([
        
        ])
    def _matcher_58(self, stream):
        return stream.operator_or([
            self._matcher_56,
            self._matcher_57
        ])
    def _matcher_59(self, stream):
        return self._rules['sequence'](stream)
    def _matcher_60(self, stream):
        return stream.bind('x', self._matcher_59(stream))
    def _matcher_61(self, stream):
        return self._rules['space'](stream)
    def _matcher_62(self, stream):
        return stream.match(lambda item: item == '|', "'|'")
    def _matcher_63(self, stream):
        return stream.operator_and([
            self._matcher_62
        ])
    def _matcher_64(self, stream):
        return self._rules['sequence'](stream)
    def _matcher_65(self, stream):
        return stream.operator_and([
            self._matcher_61,
            self._matcher_63,
            self._matcher_64
        ])
    def _matcher_66(self, stream):
        return stream.with_scope(self._matcher_65)
    def _matcher_67(self, stream):
        return stream.operator_or([
            self._matcher_66
        ])
    def _matcher_68(self, stream):
        return stream.operator_star(self._matcher_67)
    def _matcher_69(self, stream):
        return stream.bind('xs', self._matcher_68(stream))
    def _matcher_70(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'Or'),
            self.lookup('splice')(0, self.lookup('x')),
            self.lookup('splice')(1, self.lookup('xs'))
        ]))
    def _matcher_71(self, stream):
        return stream.operator_and([
            self._matcher_58,
            self._matcher_60,
            self._matcher_69,
            self._matcher_70
        ])
    def _matcher_72(self, stream):
        return stream.with_scope(self._matcher_71)
    def _matcher_73(self, stream):
        return stream.operator_or([
            self._matcher_72
        ])
    def _matcher_74(self, stream):
        return self._rules['expr'](stream)
    def _matcher_75(self, stream):
        return stream.operator_star(self._matcher_74)
    def _matcher_76(self, stream):
        return stream.bind('xs', self._matcher_75(stream))
    def _matcher_77(self, stream):
        return self._rules['maybeAction'](stream)
    def _matcher_78(self, stream):
        return stream.bind('ys', self._matcher_77(stream))
    def _matcher_79(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'Scope'),
            self.lookup('splice')(0, self.lookup('concat')([
                self.lookup('splice')(0, 'And'),
                self.lookup('splice')(1, self.lookup('xs')),
                self.lookup('splice')(1, self.lookup('ys'))
            ]))
        ]))
    def _matcher_80(self, stream):
        return stream.operator_and([
            self._matcher_76,
            self._matcher_78,
            self._matcher_79
        ])
    def _matcher_81(self, stream):
        return stream.with_scope(self._matcher_80)
    def _matcher_82(self, stream):
        return stream.operator_or([
            self._matcher_81
        ])
    def _matcher_83(self, stream):
        return self._rules['expr1'](stream)
    def _matcher_84(self, stream):
        return stream.bind('x', self._matcher_83(stream))
    def _matcher_85(self, stream):
        return self._rules['space'](stream)
    def _matcher_86(self, stream):
        return stream.match(lambda item: item == ':', "':'")
    def _matcher_87(self, stream):
        return stream.operator_and([
            self._matcher_86
        ])
    def _matcher_88(self, stream):
        return self._rules['name'](stream)
    def _matcher_89(self, stream):
        return stream.bind('y', self._matcher_88(stream))
    def _matcher_90(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'Bind'),
            self.lookup('splice')(0, self.lookup('y')),
            self.lookup('splice')(0, self.lookup('x'))
        ]))
    def _matcher_91(self, stream):
        return stream.operator_and([
            self._matcher_84,
            self._matcher_85,
            self._matcher_87,
            self._matcher_89,
            self._matcher_90
        ])
    def _matcher_92(self, stream):
        return stream.with_scope(self._matcher_91)
    def _matcher_93(self, stream):
        return self._rules['space'](stream)
    def _matcher_94(self, stream):
        return stream.match(lambda item: item == '[', "'['")
    def _matcher_95(self, stream):
        return stream.operator_and([
            self._matcher_94
        ])
    def _matcher_96(self, stream):
        return self._rules['expr'](stream)
    def _matcher_97(self, stream):
        return stream.operator_star(self._matcher_96)
    def _matcher_98(self, stream):
        return stream.bind('xs', self._matcher_97(stream))
    def _matcher_99(self, stream):
        return self._rules['space'](stream)
    def _matcher_100(self, stream):
        return stream.match(lambda item: item == ']', "']'")
    def _matcher_101(self, stream):
        return stream.operator_and([
            self._matcher_100
        ])
    def _matcher_102(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'MatchList'),
            self.lookup('splice')(0, self.lookup('concat')([
                self.lookup('splice')(0, 'And'),
                self.lookup('splice')(1, self.lookup('xs'))
            ]))
        ]))
    def _matcher_103(self, stream):
        return stream.operator_and([
            self._matcher_93,
            self._matcher_95,
            self._matcher_98,
            self._matcher_99,
            self._matcher_101,
            self._matcher_102
        ])
    def _matcher_104(self, stream):
        return stream.with_scope(self._matcher_103)
    def _matcher_105(self, stream):
        return self._rules['expr1'](stream)
    def _matcher_106(self, stream):
        return stream.operator_and([
            self._matcher_105
        ])
    def _matcher_107(self, stream):
        return stream.with_scope(self._matcher_106)
    def _matcher_108(self, stream):
        return stream.operator_or([
            self._matcher_92,
            self._matcher_104,
            self._matcher_107
        ])
    def _matcher_109(self, stream):
        return self._rules['expr2'](stream)
    def _matcher_110(self, stream):
        return stream.bind('x', self._matcher_109(stream))
    def _matcher_111(self, stream):
        return self._rules['space'](stream)
    def _matcher_112(self, stream):
        return stream.match(lambda item: item == '*', "'*'")
    def _matcher_113(self, stream):
        return stream.operator_and([
            self._matcher_112
        ])
    def _matcher_114(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'Star'),
            self.lookup('splice')(0, self.lookup('x'))
        ]))
    def _matcher_115(self, stream):
        return stream.operator_and([
            self._matcher_110,
            self._matcher_111,
            self._matcher_113,
            self._matcher_114
        ])
    def _matcher_116(self, stream):
        return stream.with_scope(self._matcher_115)
    def _matcher_117(self, stream):
        return self._rules['expr2'](stream)
    def _matcher_118(self, stream):
        return stream.bind('x', self._matcher_117(stream))
    def _matcher_119(self, stream):
        return self._rules['space'](stream)
    def _matcher_120(self, stream):
        return stream.match(lambda item: item == '?', "'?'")
    def _matcher_121(self, stream):
        return stream.operator_and([
            self._matcher_120
        ])
    def _matcher_122(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'Or'),
            self.lookup('splice')(0, self.lookup('x')),
            self.lookup('splice')(0, self.lookup('concat')([
                self.lookup('splice')(0, 'And')
            ]))
        ]))
    def _matcher_123(self, stream):
        return stream.operator_and([
            self._matcher_118,
            self._matcher_119,
            self._matcher_121,
            self._matcher_122
        ])
    def _matcher_124(self, stream):
        return stream.with_scope(self._matcher_123)
    def _matcher_125(self, stream):
        return self._rules['space'](stream)
    def _matcher_126(self, stream):
        return stream.match(lambda item: item == '!', "'!'")
    def _matcher_127(self, stream):
        return stream.operator_and([
            self._matcher_126
        ])
    def _matcher_128(self, stream):
        return self._rules['expr2'](stream)
    def _matcher_129(self, stream):
        return stream.bind('x', self._matcher_128(stream))
    def _matcher_130(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'Not'),
            self.lookup('splice')(0, self.lookup('x'))
        ]))
    def _matcher_131(self, stream):
        return stream.operator_and([
            self._matcher_125,
            self._matcher_127,
            self._matcher_129,
            self._matcher_130
        ])
    def _matcher_132(self, stream):
        return stream.with_scope(self._matcher_131)
    def _matcher_133(self, stream):
        return self._rules['space'](stream)
    def _matcher_134(self, stream):
        return stream.match(lambda item: item == '%', "'%'")
    def _matcher_135(self, stream):
        return stream.operator_and([
            self._matcher_134
        ])
    def _matcher_136(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'MatchCallRule')
        ]))
    def _matcher_137(self, stream):
        return stream.operator_and([
            self._matcher_133,
            self._matcher_135,
            self._matcher_136
        ])
    def _matcher_138(self, stream):
        return stream.with_scope(self._matcher_137)
    def _matcher_139(self, stream):
        return self._rules['space'](stream)
    def _matcher_140(self, stream):
        return stream.match(lambda item: item == '#', "'#'")
    def _matcher_141(self, stream):
        return stream.operator_and([
            self._matcher_140
        ])
    def _matcher_142(self, stream):
        return self._rules['name'](stream)
    def _matcher_143(self, stream):
        return stream.bind('x', self._matcher_142(stream))
    def _matcher_144(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'MatchObject'),
            self.lookup('splice')(0, self.lookup('concat')([
                self.lookup('splice')(0, 'State'),
                self.lookup('splice')(0, self.lookup('x'))
            ]))
        ]))
    def _matcher_145(self, stream):
        return stream.operator_and([
            self._matcher_139,
            self._matcher_141,
            self._matcher_143,
            self._matcher_144
        ])
    def _matcher_146(self, stream):
        return stream.with_scope(self._matcher_145)
    def _matcher_147(self, stream):
        return self._rules['expr2'](stream)
    def _matcher_148(self, stream):
        return stream.operator_and([
            self._matcher_147
        ])
    def _matcher_149(self, stream):
        return stream.with_scope(self._matcher_148)
    def _matcher_150(self, stream):
        return stream.operator_or([
            self._matcher_116,
            self._matcher_124,
            self._matcher_132,
            self._matcher_138,
            self._matcher_146,
            self._matcher_149
        ])
    def _matcher_151(self, stream):
        return self._rules['name'](stream)
    def _matcher_152(self, stream):
        return stream.bind('x', self._matcher_151(stream))
    def _matcher_153(self, stream):
        return self._rules['space'](stream)
    def _matcher_154(self, stream):
        return stream.match(lambda item: item == '=', "'='")
    def _matcher_155(self, stream):
        return stream.operator_and([
            self._matcher_154
        ])
    def _matcher_156(self, stream):
        return stream.operator_and([
            self._matcher_153,
            self._matcher_155
        ])
    def _matcher_157(self, stream):
        return stream.with_scope(self._matcher_156)
    def _matcher_158(self, stream):
        return stream.operator_or([
            self._matcher_157
        ])
    def _matcher_159(self, stream):
        return stream.operator_not(self._matcher_158)
    def _matcher_160(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'MatchRule'),
            self.lookup('splice')(0, self.lookup('x'))
        ]))
    def _matcher_161(self, stream):
        return stream.operator_and([
            self._matcher_152,
            self._matcher_159,
            self._matcher_160
        ])
    def _matcher_162(self, stream):
        return stream.with_scope(self._matcher_161)
    def _matcher_163(self, stream):
        return self._rules['space'](stream)
    def _matcher_164(self, stream):
        return self._rules['char'](stream)
    def _matcher_165(self, stream):
        return stream.bind('x', self._matcher_164(stream))
    def _matcher_166(self, stream):
        return stream.match(lambda item: item == '-', "'-'")
    def _matcher_167(self, stream):
        return stream.operator_and([
            self._matcher_166
        ])
    def _matcher_168(self, stream):
        return self._rules['char'](stream)
    def _matcher_169(self, stream):
        return stream.bind('y', self._matcher_168(stream))
    def _matcher_170(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'MatchObject'),
            self.lookup('splice')(0, self.lookup('concat')([
                self.lookup('splice')(0, 'Range'),
                self.lookup('splice')(0, self.lookup('x')),
                self.lookup('splice')(0, self.lookup('y'))
            ]))
        ]))
    def _matcher_171(self, stream):
        return stream.operator_and([
            self._matcher_163,
            self._matcher_165,
            self._matcher_167,
            self._matcher_169,
            self._matcher_170
        ])
    def _matcher_172(self, stream):
        return stream.with_scope(self._matcher_171)
    def _matcher_173(self, stream):
        return self._rules['space'](stream)
    def _matcher_174(self, stream):
        return stream.match(lambda item: item == "'", '"\'"')
    def _matcher_175(self, stream):
        return stream.operator_and([
            self._matcher_174
        ])
    def _matcher_176(self, stream):
        return stream.match(lambda item: item == "'", '"\'"')
    def _matcher_177(self, stream):
        return stream.operator_and([
            self._matcher_176
        ])
    def _matcher_178(self, stream):
        return stream.operator_not(self._matcher_177)
    def _matcher_179(self, stream):
        return self._rules['matchChar'](stream)
    def _matcher_180(self, stream):
        return stream.operator_and([
            self._matcher_178,
            self._matcher_179
        ])
    def _matcher_181(self, stream):
        return stream.with_scope(self._matcher_180)
    def _matcher_182(self, stream):
        return stream.operator_or([
            self._matcher_181
        ])
    def _matcher_183(self, stream):
        return stream.operator_star(self._matcher_182)
    def _matcher_184(self, stream):
        return stream.bind('xs', self._matcher_183(stream))
    def _matcher_185(self, stream):
        return stream.match(lambda item: item == "'", '"\'"')
    def _matcher_186(self, stream):
        return stream.operator_and([
            self._matcher_185
        ])
    def _matcher_187(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'And'),
            self.lookup('splice')(1, self.lookup('xs'))
        ]))
    def _matcher_188(self, stream):
        return stream.operator_and([
            self._matcher_173,
            self._matcher_175,
            self._matcher_184,
            self._matcher_186,
            self._matcher_187
        ])
    def _matcher_189(self, stream):
        return stream.with_scope(self._matcher_188)
    def _matcher_190(self, stream):
        return self._rules['space'](stream)
    def _matcher_191(self, stream):
        return stream.match(lambda item: item == '.', "'.'")
    def _matcher_192(self, stream):
        return stream.operator_and([
            self._matcher_191
        ])
    def _matcher_193(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'MatchObject'),
            self.lookup('splice')(0, self.lookup('concat')([
                self.lookup('splice')(0, 'Any')
            ]))
        ]))
    def _matcher_194(self, stream):
        return stream.operator_and([
            self._matcher_190,
            self._matcher_192,
            self._matcher_193
        ])
    def _matcher_195(self, stream):
        return stream.with_scope(self._matcher_194)
    def _matcher_196(self, stream):
        return self._rules['space'](stream)
    def _matcher_197(self, stream):
        return stream.match(lambda item: item == '(', "'('")
    def _matcher_198(self, stream):
        return stream.operator_and([
            self._matcher_197
        ])
    def _matcher_199(self, stream):
        return self._rules['choice'](stream)
    def _matcher_200(self, stream):
        return stream.bind('x', self._matcher_199(stream))
    def _matcher_201(self, stream):
        return self._rules['space'](stream)
    def _matcher_202(self, stream):
        return stream.match(lambda item: item == ')', "')'")
    def _matcher_203(self, stream):
        return stream.operator_and([
            self._matcher_202
        ])
    def _matcher_204(self, stream):
        return stream.action(lambda self: self.lookup('x'))
    def _matcher_205(self, stream):
        return stream.operator_and([
            self._matcher_196,
            self._matcher_198,
            self._matcher_200,
            self._matcher_201,
            self._matcher_203,
            self._matcher_204
        ])
    def _matcher_206(self, stream):
        return stream.with_scope(self._matcher_205)
    def _matcher_207(self, stream):
        return self._rules['space'](stream)
    def _matcher_208(self, stream):
        return self._rules['number'](stream)
    def _matcher_209(self, stream):
        return stream.bind('x', self._matcher_208(stream))
    def _matcher_210(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'MatchObject'),
            self.lookup('splice')(0, self.lookup('concat')([
                self.lookup('splice')(0, 'Eq'),
                self.lookup('splice')(0, self.lookup('x'))
            ]))
        ]))
    def _matcher_211(self, stream):
        return stream.operator_and([
            self._matcher_207,
            self._matcher_209,
            self._matcher_210
        ])
    def _matcher_212(self, stream):
        return stream.with_scope(self._matcher_211)
    def _matcher_213(self, stream):
        return self._rules['space'](stream)
    def _matcher_214(self, stream):
        return self._rules['string'](stream)
    def _matcher_215(self, stream):
        return stream.bind('x', self._matcher_214(stream))
    def _matcher_216(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'MatchObject'),
            self.lookup('splice')(0, self.lookup('concat')([
                self.lookup('splice')(0, 'Eq'),
                self.lookup('splice')(0, self.lookup('x'))
            ]))
        ]))
    def _matcher_217(self, stream):
        return stream.operator_and([
            self._matcher_213,
            self._matcher_215,
            self._matcher_216
        ])
    def _matcher_218(self, stream):
        return stream.with_scope(self._matcher_217)
    def _matcher_219(self, stream):
        return stream.operator_or([
            self._matcher_162,
            self._matcher_172,
            self._matcher_189,
            self._matcher_195,
            self._matcher_206,
            self._matcher_212,
            self._matcher_218
        ])
    def _matcher_220(self, stream):
        return self._rules['innerChar'](stream)
    def _matcher_221(self, stream):
        return stream.bind('x', self._matcher_220(stream))
    def _matcher_222(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'MatchObject'),
            self.lookup('splice')(0, self.lookup('concat')([
                self.lookup('splice')(0, 'Eq'),
                self.lookup('splice')(0, self.lookup('x'))
            ]))
        ]))
    def _matcher_223(self, stream):
        return stream.operator_and([
            self._matcher_221,
            self._matcher_222
        ])
    def _matcher_224(self, stream):
        return stream.with_scope(self._matcher_223)
    def _matcher_225(self, stream):
        return stream.operator_or([
            self._matcher_224
        ])
    def _matcher_226(self, stream):
        return self._rules['actionExpr'](stream)
    def _matcher_227(self, stream):
        return stream.bind('x', self._matcher_226(stream))
    def _matcher_228(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, self.lookup('concat')([
                self.lookup('splice')(0, 'Action'),
                self.lookup('splice')(0, self.lookup('x'))
            ]))
        ]))
    def _matcher_229(self, stream):
        return stream.operator_and([
            self._matcher_227,
            self._matcher_228
        ])
    def _matcher_230(self, stream):
        return stream.with_scope(self._matcher_229)
    def _matcher_231(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
        
        ]))
    def _matcher_232(self, stream):
        return stream.operator_and([
            self._matcher_231
        ])
    def _matcher_233(self, stream):
        return stream.with_scope(self._matcher_232)
    def _matcher_234(self, stream):
        return stream.operator_or([
            self._matcher_230,
            self._matcher_233
        ])
    def _matcher_235(self, stream):
        return self._rules['space'](stream)
    def _matcher_236(self, stream):
        return stream.match(lambda item: item == '-', "'-'")
    def _matcher_237(self, stream):
        return stream.match(lambda item: item == '>', "'>'")
    def _matcher_238(self, stream):
        return stream.operator_and([
            self._matcher_236,
            self._matcher_237
        ])
    def _matcher_239(self, stream):
        return self._rules['hostExpr'](stream)
    def _matcher_240(self, stream):
        return stream.bind('x', self._matcher_239(stream))
    def _matcher_241(self, stream):
        return self._rules['space'](stream)
    def _matcher_242(self, stream):
        return stream.match(lambda item: item == ':', "':'")
    def _matcher_243(self, stream):
        return stream.operator_and([
            self._matcher_242
        ])
    def _matcher_244(self, stream):
        return self._rules['name'](stream)
    def _matcher_245(self, stream):
        return stream.operator_and([
            self._matcher_241,
            self._matcher_243,
            self._matcher_244
        ])
    def _matcher_246(self, stream):
        return stream.with_scope(self._matcher_245)
    def _matcher_247(self, stream):
        return stream.action(lambda self: '')
    def _matcher_248(self, stream):
        return stream.operator_and([
            self._matcher_247
        ])
    def _matcher_249(self, stream):
        return stream.with_scope(self._matcher_248)
    def _matcher_250(self, stream):
        return stream.operator_or([
            self._matcher_246,
            self._matcher_249
        ])
    def _matcher_251(self, stream):
        return stream.bind('y', self._matcher_250(stream))
    def _matcher_252(self, stream):
        return self._rules['actionExpr'](stream)
    def _matcher_253(self, stream):
        return stream.bind('z', self._matcher_252(stream))
    def _matcher_254(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'Set'),
            self.lookup('splice')(0, self.lookup('y')),
            self.lookup('splice')(0, self.lookup('x')),
            self.lookup('splice')(0, self.lookup('z'))
        ]))
    def _matcher_255(self, stream):
        return stream.operator_and([
            self._matcher_235,
            self._matcher_238,
            self._matcher_240,
            self._matcher_251,
            self._matcher_253,
            self._matcher_254
        ])
    def _matcher_256(self, stream):
        return stream.with_scope(self._matcher_255)
    def _matcher_257(self, stream):
        return self._rules['space'](stream)
    def _matcher_258(self, stream):
        return stream.match(lambda item: item == '-', "'-'")
    def _matcher_259(self, stream):
        return stream.match(lambda item: item == '>', "'>'")
    def _matcher_260(self, stream):
        return stream.operator_and([
            self._matcher_258,
            self._matcher_259
        ])
    def _matcher_261(self, stream):
        return self._rules['hostExpr'](stream)
    def _matcher_262(self, stream):
        return stream.operator_and([
            self._matcher_257,
            self._matcher_260,
            self._matcher_261
        ])
    def _matcher_263(self, stream):
        return stream.with_scope(self._matcher_262)
    def _matcher_264(self, stream):
        return stream.operator_or([
            self._matcher_256,
            self._matcher_263
        ])
    def _matcher_265(self, stream):
        return self._rules['space'](stream)
    def _matcher_266(self, stream):
        return self._rules['string'](stream)
    def _matcher_267(self, stream):
        return stream.bind('x', self._matcher_266(stream))
    def _matcher_268(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'String'),
            self.lookup('splice')(0, self.lookup('x'))
        ]))
    def _matcher_269(self, stream):
        return stream.operator_and([
            self._matcher_265,
            self._matcher_267,
            self._matcher_268
        ])
    def _matcher_270(self, stream):
        return stream.with_scope(self._matcher_269)
    def _matcher_271(self, stream):
        return self._rules['space'](stream)
    def _matcher_272(self, stream):
        return self._rules['number'](stream)
    def _matcher_273(self, stream):
        return stream.bind('x', self._matcher_272(stream))
    def _matcher_274(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'Number'),
            self.lookup('splice')(0, self.lookup('x'))
        ]))
    def _matcher_275(self, stream):
        return stream.operator_and([
            self._matcher_271,
            self._matcher_273,
            self._matcher_274
        ])
    def _matcher_276(self, stream):
        return stream.with_scope(self._matcher_275)
    def _matcher_277(self, stream):
        return self._rules['space'](stream)
    def _matcher_278(self, stream):
        return stream.match(lambda item: item == '[', "'['")
    def _matcher_279(self, stream):
        return stream.operator_and([
            self._matcher_278
        ])
    def _matcher_280(self, stream):
        return self._rules['hostListItem'](stream)
    def _matcher_281(self, stream):
        return stream.operator_star(self._matcher_280)
    def _matcher_282(self, stream):
        return stream.bind('xs', self._matcher_281(stream))
    def _matcher_283(self, stream):
        return self._rules['space'](stream)
    def _matcher_284(self, stream):
        return stream.match(lambda item: item == ']', "']'")
    def _matcher_285(self, stream):
        return stream.operator_and([
            self._matcher_284
        ])
    def _matcher_286(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'List'),
            self.lookup('splice')(1, self.lookup('xs'))
        ]))
    def _matcher_287(self, stream):
        return stream.operator_and([
            self._matcher_277,
            self._matcher_279,
            self._matcher_282,
            self._matcher_283,
            self._matcher_285,
            self._matcher_286
        ])
    def _matcher_288(self, stream):
        return stream.with_scope(self._matcher_287)
    def _matcher_289(self, stream):
        return self._rules['space'](stream)
    def _matcher_290(self, stream):
        return stream.match(lambda item: item == '{', "'{'")
    def _matcher_291(self, stream):
        return stream.operator_and([
            self._matcher_290
        ])
    def _matcher_292(self, stream):
        return self._rules['hostExpr'](stream)
    def _matcher_293(self, stream):
        return stream.operator_star(self._matcher_292)
    def _matcher_294(self, stream):
        return stream.bind('xs', self._matcher_293(stream))
    def _matcher_295(self, stream):
        return self._rules['space'](stream)
    def _matcher_296(self, stream):
        return stream.match(lambda item: item == '}', "'}'")
    def _matcher_297(self, stream):
        return stream.operator_and([
            self._matcher_296
        ])
    def _matcher_298(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'Format'),
            self.lookup('splice')(1, self.lookup('xs'))
        ]))
    def _matcher_299(self, stream):
        return stream.operator_and([
            self._matcher_289,
            self._matcher_291,
            self._matcher_294,
            self._matcher_295,
            self._matcher_297,
            self._matcher_298
        ])
    def _matcher_300(self, stream):
        return stream.with_scope(self._matcher_299)
    def _matcher_301(self, stream):
        return self._rules['var'](stream)
    def _matcher_302(self, stream):
        return stream.bind('x', self._matcher_301(stream))
    def _matcher_303(self, stream):
        return self._rules['space'](stream)
    def _matcher_304(self, stream):
        return stream.match(lambda item: item == '(', "'('")
    def _matcher_305(self, stream):
        return stream.operator_and([
            self._matcher_304
        ])
    def _matcher_306(self, stream):
        return self._rules['hostExpr'](stream)
    def _matcher_307(self, stream):
        return stream.operator_star(self._matcher_306)
    def _matcher_308(self, stream):
        return stream.bind('ys', self._matcher_307(stream))
    def _matcher_309(self, stream):
        return self._rules['space'](stream)
    def _matcher_310(self, stream):
        return stream.match(lambda item: item == ')', "')'")
    def _matcher_311(self, stream):
        return stream.operator_and([
            self._matcher_310
        ])
    def _matcher_312(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'Call'),
            self.lookup('splice')(0, self.lookup('x')),
            self.lookup('splice')(1, self.lookup('ys'))
        ]))
    def _matcher_313(self, stream):
        return stream.operator_and([
            self._matcher_302,
            self._matcher_303,
            self._matcher_305,
            self._matcher_308,
            self._matcher_309,
            self._matcher_311,
            self._matcher_312
        ])
    def _matcher_314(self, stream):
        return stream.with_scope(self._matcher_313)
    def _matcher_315(self, stream):
        return self._rules['var'](stream)
    def _matcher_316(self, stream):
        return stream.operator_and([
            self._matcher_315
        ])
    def _matcher_317(self, stream):
        return stream.with_scope(self._matcher_316)
    def _matcher_318(self, stream):
        return stream.operator_or([
            self._matcher_270,
            self._matcher_276,
            self._matcher_288,
            self._matcher_300,
            self._matcher_314,
            self._matcher_317
        ])
    def _matcher_319(self, stream):
        return self._rules['space'](stream)
    def _matcher_320(self, stream):
        return stream.match(lambda item: item == '~', "'~'")
    def _matcher_321(self, stream):
        return stream.operator_and([
            self._matcher_320
        ])
    def _matcher_322(self, stream):
        return stream.operator_star(self._matcher_321)
    def _matcher_323(self, stream):
        return stream.bind('ys', self._matcher_322(stream))
    def _matcher_324(self, stream):
        return self._rules['hostExpr'](stream)
    def _matcher_325(self, stream):
        return stream.bind('x', self._matcher_324(stream))
    def _matcher_326(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'ListItem'),
            self.lookup('splice')(0, self.lookup('len')(
                self.lookup('ys')
            )),
            self.lookup('splice')(0, self.lookup('x'))
        ]))
    def _matcher_327(self, stream):
        return stream.operator_and([
            self._matcher_319,
            self._matcher_323,
            self._matcher_325,
            self._matcher_326
        ])
    def _matcher_328(self, stream):
        return stream.with_scope(self._matcher_327)
    def _matcher_329(self, stream):
        return stream.operator_or([
            self._matcher_328
        ])
    def _matcher_330(self, stream):
        return self._rules['name'](stream)
    def _matcher_331(self, stream):
        return stream.bind('x', self._matcher_330(stream))
    def _matcher_332(self, stream):
        return self._rules['space'](stream)
    def _matcher_333(self, stream):
        return stream.match(lambda item: item == '=', "'='")
    def _matcher_334(self, stream):
        return stream.operator_and([
            self._matcher_333
        ])
    def _matcher_335(self, stream):
        return stream.operator_and([
            self._matcher_332,
            self._matcher_334
        ])
    def _matcher_336(self, stream):
        return stream.with_scope(self._matcher_335)
    def _matcher_337(self, stream):
        return stream.operator_or([
            self._matcher_336
        ])
    def _matcher_338(self, stream):
        return stream.operator_not(self._matcher_337)
    def _matcher_339(self, stream):
        return stream.action(lambda self: self.lookup('concat')([
            self.lookup('splice')(0, 'Lookup'),
            self.lookup('splice')(0, self.lookup('x'))
        ]))
    def _matcher_340(self, stream):
        return stream.operator_and([
            self._matcher_331,
            self._matcher_338,
            self._matcher_339
        ])
    def _matcher_341(self, stream):
        return stream.with_scope(self._matcher_340)
    def _matcher_342(self, stream):
        return stream.operator_or([
            self._matcher_341
        ])
    def _matcher_343(self, stream):
        return stream.match(lambda item: item == '"', '\'"\'')
    def _matcher_344(self, stream):
        return stream.operator_and([
            self._matcher_343
        ])
    def _matcher_345(self, stream):
        return stream.match(lambda item: item == '"', '\'"\'')
    def _matcher_346(self, stream):
        return stream.operator_and([
            self._matcher_345
        ])
    def _matcher_347(self, stream):
        return stream.operator_not(self._matcher_346)
    def _matcher_348(self, stream):
        return self._rules['innerChar'](stream)
    def _matcher_349(self, stream):
        return stream.operator_and([
            self._matcher_347,
            self._matcher_348
        ])
    def _matcher_350(self, stream):
        return stream.with_scope(self._matcher_349)
    def _matcher_351(self, stream):
        return stream.operator_or([
            self._matcher_350
        ])
    def _matcher_352(self, stream):
        return stream.operator_star(self._matcher_351)
    def _matcher_353(self, stream):
        return stream.bind('xs', self._matcher_352(stream))
    def _matcher_354(self, stream):
        return stream.match(lambda item: item == '"', '\'"\'')
    def _matcher_355(self, stream):
        return stream.operator_and([
            self._matcher_354
        ])
    def _matcher_356(self, stream):
        return stream.action(lambda self: self.lookup('join')([
            self.lookup('xs')
        ]))
    def _matcher_357(self, stream):
        return stream.operator_and([
            self._matcher_344,
            self._matcher_353,
            self._matcher_355,
            self._matcher_356
        ])
    def _matcher_358(self, stream):
        return stream.with_scope(self._matcher_357)
    def _matcher_359(self, stream):
        return stream.operator_or([
            self._matcher_358
        ])
    def _matcher_360(self, stream):
        return stream.match(lambda item: item == "'", '"\'"')
    def _matcher_361(self, stream):
        return stream.operator_and([
            self._matcher_360
        ])
    def _matcher_362(self, stream):
        return stream.match(lambda item: item == "'", '"\'"')
    def _matcher_363(self, stream):
        return stream.operator_and([
            self._matcher_362
        ])
    def _matcher_364(self, stream):
        return stream.operator_not(self._matcher_363)
    def _matcher_365(self, stream):
        return self._rules['innerChar'](stream)
    def _matcher_366(self, stream):
        return stream.bind('x', self._matcher_365(stream))
    def _matcher_367(self, stream):
        return stream.match(lambda item: item == "'", '"\'"')
    def _matcher_368(self, stream):
        return stream.operator_and([
            self._matcher_367
        ])
    def _matcher_369(self, stream):
        return stream.action(lambda self: self.lookup('x'))
    def _matcher_370(self, stream):
        return stream.operator_and([
            self._matcher_361,
            self._matcher_364,
            self._matcher_366,
            self._matcher_368,
            self._matcher_369
        ])
    def _matcher_371(self, stream):
        return stream.with_scope(self._matcher_370)
    def _matcher_372(self, stream):
        return stream.operator_or([
            self._matcher_371
        ])
    def _matcher_373(self, stream):
        return stream.match(lambda item: item == '\\', "'\\\\'")
    def _matcher_374(self, stream):
        return stream.operator_and([
            self._matcher_373
        ])
    def _matcher_375(self, stream):
        return self._rules['escape'](stream)
    def _matcher_376(self, stream):
        return stream.operator_and([
            self._matcher_374,
            self._matcher_375
        ])
    def _matcher_377(self, stream):
        return stream.with_scope(self._matcher_376)
    def _matcher_378(self, stream):
        return stream.match(lambda item: True, 'any')
    def _matcher_379(self, stream):
        return stream.operator_and([
            self._matcher_378
        ])
    def _matcher_380(self, stream):
        return stream.with_scope(self._matcher_379)
    def _matcher_381(self, stream):
        return stream.operator_or([
            self._matcher_377,
            self._matcher_380
        ])
    def _matcher_382(self, stream):
        return stream.match(lambda item: item == '\\', "'\\\\'")
    def _matcher_383(self, stream):
        return stream.operator_and([
            self._matcher_382
        ])
    def _matcher_384(self, stream):
        return stream.action(lambda self: '\\')
    def _matcher_385(self, stream):
        return stream.operator_and([
            self._matcher_383,
            self._matcher_384
        ])
    def _matcher_386(self, stream):
        return stream.with_scope(self._matcher_385)
    def _matcher_387(self, stream):
        return stream.match(lambda item: item == "'", '"\'"')
    def _matcher_388(self, stream):
        return stream.operator_and([
            self._matcher_387
        ])
    def _matcher_389(self, stream):
        return stream.action(lambda self: "'")
    def _matcher_390(self, stream):
        return stream.operator_and([
            self._matcher_388,
            self._matcher_389
        ])
    def _matcher_391(self, stream):
        return stream.with_scope(self._matcher_390)
    def _matcher_392(self, stream):
        return stream.match(lambda item: item == '"', '\'"\'')
    def _matcher_393(self, stream):
        return stream.operator_and([
            self._matcher_392
        ])
    def _matcher_394(self, stream):
        return stream.action(lambda self: '"')
    def _matcher_395(self, stream):
        return stream.operator_and([
            self._matcher_393,
            self._matcher_394
        ])
    def _matcher_396(self, stream):
        return stream.with_scope(self._matcher_395)
    def _matcher_397(self, stream):
        return stream.match(lambda item: item == 'n', "'n'")
    def _matcher_398(self, stream):
        return stream.operator_and([
            self._matcher_397
        ])
    def _matcher_399(self, stream):
        return stream.action(lambda self: '\n')
    def _matcher_400(self, stream):
        return stream.operator_and([
            self._matcher_398,
            self._matcher_399
        ])
    def _matcher_401(self, stream):
        return stream.with_scope(self._matcher_400)
    def _matcher_402(self, stream):
        return stream.operator_or([
            self._matcher_386,
            self._matcher_391,
            self._matcher_396,
            self._matcher_401
        ])
    def _matcher_403(self, stream):
        return stream.match(lambda item: '0' <= item <= '9', "'0'-'9'")
    def _matcher_404(self, stream):
        return stream.bind('x', self._matcher_403(stream))
    def _matcher_405(self, stream):
        return stream.match(lambda item: '0' <= item <= '9', "'0'-'9'")
    def _matcher_406(self, stream):
        return stream.operator_star(self._matcher_405)
    def _matcher_407(self, stream):
        return stream.bind('xs', self._matcher_406(stream))
    def _matcher_408(self, stream):
        return stream.action(lambda self: self.lookup('int')(
            self.lookup('join')([
                self.lookup('x'),
                self.lookup('xs')
            ])
        ))
    def _matcher_409(self, stream):
        return stream.operator_and([
            self._matcher_404,
            self._matcher_407,
            self._matcher_408
        ])
    def _matcher_410(self, stream):
        return stream.with_scope(self._matcher_409)
    def _matcher_411(self, stream):
        return stream.operator_or([
            self._matcher_410
        ])
    def _matcher_412(self, stream):
        return self._rules['space'](stream)
    def _matcher_413(self, stream):
        return self._rules['nameStart'](stream)
    def _matcher_414(self, stream):
        return stream.bind('x', self._matcher_413(stream))
    def _matcher_415(self, stream):
        return self._rules['nameChar'](stream)
    def _matcher_416(self, stream):
        return stream.operator_star(self._matcher_415)
    def _matcher_417(self, stream):
        return stream.bind('xs', self._matcher_416(stream))
    def _matcher_418(self, stream):
        return stream.action(lambda self: self.lookup('join')([
            self.lookup('x'),
            self.lookup('xs')
        ]))
    def _matcher_419(self, stream):
        return stream.operator_and([
            self._matcher_412,
            self._matcher_414,
            self._matcher_417,
            self._matcher_418
        ])
    def _matcher_420(self, stream):
        return stream.with_scope(self._matcher_419)
    def _matcher_421(self, stream):
        return stream.operator_or([
            self._matcher_420
        ])
    def _matcher_422(self, stream):
        return stream.match(lambda item: 'a' <= item <= 'z', "'a'-'z'")
    def _matcher_423(self, stream):
        return stream.operator_and([
            self._matcher_422
        ])
    def _matcher_424(self, stream):
        return stream.with_scope(self._matcher_423)
    def _matcher_425(self, stream):
        return stream.match(lambda item: 'A' <= item <= 'Z', "'A'-'Z'")
    def _matcher_426(self, stream):
        return stream.operator_and([
            self._matcher_425
        ])
    def _matcher_427(self, stream):
        return stream.with_scope(self._matcher_426)
    def _matcher_428(self, stream):
        return stream.operator_or([
            self._matcher_424,
            self._matcher_427
        ])
    def _matcher_429(self, stream):
        return stream.match(lambda item: 'a' <= item <= 'z', "'a'-'z'")
    def _matcher_430(self, stream):
        return stream.operator_and([
            self._matcher_429
        ])
    def _matcher_431(self, stream):
        return stream.with_scope(self._matcher_430)
    def _matcher_432(self, stream):
        return stream.match(lambda item: 'A' <= item <= 'Z', "'A'-'Z'")
    def _matcher_433(self, stream):
        return stream.operator_and([
            self._matcher_432
        ])
    def _matcher_434(self, stream):
        return stream.with_scope(self._matcher_433)
    def _matcher_435(self, stream):
        return stream.match(lambda item: '0' <= item <= '9', "'0'-'9'")
    def _matcher_436(self, stream):
        return stream.operator_and([
            self._matcher_435
        ])
    def _matcher_437(self, stream):
        return stream.with_scope(self._matcher_436)
    def _matcher_438(self, stream):
        return stream.operator_or([
            self._matcher_431,
            self._matcher_434,
            self._matcher_437
        ])
    def _matcher_439(self, stream):
        return stream.match(lambda item: item == ' ', "' '")
    def _matcher_440(self, stream):
        return stream.operator_and([
            self._matcher_439
        ])
    def _matcher_441(self, stream):
        return stream.operator_and([
            self._matcher_440
        ])
    def _matcher_442(self, stream):
        return stream.with_scope(self._matcher_441)
    def _matcher_443(self, stream):
        return stream.match(lambda item: item == '\n', "'\\n'")
    def _matcher_444(self, stream):
        return stream.operator_and([
            self._matcher_443
        ])
    def _matcher_445(self, stream):
        return stream.operator_and([
            self._matcher_444
        ])
    def _matcher_446(self, stream):
        return stream.with_scope(self._matcher_445)
    def _matcher_447(self, stream):
        return stream.operator_or([
            self._matcher_442,
            self._matcher_446
        ])
    def _matcher_448(self, stream):
        return stream.operator_star(self._matcher_447)
    def _matcher_449(self, stream):
        return stream.operator_and([
            self._matcher_448
        ])
    def _matcher_450(self, stream):
        return stream.with_scope(self._matcher_449)
    def _matcher_451(self, stream):
        return stream.operator_or([
            self._matcher_450
        ])
class CodeGenerator:
    def __init__(self, n=None):
        self._state = {'n': n}
        self._rules = {
            'run': self._matcher_10,
            'asts': self._matcher_19,
            'ast': self._matcher_29,
            'Actor': self._matcher_38,
            'Rule': self._matcher_46,
            'Or': self._matcher_54,
            'Scope': self._matcher_62,
            'And': self._matcher_70,
            'Bind': self._matcher_80,
            'Star': self._matcher_88,
            'Not': self._matcher_96,
            'MatchCallRule': self._matcher_102,
            'MatchRule': self._matcher_110,
            'MatchObject': self._matcher_118,
            'MatchList': self._matcher_126,
            'Action': self._matcher_134,
            'Any': self._matcher_138,
            'State': self._matcher_144,
            'Eq': self._matcher_150,
            'Range': self._matcher_158,
            'Set': self._matcher_168,
            'String': self._matcher_172,
            'Number': self._matcher_176,
            'List': self._matcher_182,
            'ListItem': self._matcher_190,
            'Format': self._matcher_196,
            'Call': self._matcher_204,
            'Lookup': self._matcher_210,
            'astList': self._matcher_217,
            'matcher': self._matcher_221,
            'repr': self._matcher_227,
        }
    def run(self, stream):
        return self._rules['run'](stream)
    def _matcher_0(self, stream):
        return stream.match(lambda item: item == 'Ast', "'Ast'")
    def _matcher_1(self, stream):
        return stream.match(lambda item: True, 'any')
    def _matcher_2(self, stream):
        return stream.bind('p', self._matcher_1(stream))
    def _matcher_3(self, stream):
        return self._rules['asts'](stream)
    def _matcher_4(self, stream):
        return stream.bind('x', self._matcher_3(stream))
    def _matcher_5(self, stream):
        return stream.operator_and([
            self._matcher_4
        ])
    def _matcher_6(self, stream):
        return stream.match_list(self._matcher_5)
    def _matcher_7(self, stream):
        return stream.action(lambda self: self.lookup('put')(
            self.lookup('concat')([
                self.lookup('splice')(0, 'Part'),
                self.lookup('splice')(0, self.lookup('p')),
                self.lookup('splice')(0, self.lookup('x'))
            ])
        ))
    def _matcher_8(self, stream):
        return stream.operator_and([
            self._matcher_0,
            self._matcher_2,
            self._matcher_6,
            self._matcher_7
        ])
    def _matcher_9(self, stream):
        return stream.with_scope(self._matcher_8)
    def _matcher_10(self, stream):
        return stream.operator_or([
            self._matcher_9
        ])
    def _matcher_11(self, stream):
        return self._rules['ast'](stream)
    def _matcher_12(self, stream):
        return stream.operator_star(self._matcher_11)
    def _matcher_13(self, stream):
        return stream.bind('xs', self._matcher_12(stream))
    def _matcher_14(self, stream):
        return stream.match(lambda item: True, 'any')
    def _matcher_15(self, stream):
        return stream.operator_not(self._matcher_14)
    def _matcher_16(self, stream):
        return stream.action(lambda self: self.lookup('join')([
            self.lookup('xs')
        ]))
    def _matcher_17(self, stream):
        return stream.operator_and([
            self._matcher_13,
            self._matcher_15,
            self._matcher_16
        ])
    def _matcher_18(self, stream):
        return stream.with_scope(self._matcher_17)
    def _matcher_19(self, stream):
        return stream.operator_or([
            self._matcher_18
        ])
    def _matcher_20(self, stream):
        return stream.match_call_rule(self._rules)
    def _matcher_21(self, stream):
        return stream.bind('x', self._matcher_20(stream))
    def _matcher_22(self, stream):
        return stream.match(lambda item: True, 'any')
    def _matcher_23(self, stream):
        return stream.operator_not(self._matcher_22)
    def _matcher_24(self, stream):
        return stream.operator_and([
            self._matcher_21,
            self._matcher_23
        ])
    def _matcher_25(self, stream):
        return stream.match_list(self._matcher_24)
    def _matcher_26(self, stream):
        return stream.action(lambda self: self.lookup('x'))
    def _matcher_27(self, stream):
        return stream.operator_and([
            self._matcher_25,
            self._matcher_26
        ])
    def _matcher_28(self, stream):
        return stream.with_scope(self._matcher_27)
    def _matcher_29(self, stream):
        return stream.operator_or([
            self._matcher_28
        ])
    def _matcher_30(self, stream):
        return stream.match(lambda item: True, 'any')
    def _matcher_31(self, stream):
        return stream.bind('x', self._matcher_30(stream))
    def _matcher_32(self, stream):
        return self._rules['ast'](stream)
    def _matcher_33(self, stream):
        return stream.operator_star(self._matcher_32)
    def _matcher_34(self, stream):
        return stream.bind('ys', self._matcher_33(stream))
    def _matcher_35(self, stream):
        return stream.action(lambda self: self.bind('ids', self.lookup('concat')([
        
        ]), lambda: self.bind('matchers', self.lookup('concat')([
        
        ]), lambda: self.bind('rules', self.lookup('concat')([
        
        ]), lambda: self.lookup('join')([
            self.lookup('ys'),
            'class ',
            self.lookup('x'),
            ':\n',
            self.lookup('indent')(
                self.lookup('join')([
                    'def __init__(self, n=None):\n',
                    self.lookup('indent')(
                        self.lookup('join')([
                            "self._state = {'n': n}\n",
                            'self._rules = {\n',
                            self.lookup('indent')(
                                self.lookup('join')([
                                    self.lookup('rules')
                                ])
                            ),
                            '}\n'
                        ])
                    ),
                    'def run(self, stream):\n',
                    self.lookup('indent')(
                        self.lookup('join')([
                            "return self._rules['run'](stream)\n"
                        ])
                    ),
                    self.lookup('matchers')
                ])
            )
        ])))))
    def _matcher_36(self, stream):
        return stream.operator_and([
            self._matcher_31,
            self._matcher_34,
            self._matcher_35
        ])
    def _matcher_37(self, stream):
        return stream.with_scope(self._matcher_36)
    def _matcher_38(self, stream):
        return stream.operator_or([
            self._matcher_37
        ])
    def _matcher_39(self, stream):
        return stream.match(lambda item: True, 'any')
    def _matcher_40(self, stream):
        return stream.bind('x', self._matcher_39(stream))
    def _matcher_41(self, stream):
        return self._rules['ast'](stream)
    def _matcher_42(self, stream):
        return stream.bind('y', self._matcher_41(stream))
    def _matcher_43(self, stream):
        return stream.action(lambda self: self.bind('', self.lookup('append')(
            self.lookup('rules'),
            self.lookup('join')([
                self.lookup('repr')(
                    self.lookup('x')
                ),
                ': ',
                self.lookup('y'),
                ',\n'
            ])
        ), lambda: ''))
    def _matcher_44(self, stream):
        return stream.operator_and([
            self._matcher_40,
            self._matcher_42,
            self._matcher_43
        ])
    def _matcher_45(self, stream):
        return stream.with_scope(self._matcher_44)
    def _matcher_46(self, stream):
        return stream.operator_or([
            self._matcher_45
        ])
    def _matcher_47(self, stream):
        return self._rules['matcher'](stream)
    def _matcher_48(self, stream):
        return stream.bind('m', self._matcher_47(stream))
    def _matcher_49(self, stream):
        return self._rules['astList'](stream)
    def _matcher_50(self, stream):
        return stream.bind('x', self._matcher_49(stream))
    def _matcher_51(self, stream):
        return stream.action(lambda self: self.bind('body', self.lookup('join')([
            'stream.operator_or([',
            self.lookup('x'),
            '])'
        ]), lambda: self.lookup('m')))
    def _matcher_52(self, stream):
        return stream.operator_and([
            self._matcher_48,
            self._matcher_50,
            self._matcher_51
        ])
    def _matcher_53(self, stream):
        return stream.with_scope(self._matcher_52)
    def _matcher_54(self, stream):
        return stream.operator_or([
            self._matcher_53
        ])
    def _matcher_55(self, stream):
        return self._rules['matcher'](stream)
    def _matcher_56(self, stream):
        return stream.bind('m', self._matcher_55(stream))
    def _matcher_57(self, stream):
        return self._rules['ast'](stream)
    def _matcher_58(self, stream):
        return stream.bind('x', self._matcher_57(stream))
    def _matcher_59(self, stream):
        return stream.action(lambda self: self.bind('body', self.lookup('join')([
            'stream.with_scope(',
            self.lookup('x'),
            ')'
        ]), lambda: self.lookup('m')))
    def _matcher_60(self, stream):
        return stream.operator_and([
            self._matcher_56,
            self._matcher_58,
            self._matcher_59
        ])
    def _matcher_61(self, stream):
        return stream.with_scope(self._matcher_60)
    def _matcher_62(self, stream):
        return stream.operator_or([
            self._matcher_61
        ])
    def _matcher_63(self, stream):
        return self._rules['matcher'](stream)
    def _matcher_64(self, stream):
        return stream.bind('m', self._matcher_63(stream))
    def _matcher_65(self, stream):
        return self._rules['astList'](stream)
    def _matcher_66(self, stream):
        return stream.bind('x', self._matcher_65(stream))
    def _matcher_67(self, stream):
        return stream.action(lambda self: self.bind('body', self.lookup('join')([
            'stream.operator_and([',
            self.lookup('x'),
            '])'
        ]), lambda: self.lookup('m')))
    def _matcher_68(self, stream):
        return stream.operator_and([
            self._matcher_64,
            self._matcher_66,
            self._matcher_67
        ])
    def _matcher_69(self, stream):
        return stream.with_scope(self._matcher_68)
    def _matcher_70(self, stream):
        return stream.operator_or([
            self._matcher_69
        ])
    def _matcher_71(self, stream):
        return self._rules['matcher'](stream)
    def _matcher_72(self, stream):
        return stream.bind('m', self._matcher_71(stream))
    def _matcher_73(self, stream):
        return self._rules['repr'](stream)
    def _matcher_74(self, stream):
        return stream.bind('x', self._matcher_73(stream))
    def _matcher_75(self, stream):
        return self._rules['ast'](stream)
    def _matcher_76(self, stream):
        return stream.bind('y', self._matcher_75(stream))
    def _matcher_77(self, stream):
        return stream.action(lambda self: self.bind('body', self.lookup('join')([
            'stream.bind(',
            self.lookup('x'),
            ', ',
            self.lookup('y'),
            '(stream))'
        ]), lambda: self.lookup('m')))
    def _matcher_78(self, stream):
        return stream.operator_and([
            self._matcher_72,
            self._matcher_74,
            self._matcher_76,
            self._matcher_77
        ])
    def _matcher_79(self, stream):
        return stream.with_scope(self._matcher_78)
    def _matcher_80(self, stream):
        return stream.operator_or([
            self._matcher_79
        ])
    def _matcher_81(self, stream):
        return self._rules['matcher'](stream)
    def _matcher_82(self, stream):
        return stream.bind('m', self._matcher_81(stream))
    def _matcher_83(self, stream):
        return self._rules['ast'](stream)
    def _matcher_84(self, stream):
        return stream.bind('x', self._matcher_83(stream))
    def _matcher_85(self, stream):
        return stream.action(lambda self: self.bind('body', self.lookup('join')([
            'stream.operator_star(',
            self.lookup('x'),
            ')'
        ]), lambda: self.lookup('m')))
    def _matcher_86(self, stream):
        return stream.operator_and([
            self._matcher_82,
            self._matcher_84,
            self._matcher_85
        ])
    def _matcher_87(self, stream):
        return stream.with_scope(self._matcher_86)
    def _matcher_88(self, stream):
        return stream.operator_or([
            self._matcher_87
        ])
    def _matcher_89(self, stream):
        return self._rules['matcher'](stream)
    def _matcher_90(self, stream):
        return stream.bind('m', self._matcher_89(stream))
    def _matcher_91(self, stream):
        return self._rules['ast'](stream)
    def _matcher_92(self, stream):
        return stream.bind('x', self._matcher_91(stream))
    def _matcher_93(self, stream):
        return stream.action(lambda self: self.bind('body', self.lookup('join')([
            'stream.operator_not(',
            self.lookup('x'),
            ')'
        ]), lambda: self.lookup('m')))
    def _matcher_94(self, stream):
        return stream.operator_and([
            self._matcher_90,
            self._matcher_92,
            self._matcher_93
        ])
    def _matcher_95(self, stream):
        return stream.with_scope(self._matcher_94)
    def _matcher_96(self, stream):
        return stream.operator_or([
            self._matcher_95
        ])
    def _matcher_97(self, stream):
        return self._rules['matcher'](stream)
    def _matcher_98(self, stream):
        return stream.bind('m', self._matcher_97(stream))
    def _matcher_99(self, stream):
        return stream.action(lambda self: self.bind('body', self.lookup('join')([
            'stream.match_call_rule(self._rules)'
        ]), lambda: self.lookup('m')))
    def _matcher_100(self, stream):
        return stream.operator_and([
            self._matcher_98,
            self._matcher_99
        ])
    def _matcher_101(self, stream):
        return stream.with_scope(self._matcher_100)
    def _matcher_102(self, stream):
        return stream.operator_or([
            self._matcher_101
        ])
    def _matcher_103(self, stream):
        return self._rules['matcher'](stream)
    def _matcher_104(self, stream):
        return stream.bind('m', self._matcher_103(stream))
    def _matcher_105(self, stream):
        return stream.match(lambda item: True, 'any')
    def _matcher_106(self, stream):
        return stream.bind('x', self._matcher_105(stream))
    def _matcher_107(self, stream):
        return stream.action(lambda self: self.bind('body', self.lookup('join')([
            "self._rules['",
            self.lookup('x'),
            "'](stream)"
        ]), lambda: self.lookup('m')))
    def _matcher_108(self, stream):
        return stream.operator_and([
            self._matcher_104,
            self._matcher_106,
            self._matcher_107
        ])
    def _matcher_109(self, stream):
        return stream.with_scope(self._matcher_108)
    def _matcher_110(self, stream):
        return stream.operator_or([
            self._matcher_109
        ])
    def _matcher_111(self, stream):
        return self._rules['matcher'](stream)
    def _matcher_112(self, stream):
        return stream.bind('m', self._matcher_111(stream))
    def _matcher_113(self, stream):
        return self._rules['ast'](stream)
    def _matcher_114(self, stream):
        return stream.bind('x', self._matcher_113(stream))
    def _matcher_115(self, stream):
        return stream.action(lambda self: self.bind('body', self.lookup('join')([
            'stream.match(lambda item: ',
            self.lookup('x'),
            ')'
        ]), lambda: self.lookup('m')))
    def _matcher_116(self, stream):
        return stream.operator_and([
            self._matcher_112,
            self._matcher_114,
            self._matcher_115
        ])
    def _matcher_117(self, stream):
        return stream.with_scope(self._matcher_116)
    def _matcher_118(self, stream):
        return stream.operator_or([
            self._matcher_117
        ])
    def _matcher_119(self, stream):
        return self._rules['matcher'](stream)
    def _matcher_120(self, stream):
        return stream.bind('m', self._matcher_119(stream))
    def _matcher_121(self, stream):
        return self._rules['ast'](stream)
    def _matcher_122(self, stream):
        return stream.bind('x', self._matcher_121(stream))
    def _matcher_123(self, stream):
        return stream.action(lambda self: self.bind('body', self.lookup('join')([
            'stream.match_list(',
            self.lookup('x'),
            ')'
        ]), lambda: self.lookup('m')))
    def _matcher_124(self, stream):
        return stream.operator_and([
            self._matcher_120,
            self._matcher_122,
            self._matcher_123
        ])
    def _matcher_125(self, stream):
        return stream.with_scope(self._matcher_124)
    def _matcher_126(self, stream):
        return stream.operator_or([
            self._matcher_125
        ])
    def _matcher_127(self, stream):
        return self._rules['matcher'](stream)
    def _matcher_128(self, stream):
        return stream.bind('m', self._matcher_127(stream))
    def _matcher_129(self, stream):
        return self._rules['ast'](stream)
    def _matcher_130(self, stream):
        return stream.bind('x', self._matcher_129(stream))
    def _matcher_131(self, stream):
        return stream.action(lambda self: self.bind('body', self.lookup('join')([
            'stream.action(lambda self: ',
            self.lookup('x'),
            ')'
        ]), lambda: self.lookup('m')))
    def _matcher_132(self, stream):
        return stream.operator_and([
            self._matcher_128,
            self._matcher_130,
            self._matcher_131
        ])
    def _matcher_133(self, stream):
        return stream.with_scope(self._matcher_132)
    def _matcher_134(self, stream):
        return stream.operator_or([
            self._matcher_133
        ])
    def _matcher_135(self, stream):
        return stream.action(lambda self: self.lookup('join')([
            'True',
            ", 'any'"
        ]))
    def _matcher_136(self, stream):
        return stream.operator_and([
            self._matcher_135
        ])
    def _matcher_137(self, stream):
        return stream.with_scope(self._matcher_136)
    def _matcher_138(self, stream):
        return stream.operator_or([
            self._matcher_137
        ])
    def _matcher_139(self, stream):
        return self._rules['repr'](stream)
    def _matcher_140(self, stream):
        return stream.bind('x', self._matcher_139(stream))
    def _matcher_141(self, stream):
        return stream.action(lambda self: self.lookup('join')([
            'item == self._state[',
            self.lookup('x'),
            "], 'state'"
        ]))
    def _matcher_142(self, stream):
        return stream.operator_and([
            self._matcher_140,
            self._matcher_141
        ])
    def _matcher_143(self, stream):
        return stream.with_scope(self._matcher_142)
    def _matcher_144(self, stream):
        return stream.operator_or([
            self._matcher_143
        ])
    def _matcher_145(self, stream):
        return self._rules['repr'](stream)
    def _matcher_146(self, stream):
        return stream.bind('x', self._matcher_145(stream))
    def _matcher_147(self, stream):
        return stream.action(lambda self: self.lookup('join')([
            'item == ',
            self.lookup('x'),
            ', ',
            self.lookup('repr')(
                self.lookup('x')
            )
        ]))
    def _matcher_148(self, stream):
        return stream.operator_and([
            self._matcher_146,
            self._matcher_147
        ])
    def _matcher_149(self, stream):
        return stream.with_scope(self._matcher_148)
    def _matcher_150(self, stream):
        return stream.operator_or([
            self._matcher_149
        ])
    def _matcher_151(self, stream):
        return self._rules['repr'](stream)
    def _matcher_152(self, stream):
        return stream.bind('x', self._matcher_151(stream))
    def _matcher_153(self, stream):
        return self._rules['repr'](stream)
    def _matcher_154(self, stream):
        return stream.bind('y', self._matcher_153(stream))
    def _matcher_155(self, stream):
        return stream.action(lambda self: self.lookup('join')([
            self.lookup('x'),
            ' <= item <= ',
            self.lookup('y'),
            ', "',
            self.lookup('x'),
            '-',
            self.lookup('y'),
            '"'
        ]))
    def _matcher_156(self, stream):
        return stream.operator_and([
            self._matcher_152,
            self._matcher_154,
            self._matcher_155
        ])
    def _matcher_157(self, stream):
        return stream.with_scope(self._matcher_156)
    def _matcher_158(self, stream):
        return stream.operator_or([
            self._matcher_157
        ])
    def _matcher_159(self, stream):
        return self._rules['repr'](stream)
    def _matcher_160(self, stream):
        return stream.bind('x', self._matcher_159(stream))
    def _matcher_161(self, stream):
        return self._rules['ast'](stream)
    def _matcher_162(self, stream):
        return stream.bind('y', self._matcher_161(stream))
    def _matcher_163(self, stream):
        return self._rules['ast'](stream)
    def _matcher_164(self, stream):
        return stream.bind('z', self._matcher_163(stream))
    def _matcher_165(self, stream):
        return stream.action(lambda self: self.lookup('join')([
            'self.bind(',
            self.lookup('x'),
            ', ',
            self.lookup('y'),
            ', lambda: ',
            self.lookup('z'),
            ')'
        ]))
    def _matcher_166(self, stream):
        return stream.operator_and([
            self._matcher_160,
            self._matcher_162,
            self._matcher_164,
            self._matcher_165
        ])
    def _matcher_167(self, stream):
        return stream.with_scope(self._matcher_166)
    def _matcher_168(self, stream):
        return stream.operator_or([
            self._matcher_167
        ])
    def _matcher_169(self, stream):
        return self._rules['repr'](stream)
    def _matcher_170(self, stream):
        return stream.operator_and([
            self._matcher_169
        ])
    def _matcher_171(self, stream):
        return stream.with_scope(self._matcher_170)
    def _matcher_172(self, stream):
        return stream.operator_or([
            self._matcher_171
        ])
    def _matcher_173(self, stream):
        return self._rules['repr'](stream)
    def _matcher_174(self, stream):
        return stream.operator_and([
            self._matcher_173
        ])
    def _matcher_175(self, stream):
        return stream.with_scope(self._matcher_174)
    def _matcher_176(self, stream):
        return stream.operator_or([
            self._matcher_175
        ])
    def _matcher_177(self, stream):
        return self._rules['astList'](stream)
    def _matcher_178(self, stream):
        return stream.bind('x', self._matcher_177(stream))
    def _matcher_179(self, stream):
        return stream.action(lambda self: self.lookup('join')([
            "self.lookup('concat')([",
            self.lookup('x'),
            '])'
        ]))
    def _matcher_180(self, stream):
        return stream.operator_and([
            self._matcher_178,
            self._matcher_179
        ])
    def _matcher_181(self, stream):
        return stream.with_scope(self._matcher_180)
    def _matcher_182(self, stream):
        return stream.operator_or([
            self._matcher_181
        ])
    def _matcher_183(self, stream):
        return self._rules['repr'](stream)
    def _matcher_184(self, stream):
        return stream.bind('x', self._matcher_183(stream))
    def _matcher_185(self, stream):
        return self._rules['ast'](stream)
    def _matcher_186(self, stream):
        return stream.bind('y', self._matcher_185(stream))
    def _matcher_187(self, stream):
        return stream.action(lambda self: self.lookup('join')([
            "self.lookup('splice')(",
            self.lookup('x'),
            ', ',
            self.lookup('y'),
            ')'
        ]))
    def _matcher_188(self, stream):
        return stream.operator_and([
            self._matcher_184,
            self._matcher_186,
            self._matcher_187
        ])
    def _matcher_189(self, stream):
        return stream.with_scope(self._matcher_188)
    def _matcher_190(self, stream):
        return stream.operator_or([
            self._matcher_189
        ])
    def _matcher_191(self, stream):
        return self._rules['astList'](stream)
    def _matcher_192(self, stream):
        return stream.bind('x', self._matcher_191(stream))
    def _matcher_193(self, stream):
        return stream.action(lambda self: self.lookup('join')([
            "self.lookup('join')([",
            self.lookup('x'),
            '])'
        ]))
    def _matcher_194(self, stream):
        return stream.operator_and([
            self._matcher_192,
            self._matcher_193
        ])
    def _matcher_195(self, stream):
        return stream.with_scope(self._matcher_194)
    def _matcher_196(self, stream):
        return stream.operator_or([
            self._matcher_195
        ])
    def _matcher_197(self, stream):
        return self._rules['ast'](stream)
    def _matcher_198(self, stream):
        return stream.bind('x', self._matcher_197(stream))
    def _matcher_199(self, stream):
        return self._rules['astList'](stream)
    def _matcher_200(self, stream):
        return stream.bind('y', self._matcher_199(stream))
    def _matcher_201(self, stream):
        return stream.action(lambda self: self.lookup('join')([
            self.lookup('x'),
            '(',
            self.lookup('y'),
            ')'
        ]))
    def _matcher_202(self, stream):
        return stream.operator_and([
            self._matcher_198,
            self._matcher_200,
            self._matcher_201
        ])
    def _matcher_203(self, stream):
        return stream.with_scope(self._matcher_202)
    def _matcher_204(self, stream):
        return stream.operator_or([
            self._matcher_203
        ])
    def _matcher_205(self, stream):
        return self._rules['repr'](stream)
    def _matcher_206(self, stream):
        return stream.bind('x', self._matcher_205(stream))
    def _matcher_207(self, stream):
        return stream.action(lambda self: self.lookup('join')([
            'self.lookup(',
            self.lookup('x'),
            ')'
        ]))
    def _matcher_208(self, stream):
        return stream.operator_and([
            self._matcher_206,
            self._matcher_207
        ])
    def _matcher_209(self, stream):
        return stream.with_scope(self._matcher_208)
    def _matcher_210(self, stream):
        return stream.operator_or([
            self._matcher_209
        ])
    def _matcher_211(self, stream):
        return self._rules['ast'](stream)
    def _matcher_212(self, stream):
        return stream.operator_star(self._matcher_211)
    def _matcher_213(self, stream):
        return stream.bind('xs', self._matcher_212(stream))
    def _matcher_214(self, stream):
        return stream.action(lambda self: self.lookup('join')([
            '\n',
            self.lookup('indent')(
                self.lookup('join')(
                    self.lookup('xs'),
                    ',\n'
                )
            ),
            '\n'
        ]))
    def _matcher_215(self, stream):
        return stream.operator_and([
            self._matcher_213,
            self._matcher_214
        ])
    def _matcher_216(self, stream):
        return stream.with_scope(self._matcher_215)
    def _matcher_217(self, stream):
        return stream.operator_or([
            self._matcher_216
        ])
    def _matcher_218(self, stream):
        return stream.action(lambda self: self.bind('id', self.lookup('join')([
            '_matcher_',
            self.lookup('len')(
                self.lookup('ids')
            )
        ]), lambda: self.bind('', self.lookup('append')(
            self.lookup('ids'),
            self.lookup('id')
        ), lambda: self.bind('', self.lookup('append')(
            self.lookup('matchers'),
            self.lookup('join')([
                'def ',
                self.lookup('id'),
                '(self, stream):\n',
                self.lookup('indent')(
                    self.lookup('join')([
                        'return ',
                        self.lookup('body'),
                        '\n'
                    ])
                )
            ])
        ), lambda: self.lookup('join')([
            'self.',
            self.lookup('id')
        ])))))
    def _matcher_219(self, stream):
        return stream.operator_and([
            self._matcher_218
        ])
    def _matcher_220(self, stream):
        return stream.with_scope(self._matcher_219)
    def _matcher_221(self, stream):
        return stream.operator_or([
            self._matcher_220
        ])
    def _matcher_222(self, stream):
        return stream.match(lambda item: True, 'any')
    def _matcher_223(self, stream):
        return stream.bind('x', self._matcher_222(stream))
    def _matcher_224(self, stream):
        return stream.action(lambda self: self.lookup('repr')(
            self.lookup('x')
        ))
    def _matcher_225(self, stream):
        return stream.operator_and([
            self._matcher_223,
            self._matcher_224
        ])
    def _matcher_226(self, stream):
        return stream.with_scope(self._matcher_225)
    def _matcher_227(self, stream):
        return stream.operator_or([
            self._matcher_226
        ])
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
