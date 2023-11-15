SUPPORT = 'rules = {}\n\nclass Stream:\n\n    def __init__(self, items):\n        self.items = items\n        self.index = 0\n        self.latest_error = None\n        self.scope = None\n\n    def operator_or(self, matchers):\n        for matcher in matchers:\n            backtrack_index = self.index\n            try:\n                return matcher(self)\n            except MatchError:\n                self.index = backtrack_index\n        self.error("no or match")\n\n    def operator_and(self, matchers):\n        result = self.action()\n        for matcher in matchers:\n            result = matcher(self)\n        return result\n\n    def operator_star(self, matcher):\n        results = []\n        while True:\n            backtrack_index = self.index\n            try:\n                results.append(matcher(self))\n            except MatchError:\n                self.index = backtrack_index\n                return self.action(lambda self: [x.eval(self.runtime) for x in results])\n\n    def operator_not(self, matcher):\n        backtrack_index = self.index\n        try:\n            matcher(self)\n        except MatchError:\n            return self.action()\n        finally:\n            self.index = backtrack_index\n        self.error("not matched")\n\n    def action(self, fn=lambda self: None):\n        return SemanticAction(self.scope, fn)\n\n    def with_scope(self, matcher):\n        current_scope = self.scope\n        self.scope = {}\n        try:\n            return matcher(self)\n        finally:\n            self.scope = current_scope\n\n    def bind(self, name, semantic_action):\n        self.scope[name] = semantic_action\n        return semantic_action\n\n    def match_list(self, matcher):\n        if self.index < len(self.items):\n            items, index = self.items, self.index\n            try:\n                self.items = self.items[self.index]\n                self.index = 0\n                result = matcher(self)\n                index += 1\n            finally:\n                self.items, self.index = items, index\n            return result\n        self.error("no list found")\n\n    def match_call_rule(self, namespace):\n        name = namespace + "." + self.items[self.index]\n        if name in rules:\n            rule = rules[name]\n            self.index += 1\n            return rule(self)\n        else:\n            self.error("unknown rule")\n\n    def match(self, fn, description):\n        if self.index < len(self.items):\n            item = self.items[self.index]\n            if fn(item):\n                self.index += 1\n                return self.action(lambda self: item)\n        self.error(f"expected {description}")\n\n    def error(self, name):\n        if not self.latest_error or self.index > self.latest_error[2]:\n            self.latest_error = (name, self.items, self.index)\n        raise MatchError(*self.latest_error)\n\nclass MatchError(Exception):\n\n    def __init__(self, name, items, index):\n        Exception.__init__(self, name)\n        self.items = items\n        self.index = index\n\nclass SemanticAction:\n\n    def __init__(self, scope, fn):\n        self.scope = scope\n        self.fn = fn\n\n    def eval(self, runtime):\n        self.runtime = runtime\n        return self.fn(self)\n\n    def bind(self, name, value, continuation):\n        self.runtime = self.runtime.bind(name, value)\n        return continuation()\n\n    def lookup(self, name):\n        if name in self.scope:\n            return self.scope[name].eval(self.runtime)\n        else:\n            return self.runtime.lookup(name)\n\nclass Runtime:\n\n    def __init__(self, extra={}):\n        self.vars = extra\n\n    def bind(self, name, value):\n        return Runtime(dict(self.vars, **{name: value}))\n\n    def lookup(self, name):\n        if name in self.vars:\n            return self.vars[name]\n        else:\n            return getattr(self, name)\n\n    def append(self, list, thing):\n        list.append(thing)\n\n    def join(self, items, delimiter=""):\n        return delimiter.join(\n            self.join(item, delimiter) if isinstance(item, list) else str(item)\n            for item in items\n        )\n\n    def indent(self, text, prefix="    "):\n        return "".join(prefix+line for line in text.splitlines(True))\n\n    def splice(self, depth, item):\n        if depth == 0:\n            return [item]\n        else:\n            return self.concat([self.splice(depth-1, subitem) for subitem in item])\n\n    def concat(self, lists):\n        return [x for xs in lists for x in xs]\n\ndef compile_chain(grammars, source):\n    import os\n    import sys\n    import pprint\n    runtime = Runtime({"len": len, "repr": repr, "int": int})\n    for rule in grammars:\n        try:\n            source = rules[rule](Stream(source)).eval(runtime)\n        except MatchError as e:\n            marker = "<ERROR POSITION>"\n            if os.isatty(sys.stderr.fileno()):\n                marker = f"\\033[0;31m{marker}\\033[0m"\n            if isinstance(e.items, str):\n                stream_string = e.items[:e.index] + marker + e.items[e.index:]\n            else:\n                stream_string = pprint.pformat(e.items)\n            sys.exit("ERROR: {}\\nPOSITION: {}\\nSTREAM:\\n{}".format(\n                str(e),\n                e.index,\n                runtime.indent(stream_string)\n            ))\n    return source\n\ndef run_simulation(actors, extra={}):\n    import sys\n    def debug(text):\n        sys.stderr.write(f"{text}\\n")\n    def read(path):\n        if path == "-":\n            return sys.stdin.read()\n        with open(path) as f:\n            return f.read()\n    messages = [["Args"]+sys.argv[1:]]\n    iteration = 0\n    while messages:\n        debug(f"Iteration {iteration}")\n        for index, message in enumerate(messages):\n            debug(f"  Message {index:2d} = {message}")\n        debug("")\n        next_messages = []\n        x = {\n            "put": next_messages.append,\n            "write": sys.stdout.write,\n            "repr": repr,\n            "read": read,\n            "len": len,\n            "repr": repr,\n            "int": int,\n        }\n        for key, value in extra.items():\n            x[key] = value\n        runtime = Runtime(x)\n        while messages:\n            message = messages.pop(0)\n            for actor in actors:\n                try:\n                    actor.run(Stream(message)).eval(runtime)\n                except MatchError:\n                    pass\n                else:\n                    break\n            else:\n                sys.exit(f"ERROR: Message {message} not processed.")\n        messages = next_messages\n        iteration += 1\n    debug("Simulation done!")\n'
rules = {}

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

    def match_call_rule(self, namespace):
        name = namespace + "." + self.items[self.index]
        if name in rules:
            rule = rules[name]
            self.index += 1
            return rule(self)
        else:
            self.error("unknown rule")

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

def compile_chain(grammars, source):
    import os
    import sys
    import pprint
    runtime = Runtime({"len": len, "repr": repr, "int": int})
    for rule in grammars:
        try:
            source = rules[rule](Stream(source)).eval(runtime)
        except MatchError as e:
            marker = "<ERROR POSITION>"
            if os.isatty(sys.stderr.fileno()):
                marker = f"\033[0;31m{marker}\033[0m"
            if isinstance(e.items, str):
                stream_string = e.items[:e.index] + marker + e.items[e.index:]
            else:
                stream_string = pprint.pformat(e.items)
            sys.exit("ERROR: {}\nPOSITION: {}\nSTREAM:\n{}".format(
                str(e),
                e.index,
                runtime.indent(stream_string)
            ))
    return source

def run_simulation(actors, extra={}):
    import sys
    def debug(text):
        sys.stderr.write(f"{text}\n")
    def read(path):
        if path == "-":
            return sys.stdin.read()
        with open(path) as f:
            return f.read()
    messages = [["Args"]+sys.argv[1:]]
    iteration = 0
    while messages:
        debug(f"Iteration {iteration}")
        for index, message in enumerate(messages):
            debug(f"  Message {index:2d} = {message}")
        debug("")
        next_messages = []
        x = {
            "put": next_messages.append,
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
        while messages:
            message = messages.pop(0)
            for actor in actors:
                try:
                    actor.run(Stream(message)).eval(runtime)
                except MatchError:
                    pass
                else:
                    break
            else:
                sys.exit(f"ERROR: Message {message} not processed.")
        messages = next_messages
        iteration += 1
    debug("Simulation done!")
def Matcher_Cli_0(stream):
    return stream.match(lambda item: item == 'Args', "'Args'")
def Matcher_Cli_1(stream):
    return stream.match(lambda item: True, 'any')
def Matcher_Cli_2(stream):
    return stream.operator_not(Matcher_Cli_1)
def Matcher_Cli_3(stream):
    return stream.action(lambda self: self.lookup('put')(
        self.lookup('concat')([
            self.lookup('splice')(0, 'Args'),
            self.lookup('splice')(0, '--compile'),
            self.lookup('splice')(0, '-')
        ])
    ))
def Matcher_Cli_4(stream):
    return stream.operator_and([
        Matcher_Cli_0,
        Matcher_Cli_2,
        Matcher_Cli_3
    ])
def Matcher_Cli_5(stream):
    return stream.with_scope(Matcher_Cli_4)
def Matcher_Cli_6(stream):
    return stream.match(lambda item: item == 'Args', "'Args'")
def Matcher_Cli_7(stream):
    return rules['Cli.arg'](stream)
def Matcher_Cli_8(stream):
    return stream.operator_star(Matcher_Cli_7)
def Matcher_Cli_9(stream):
    return stream.bind('xs', Matcher_Cli_8(stream))
def Matcher_Cli_10(stream):
    return stream.match(lambda item: True, 'any')
def Matcher_Cli_11(stream):
    return stream.operator_not(Matcher_Cli_10)
def Matcher_Cli_12(stream):
    return stream.action(lambda self: self.lookup('xs'))
def Matcher_Cli_13(stream):
    return stream.operator_and([
        Matcher_Cli_6,
        Matcher_Cli_9,
        Matcher_Cli_11,
        Matcher_Cli_12
    ])
def Matcher_Cli_14(stream):
    return stream.with_scope(Matcher_Cli_13)
def Matcher_Cli_15(stream):
    return stream.operator_or([
        Matcher_Cli_5,
        Matcher_Cli_14
    ])
def Matcher_Cli_16(stream):
    return stream.match(lambda item: item == '--support', "'--support'")
def Matcher_Cli_17(stream):
    return stream.action(lambda self: self.lookup('write')(
        self.lookup('SUPPORT')
    ))
def Matcher_Cli_18(stream):
    return stream.operator_and([
        Matcher_Cli_16,
        Matcher_Cli_17
    ])
def Matcher_Cli_19(stream):
    return stream.with_scope(Matcher_Cli_18)
def Matcher_Cli_20(stream):
    return stream.match(lambda item: item == '--copy', "'--copy'")
def Matcher_Cli_21(stream):
    return stream.match(lambda item: True, 'any')
def Matcher_Cli_22(stream):
    return stream.bind('path', Matcher_Cli_21(stream))
def Matcher_Cli_23(stream):
    return stream.action(lambda self: self.lookup('write')(
        self.lookup('read')(
            self.lookup('path')
        )
    ))
def Matcher_Cli_24(stream):
    return stream.operator_and([
        Matcher_Cli_20,
        Matcher_Cli_22,
        Matcher_Cli_23
    ])
def Matcher_Cli_25(stream):
    return stream.with_scope(Matcher_Cli_24)
def Matcher_Cli_26(stream):
    return stream.match(lambda item: item == '--embed', "'--embed'")
def Matcher_Cli_27(stream):
    return stream.match(lambda item: True, 'any')
def Matcher_Cli_28(stream):
    return stream.bind('name', Matcher_Cli_27(stream))
def Matcher_Cli_29(stream):
    return stream.match(lambda item: True, 'any')
def Matcher_Cli_30(stream):
    return stream.bind('path', Matcher_Cli_29(stream))
def Matcher_Cli_31(stream):
    return stream.action(lambda self: self.lookup('write')(
        self.lookup('join')([
            self.lookup('name'),
            ' = ',
            self.lookup('repr')(
                self.lookup('read')(
                    self.lookup('path')
                )
            ),
            '\n'
        ])
    ))
def Matcher_Cli_32(stream):
    return stream.operator_and([
        Matcher_Cli_26,
        Matcher_Cli_28,
        Matcher_Cli_30,
        Matcher_Cli_31
    ])
def Matcher_Cli_33(stream):
    return stream.with_scope(Matcher_Cli_32)
def Matcher_Cli_34(stream):
    return stream.match(lambda item: item == '--compile', "'--compile'")
def Matcher_Cli_35(stream):
    return stream.match(lambda item: True, 'any')
def Matcher_Cli_36(stream):
    return stream.bind('path', Matcher_Cli_35(stream))
def Matcher_Cli_37(stream):
    return stream.action(lambda self: self.lookup('put')(
        self.lookup('concat')([
            self.lookup('splice')(0, 'SourceCode'),
            self.lookup('splice')(0, self.lookup('read')(
                self.lookup('path')
            ))
        ])
    ))
def Matcher_Cli_38(stream):
    return stream.operator_and([
        Matcher_Cli_34,
        Matcher_Cli_36,
        Matcher_Cli_37
    ])
def Matcher_Cli_39(stream):
    return stream.with_scope(Matcher_Cli_38)
def Matcher_Cli_40(stream):
    return stream.operator_or([
        Matcher_Cli_19,
        Matcher_Cli_25,
        Matcher_Cli_33,
        Matcher_Cli_39
    ])
rules['Cli.run'] = Matcher_Cli_15
rules['Cli.arg'] = Matcher_Cli_40
class Cli:
    def __init__(self):
        pass
    def run(self, stream):
        return rules['Cli.run'](stream)
def Matcher_Parser_0(stream):
    return stream.match(lambda item: item == 'SourceCode', "'SourceCode'")
def Matcher_Parser_1(stream):
    return rules['Parser.file'](stream)
def Matcher_Parser_2(stream):
    return stream.bind('x', Matcher_Parser_1(stream))
def Matcher_Parser_3(stream):
    return stream.operator_and([
        Matcher_Parser_2
    ])
def Matcher_Parser_4(stream):
    return stream.match_list(Matcher_Parser_3)
def Matcher_Parser_5(stream):
    return stream.action(lambda self: self.lookup('put')(
        self.lookup('concat')([
            self.lookup('splice')(0, 'Ast'),
            self.lookup('splice')(0, self.lookup('x'))
        ])
    ))
def Matcher_Parser_6(stream):
    return stream.operator_and([
        Matcher_Parser_0,
        Matcher_Parser_4,
        Matcher_Parser_5
    ])
def Matcher_Parser_7(stream):
    return stream.with_scope(Matcher_Parser_6)
def Matcher_Parser_8(stream):
    return stream.operator_or([
        Matcher_Parser_7
    ])
def Matcher_Parser_9(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_10(stream):
    return rules['Parser.actor'](stream)
def Matcher_Parser_11(stream):
    return stream.operator_and([
        Matcher_Parser_9,
        Matcher_Parser_10
    ])
def Matcher_Parser_12(stream):
    return stream.with_scope(Matcher_Parser_11)
def Matcher_Parser_13(stream):
    return stream.operator_or([
        Matcher_Parser_12
    ])
def Matcher_Parser_14(stream):
    return stream.operator_star(Matcher_Parser_13)
def Matcher_Parser_15(stream):
    return stream.bind('xs', Matcher_Parser_14(stream))
def Matcher_Parser_16(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_17(stream):
    return stream.match(lambda item: True, 'any')
def Matcher_Parser_18(stream):
    return stream.operator_not(Matcher_Parser_17)
def Matcher_Parser_19(stream):
    return stream.action(lambda self: self.lookup('xs'))
def Matcher_Parser_20(stream):
    return stream.operator_and([
        Matcher_Parser_15,
        Matcher_Parser_16,
        Matcher_Parser_18,
        Matcher_Parser_19
    ])
def Matcher_Parser_21(stream):
    return stream.with_scope(Matcher_Parser_20)
def Matcher_Parser_22(stream):
    return stream.operator_or([
        Matcher_Parser_21
    ])
def Matcher_Parser_23(stream):
    return rules['Parser.name'](stream)
def Matcher_Parser_24(stream):
    return stream.bind('x', Matcher_Parser_23(stream))
def Matcher_Parser_25(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_26(stream):
    return stream.match(lambda item: item == '{', "'{'")
def Matcher_Parser_27(stream):
    return stream.operator_and([
        Matcher_Parser_26
    ])
def Matcher_Parser_28(stream):
    return rules['Parser.rule'](stream)
def Matcher_Parser_29(stream):
    return stream.operator_star(Matcher_Parser_28)
def Matcher_Parser_30(stream):
    return stream.bind('ys', Matcher_Parser_29(stream))
def Matcher_Parser_31(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_32(stream):
    return stream.match(lambda item: item == '}', "'}'")
def Matcher_Parser_33(stream):
    return stream.operator_and([
        Matcher_Parser_32
    ])
def Matcher_Parser_34(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'Actor'),
        self.lookup('splice')(0, self.lookup('x')),
        self.lookup('splice')(1, self.lookup('ys'))
    ]))
def Matcher_Parser_35(stream):
    return stream.operator_and([
        Matcher_Parser_24,
        Matcher_Parser_25,
        Matcher_Parser_27,
        Matcher_Parser_30,
        Matcher_Parser_31,
        Matcher_Parser_33,
        Matcher_Parser_34
    ])
def Matcher_Parser_36(stream):
    return stream.with_scope(Matcher_Parser_35)
def Matcher_Parser_37(stream):
    return stream.operator_or([
        Matcher_Parser_36
    ])
def Matcher_Parser_38(stream):
    return rules['Parser.name'](stream)
def Matcher_Parser_39(stream):
    return stream.bind('x', Matcher_Parser_38(stream))
def Matcher_Parser_40(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_41(stream):
    return stream.match(lambda item: item == '=', "'='")
def Matcher_Parser_42(stream):
    return stream.operator_and([
        Matcher_Parser_41
    ])
def Matcher_Parser_43(stream):
    return rules['Parser.choice'](stream)
def Matcher_Parser_44(stream):
    return stream.bind('y', Matcher_Parser_43(stream))
def Matcher_Parser_45(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'Rule'),
        self.lookup('splice')(0, self.lookup('x')),
        self.lookup('splice')(0, self.lookup('y'))
    ]))
def Matcher_Parser_46(stream):
    return stream.operator_and([
        Matcher_Parser_39,
        Matcher_Parser_40,
        Matcher_Parser_42,
        Matcher_Parser_44,
        Matcher_Parser_45
    ])
def Matcher_Parser_47(stream):
    return stream.with_scope(Matcher_Parser_46)
def Matcher_Parser_48(stream):
    return stream.operator_or([
        Matcher_Parser_47
    ])
def Matcher_Parser_49(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_50(stream):
    return stream.match(lambda item: item == '|', "'|'")
def Matcher_Parser_51(stream):
    return stream.operator_and([
        Matcher_Parser_50
    ])
def Matcher_Parser_52(stream):
    return stream.operator_and([
        Matcher_Parser_49,
        Matcher_Parser_51
    ])
def Matcher_Parser_53(stream):
    return stream.with_scope(Matcher_Parser_52)
def Matcher_Parser_54(stream):
    return stream.operator_or([
        Matcher_Parser_53
    ])
def Matcher_Parser_55(stream):
    return stream.operator_and([
    
    ])
def Matcher_Parser_56(stream):
    return stream.operator_or([
        Matcher_Parser_54,
        Matcher_Parser_55
    ])
def Matcher_Parser_57(stream):
    return rules['Parser.sequence'](stream)
def Matcher_Parser_58(stream):
    return stream.bind('x', Matcher_Parser_57(stream))
def Matcher_Parser_59(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_60(stream):
    return stream.match(lambda item: item == '|', "'|'")
def Matcher_Parser_61(stream):
    return stream.operator_and([
        Matcher_Parser_60
    ])
def Matcher_Parser_62(stream):
    return rules['Parser.sequence'](stream)
def Matcher_Parser_63(stream):
    return stream.operator_and([
        Matcher_Parser_59,
        Matcher_Parser_61,
        Matcher_Parser_62
    ])
def Matcher_Parser_64(stream):
    return stream.with_scope(Matcher_Parser_63)
def Matcher_Parser_65(stream):
    return stream.operator_or([
        Matcher_Parser_64
    ])
def Matcher_Parser_66(stream):
    return stream.operator_star(Matcher_Parser_65)
def Matcher_Parser_67(stream):
    return stream.bind('xs', Matcher_Parser_66(stream))
def Matcher_Parser_68(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'Or'),
        self.lookup('splice')(0, self.lookup('x')),
        self.lookup('splice')(1, self.lookup('xs'))
    ]))
def Matcher_Parser_69(stream):
    return stream.operator_and([
        Matcher_Parser_56,
        Matcher_Parser_58,
        Matcher_Parser_67,
        Matcher_Parser_68
    ])
def Matcher_Parser_70(stream):
    return stream.with_scope(Matcher_Parser_69)
def Matcher_Parser_71(stream):
    return stream.operator_or([
        Matcher_Parser_70
    ])
def Matcher_Parser_72(stream):
    return rules['Parser.expr'](stream)
def Matcher_Parser_73(stream):
    return stream.operator_star(Matcher_Parser_72)
def Matcher_Parser_74(stream):
    return stream.bind('xs', Matcher_Parser_73(stream))
def Matcher_Parser_75(stream):
    return rules['Parser.maybeAction'](stream)
def Matcher_Parser_76(stream):
    return stream.bind('ys', Matcher_Parser_75(stream))
def Matcher_Parser_77(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'Scope'),
        self.lookup('splice')(0, self.lookup('concat')([
            self.lookup('splice')(0, 'And'),
            self.lookup('splice')(1, self.lookup('xs')),
            self.lookup('splice')(1, self.lookup('ys'))
        ]))
    ]))
def Matcher_Parser_78(stream):
    return stream.operator_and([
        Matcher_Parser_74,
        Matcher_Parser_76,
        Matcher_Parser_77
    ])
def Matcher_Parser_79(stream):
    return stream.with_scope(Matcher_Parser_78)
def Matcher_Parser_80(stream):
    return stream.operator_or([
        Matcher_Parser_79
    ])
def Matcher_Parser_81(stream):
    return rules['Parser.expr1'](stream)
def Matcher_Parser_82(stream):
    return stream.bind('x', Matcher_Parser_81(stream))
def Matcher_Parser_83(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_84(stream):
    return stream.match(lambda item: item == ':', "':'")
def Matcher_Parser_85(stream):
    return stream.operator_and([
        Matcher_Parser_84
    ])
def Matcher_Parser_86(stream):
    return rules['Parser.name'](stream)
def Matcher_Parser_87(stream):
    return stream.bind('y', Matcher_Parser_86(stream))
def Matcher_Parser_88(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'Bind'),
        self.lookup('splice')(0, self.lookup('y')),
        self.lookup('splice')(0, self.lookup('x'))
    ]))
def Matcher_Parser_89(stream):
    return stream.operator_and([
        Matcher_Parser_82,
        Matcher_Parser_83,
        Matcher_Parser_85,
        Matcher_Parser_87,
        Matcher_Parser_88
    ])
def Matcher_Parser_90(stream):
    return stream.with_scope(Matcher_Parser_89)
def Matcher_Parser_91(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_92(stream):
    return stream.match(lambda item: item == '[', "'['")
def Matcher_Parser_93(stream):
    return stream.operator_and([
        Matcher_Parser_92
    ])
def Matcher_Parser_94(stream):
    return rules['Parser.expr'](stream)
def Matcher_Parser_95(stream):
    return stream.operator_star(Matcher_Parser_94)
def Matcher_Parser_96(stream):
    return stream.bind('xs', Matcher_Parser_95(stream))
def Matcher_Parser_97(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_98(stream):
    return stream.match(lambda item: item == ']', "']'")
def Matcher_Parser_99(stream):
    return stream.operator_and([
        Matcher_Parser_98
    ])
def Matcher_Parser_100(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'MatchList'),
        self.lookup('splice')(0, self.lookup('concat')([
            self.lookup('splice')(0, 'And'),
            self.lookup('splice')(1, self.lookup('xs'))
        ]))
    ]))
def Matcher_Parser_101(stream):
    return stream.operator_and([
        Matcher_Parser_91,
        Matcher_Parser_93,
        Matcher_Parser_96,
        Matcher_Parser_97,
        Matcher_Parser_99,
        Matcher_Parser_100
    ])
def Matcher_Parser_102(stream):
    return stream.with_scope(Matcher_Parser_101)
def Matcher_Parser_103(stream):
    return rules['Parser.expr1'](stream)
def Matcher_Parser_104(stream):
    return stream.operator_and([
        Matcher_Parser_103
    ])
def Matcher_Parser_105(stream):
    return stream.with_scope(Matcher_Parser_104)
def Matcher_Parser_106(stream):
    return stream.operator_or([
        Matcher_Parser_90,
        Matcher_Parser_102,
        Matcher_Parser_105
    ])
def Matcher_Parser_107(stream):
    return rules['Parser.expr2'](stream)
def Matcher_Parser_108(stream):
    return stream.bind('x', Matcher_Parser_107(stream))
def Matcher_Parser_109(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_110(stream):
    return stream.match(lambda item: item == '*', "'*'")
def Matcher_Parser_111(stream):
    return stream.operator_and([
        Matcher_Parser_110
    ])
def Matcher_Parser_112(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'Star'),
        self.lookup('splice')(0, self.lookup('x'))
    ]))
def Matcher_Parser_113(stream):
    return stream.operator_and([
        Matcher_Parser_108,
        Matcher_Parser_109,
        Matcher_Parser_111,
        Matcher_Parser_112
    ])
def Matcher_Parser_114(stream):
    return stream.with_scope(Matcher_Parser_113)
def Matcher_Parser_115(stream):
    return rules['Parser.expr2'](stream)
def Matcher_Parser_116(stream):
    return stream.bind('x', Matcher_Parser_115(stream))
def Matcher_Parser_117(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_118(stream):
    return stream.match(lambda item: item == '?', "'?'")
def Matcher_Parser_119(stream):
    return stream.operator_and([
        Matcher_Parser_118
    ])
def Matcher_Parser_120(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'Or'),
        self.lookup('splice')(0, self.lookup('x')),
        self.lookup('splice')(0, self.lookup('concat')([
            self.lookup('splice')(0, 'And')
        ]))
    ]))
def Matcher_Parser_121(stream):
    return stream.operator_and([
        Matcher_Parser_116,
        Matcher_Parser_117,
        Matcher_Parser_119,
        Matcher_Parser_120
    ])
def Matcher_Parser_122(stream):
    return stream.with_scope(Matcher_Parser_121)
def Matcher_Parser_123(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_124(stream):
    return stream.match(lambda item: item == '!', "'!'")
def Matcher_Parser_125(stream):
    return stream.operator_and([
        Matcher_Parser_124
    ])
def Matcher_Parser_126(stream):
    return rules['Parser.expr2'](stream)
def Matcher_Parser_127(stream):
    return stream.bind('x', Matcher_Parser_126(stream))
def Matcher_Parser_128(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'Not'),
        self.lookup('splice')(0, self.lookup('x'))
    ]))
def Matcher_Parser_129(stream):
    return stream.operator_and([
        Matcher_Parser_123,
        Matcher_Parser_125,
        Matcher_Parser_127,
        Matcher_Parser_128
    ])
def Matcher_Parser_130(stream):
    return stream.with_scope(Matcher_Parser_129)
def Matcher_Parser_131(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_132(stream):
    return stream.match(lambda item: item == '%', "'%'")
def Matcher_Parser_133(stream):
    return stream.operator_and([
        Matcher_Parser_132
    ])
def Matcher_Parser_134(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'MatchCallRule')
    ]))
def Matcher_Parser_135(stream):
    return stream.operator_and([
        Matcher_Parser_131,
        Matcher_Parser_133,
        Matcher_Parser_134
    ])
def Matcher_Parser_136(stream):
    return stream.with_scope(Matcher_Parser_135)
def Matcher_Parser_137(stream):
    return rules['Parser.expr2'](stream)
def Matcher_Parser_138(stream):
    return stream.operator_and([
        Matcher_Parser_137
    ])
def Matcher_Parser_139(stream):
    return stream.with_scope(Matcher_Parser_138)
def Matcher_Parser_140(stream):
    return stream.operator_or([
        Matcher_Parser_114,
        Matcher_Parser_122,
        Matcher_Parser_130,
        Matcher_Parser_136,
        Matcher_Parser_139
    ])
def Matcher_Parser_141(stream):
    return rules['Parser.name'](stream)
def Matcher_Parser_142(stream):
    return stream.bind('x', Matcher_Parser_141(stream))
def Matcher_Parser_143(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_144(stream):
    return stream.match(lambda item: item == '=', "'='")
def Matcher_Parser_145(stream):
    return stream.operator_and([
        Matcher_Parser_144
    ])
def Matcher_Parser_146(stream):
    return stream.operator_and([
        Matcher_Parser_143,
        Matcher_Parser_145
    ])
def Matcher_Parser_147(stream):
    return stream.with_scope(Matcher_Parser_146)
def Matcher_Parser_148(stream):
    return stream.operator_or([
        Matcher_Parser_147
    ])
def Matcher_Parser_149(stream):
    return stream.operator_not(Matcher_Parser_148)
def Matcher_Parser_150(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'MatchRule'),
        self.lookup('splice')(0, self.lookup('x'))
    ]))
def Matcher_Parser_151(stream):
    return stream.operator_and([
        Matcher_Parser_142,
        Matcher_Parser_149,
        Matcher_Parser_150
    ])
def Matcher_Parser_152(stream):
    return stream.with_scope(Matcher_Parser_151)
def Matcher_Parser_153(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_154(stream):
    return rules['Parser.char'](stream)
def Matcher_Parser_155(stream):
    return stream.bind('x', Matcher_Parser_154(stream))
def Matcher_Parser_156(stream):
    return stream.match(lambda item: item == '-', "'-'")
def Matcher_Parser_157(stream):
    return stream.operator_and([
        Matcher_Parser_156
    ])
def Matcher_Parser_158(stream):
    return rules['Parser.char'](stream)
def Matcher_Parser_159(stream):
    return stream.bind('y', Matcher_Parser_158(stream))
def Matcher_Parser_160(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'MatchObject'),
        self.lookup('splice')(0, self.lookup('concat')([
            self.lookup('splice')(0, 'Range'),
            self.lookup('splice')(0, self.lookup('x')),
            self.lookup('splice')(0, self.lookup('y'))
        ]))
    ]))
def Matcher_Parser_161(stream):
    return stream.operator_and([
        Matcher_Parser_153,
        Matcher_Parser_155,
        Matcher_Parser_157,
        Matcher_Parser_159,
        Matcher_Parser_160
    ])
def Matcher_Parser_162(stream):
    return stream.with_scope(Matcher_Parser_161)
def Matcher_Parser_163(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_164(stream):
    return stream.match(lambda item: item == "'", '"\'"')
def Matcher_Parser_165(stream):
    return stream.operator_and([
        Matcher_Parser_164
    ])
def Matcher_Parser_166(stream):
    return stream.match(lambda item: item == "'", '"\'"')
def Matcher_Parser_167(stream):
    return stream.operator_and([
        Matcher_Parser_166
    ])
def Matcher_Parser_168(stream):
    return stream.operator_not(Matcher_Parser_167)
def Matcher_Parser_169(stream):
    return rules['Parser.matchChar'](stream)
def Matcher_Parser_170(stream):
    return stream.operator_and([
        Matcher_Parser_168,
        Matcher_Parser_169
    ])
def Matcher_Parser_171(stream):
    return stream.with_scope(Matcher_Parser_170)
def Matcher_Parser_172(stream):
    return stream.operator_or([
        Matcher_Parser_171
    ])
def Matcher_Parser_173(stream):
    return stream.operator_star(Matcher_Parser_172)
def Matcher_Parser_174(stream):
    return stream.bind('xs', Matcher_Parser_173(stream))
def Matcher_Parser_175(stream):
    return stream.match(lambda item: item == "'", '"\'"')
def Matcher_Parser_176(stream):
    return stream.operator_and([
        Matcher_Parser_175
    ])
def Matcher_Parser_177(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'And'),
        self.lookup('splice')(1, self.lookup('xs'))
    ]))
def Matcher_Parser_178(stream):
    return stream.operator_and([
        Matcher_Parser_163,
        Matcher_Parser_165,
        Matcher_Parser_174,
        Matcher_Parser_176,
        Matcher_Parser_177
    ])
def Matcher_Parser_179(stream):
    return stream.with_scope(Matcher_Parser_178)
def Matcher_Parser_180(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_181(stream):
    return stream.match(lambda item: item == '.', "'.'")
def Matcher_Parser_182(stream):
    return stream.operator_and([
        Matcher_Parser_181
    ])
def Matcher_Parser_183(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'MatchObject'),
        self.lookup('splice')(0, self.lookup('concat')([
            self.lookup('splice')(0, 'Any')
        ]))
    ]))
def Matcher_Parser_184(stream):
    return stream.operator_and([
        Matcher_Parser_180,
        Matcher_Parser_182,
        Matcher_Parser_183
    ])
def Matcher_Parser_185(stream):
    return stream.with_scope(Matcher_Parser_184)
def Matcher_Parser_186(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_187(stream):
    return stream.match(lambda item: item == '(', "'('")
def Matcher_Parser_188(stream):
    return stream.operator_and([
        Matcher_Parser_187
    ])
def Matcher_Parser_189(stream):
    return rules['Parser.choice'](stream)
def Matcher_Parser_190(stream):
    return stream.bind('x', Matcher_Parser_189(stream))
def Matcher_Parser_191(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_192(stream):
    return stream.match(lambda item: item == ')', "')'")
def Matcher_Parser_193(stream):
    return stream.operator_and([
        Matcher_Parser_192
    ])
def Matcher_Parser_194(stream):
    return stream.action(lambda self: self.lookup('x'))
def Matcher_Parser_195(stream):
    return stream.operator_and([
        Matcher_Parser_186,
        Matcher_Parser_188,
        Matcher_Parser_190,
        Matcher_Parser_191,
        Matcher_Parser_193,
        Matcher_Parser_194
    ])
def Matcher_Parser_196(stream):
    return stream.with_scope(Matcher_Parser_195)
def Matcher_Parser_197(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_198(stream):
    return rules['Parser.number'](stream)
def Matcher_Parser_199(stream):
    return stream.bind('x', Matcher_Parser_198(stream))
def Matcher_Parser_200(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'MatchObject'),
        self.lookup('splice')(0, self.lookup('concat')([
            self.lookup('splice')(0, 'Eq'),
            self.lookup('splice')(0, self.lookup('x'))
        ]))
    ]))
def Matcher_Parser_201(stream):
    return stream.operator_and([
        Matcher_Parser_197,
        Matcher_Parser_199,
        Matcher_Parser_200
    ])
def Matcher_Parser_202(stream):
    return stream.with_scope(Matcher_Parser_201)
def Matcher_Parser_203(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_204(stream):
    return rules['Parser.string'](stream)
def Matcher_Parser_205(stream):
    return stream.bind('x', Matcher_Parser_204(stream))
def Matcher_Parser_206(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'MatchObject'),
        self.lookup('splice')(0, self.lookup('concat')([
            self.lookup('splice')(0, 'Eq'),
            self.lookup('splice')(0, self.lookup('x'))
        ]))
    ]))
def Matcher_Parser_207(stream):
    return stream.operator_and([
        Matcher_Parser_203,
        Matcher_Parser_205,
        Matcher_Parser_206
    ])
def Matcher_Parser_208(stream):
    return stream.with_scope(Matcher_Parser_207)
def Matcher_Parser_209(stream):
    return stream.operator_or([
        Matcher_Parser_152,
        Matcher_Parser_162,
        Matcher_Parser_179,
        Matcher_Parser_185,
        Matcher_Parser_196,
        Matcher_Parser_202,
        Matcher_Parser_208
    ])
def Matcher_Parser_210(stream):
    return rules['Parser.innerChar'](stream)
def Matcher_Parser_211(stream):
    return stream.bind('x', Matcher_Parser_210(stream))
def Matcher_Parser_212(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'MatchObject'),
        self.lookup('splice')(0, self.lookup('concat')([
            self.lookup('splice')(0, 'Eq'),
            self.lookup('splice')(0, self.lookup('x'))
        ]))
    ]))
def Matcher_Parser_213(stream):
    return stream.operator_and([
        Matcher_Parser_211,
        Matcher_Parser_212
    ])
def Matcher_Parser_214(stream):
    return stream.with_scope(Matcher_Parser_213)
def Matcher_Parser_215(stream):
    return stream.operator_or([
        Matcher_Parser_214
    ])
def Matcher_Parser_216(stream):
    return rules['Parser.actionExpr'](stream)
def Matcher_Parser_217(stream):
    return stream.bind('x', Matcher_Parser_216(stream))
def Matcher_Parser_218(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, self.lookup('concat')([
            self.lookup('splice')(0, 'Action'),
            self.lookup('splice')(0, self.lookup('x'))
        ]))
    ]))
def Matcher_Parser_219(stream):
    return stream.operator_and([
        Matcher_Parser_217,
        Matcher_Parser_218
    ])
def Matcher_Parser_220(stream):
    return stream.with_scope(Matcher_Parser_219)
def Matcher_Parser_221(stream):
    return stream.action(lambda self: self.lookup('concat')([
    
    ]))
def Matcher_Parser_222(stream):
    return stream.operator_and([
        Matcher_Parser_221
    ])
def Matcher_Parser_223(stream):
    return stream.with_scope(Matcher_Parser_222)
def Matcher_Parser_224(stream):
    return stream.operator_or([
        Matcher_Parser_220,
        Matcher_Parser_223
    ])
def Matcher_Parser_225(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_226(stream):
    return stream.match(lambda item: item == '-', "'-'")
def Matcher_Parser_227(stream):
    return stream.match(lambda item: item == '>', "'>'")
def Matcher_Parser_228(stream):
    return stream.operator_and([
        Matcher_Parser_226,
        Matcher_Parser_227
    ])
def Matcher_Parser_229(stream):
    return rules['Parser.hostExpr'](stream)
def Matcher_Parser_230(stream):
    return stream.bind('x', Matcher_Parser_229(stream))
def Matcher_Parser_231(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_232(stream):
    return stream.match(lambda item: item == ':', "':'")
def Matcher_Parser_233(stream):
    return stream.operator_and([
        Matcher_Parser_232
    ])
def Matcher_Parser_234(stream):
    return rules['Parser.name'](stream)
def Matcher_Parser_235(stream):
    return stream.operator_and([
        Matcher_Parser_231,
        Matcher_Parser_233,
        Matcher_Parser_234
    ])
def Matcher_Parser_236(stream):
    return stream.with_scope(Matcher_Parser_235)
def Matcher_Parser_237(stream):
    return stream.action(lambda self: '')
def Matcher_Parser_238(stream):
    return stream.operator_and([
        Matcher_Parser_237
    ])
def Matcher_Parser_239(stream):
    return stream.with_scope(Matcher_Parser_238)
def Matcher_Parser_240(stream):
    return stream.operator_or([
        Matcher_Parser_236,
        Matcher_Parser_239
    ])
def Matcher_Parser_241(stream):
    return stream.bind('y', Matcher_Parser_240(stream))
def Matcher_Parser_242(stream):
    return rules['Parser.actionExpr'](stream)
def Matcher_Parser_243(stream):
    return stream.bind('z', Matcher_Parser_242(stream))
def Matcher_Parser_244(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'Set'),
        self.lookup('splice')(0, self.lookup('y')),
        self.lookup('splice')(0, self.lookup('x')),
        self.lookup('splice')(0, self.lookup('z'))
    ]))
def Matcher_Parser_245(stream):
    return stream.operator_and([
        Matcher_Parser_225,
        Matcher_Parser_228,
        Matcher_Parser_230,
        Matcher_Parser_241,
        Matcher_Parser_243,
        Matcher_Parser_244
    ])
def Matcher_Parser_246(stream):
    return stream.with_scope(Matcher_Parser_245)
def Matcher_Parser_247(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_248(stream):
    return stream.match(lambda item: item == '-', "'-'")
def Matcher_Parser_249(stream):
    return stream.match(lambda item: item == '>', "'>'")
def Matcher_Parser_250(stream):
    return stream.operator_and([
        Matcher_Parser_248,
        Matcher_Parser_249
    ])
def Matcher_Parser_251(stream):
    return rules['Parser.hostExpr'](stream)
def Matcher_Parser_252(stream):
    return stream.operator_and([
        Matcher_Parser_247,
        Matcher_Parser_250,
        Matcher_Parser_251
    ])
def Matcher_Parser_253(stream):
    return stream.with_scope(Matcher_Parser_252)
def Matcher_Parser_254(stream):
    return stream.operator_or([
        Matcher_Parser_246,
        Matcher_Parser_253
    ])
def Matcher_Parser_255(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_256(stream):
    return rules['Parser.string'](stream)
def Matcher_Parser_257(stream):
    return stream.bind('x', Matcher_Parser_256(stream))
def Matcher_Parser_258(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'String'),
        self.lookup('splice')(0, self.lookup('x'))
    ]))
def Matcher_Parser_259(stream):
    return stream.operator_and([
        Matcher_Parser_255,
        Matcher_Parser_257,
        Matcher_Parser_258
    ])
def Matcher_Parser_260(stream):
    return stream.with_scope(Matcher_Parser_259)
def Matcher_Parser_261(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_262(stream):
    return rules['Parser.number'](stream)
def Matcher_Parser_263(stream):
    return stream.bind('x', Matcher_Parser_262(stream))
def Matcher_Parser_264(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'Number'),
        self.lookup('splice')(0, self.lookup('x'))
    ]))
def Matcher_Parser_265(stream):
    return stream.operator_and([
        Matcher_Parser_261,
        Matcher_Parser_263,
        Matcher_Parser_264
    ])
def Matcher_Parser_266(stream):
    return stream.with_scope(Matcher_Parser_265)
def Matcher_Parser_267(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_268(stream):
    return stream.match(lambda item: item == '[', "'['")
def Matcher_Parser_269(stream):
    return stream.operator_and([
        Matcher_Parser_268
    ])
def Matcher_Parser_270(stream):
    return rules['Parser.hostListItem'](stream)
def Matcher_Parser_271(stream):
    return stream.operator_star(Matcher_Parser_270)
def Matcher_Parser_272(stream):
    return stream.bind('xs', Matcher_Parser_271(stream))
def Matcher_Parser_273(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_274(stream):
    return stream.match(lambda item: item == ']', "']'")
def Matcher_Parser_275(stream):
    return stream.operator_and([
        Matcher_Parser_274
    ])
def Matcher_Parser_276(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'List'),
        self.lookup('splice')(1, self.lookup('xs'))
    ]))
def Matcher_Parser_277(stream):
    return stream.operator_and([
        Matcher_Parser_267,
        Matcher_Parser_269,
        Matcher_Parser_272,
        Matcher_Parser_273,
        Matcher_Parser_275,
        Matcher_Parser_276
    ])
def Matcher_Parser_278(stream):
    return stream.with_scope(Matcher_Parser_277)
def Matcher_Parser_279(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_280(stream):
    return stream.match(lambda item: item == '{', "'{'")
def Matcher_Parser_281(stream):
    return stream.operator_and([
        Matcher_Parser_280
    ])
def Matcher_Parser_282(stream):
    return rules['Parser.hostExpr'](stream)
def Matcher_Parser_283(stream):
    return stream.operator_star(Matcher_Parser_282)
def Matcher_Parser_284(stream):
    return stream.bind('xs', Matcher_Parser_283(stream))
def Matcher_Parser_285(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_286(stream):
    return stream.match(lambda item: item == '}', "'}'")
def Matcher_Parser_287(stream):
    return stream.operator_and([
        Matcher_Parser_286
    ])
def Matcher_Parser_288(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'Format'),
        self.lookup('splice')(1, self.lookup('xs'))
    ]))
def Matcher_Parser_289(stream):
    return stream.operator_and([
        Matcher_Parser_279,
        Matcher_Parser_281,
        Matcher_Parser_284,
        Matcher_Parser_285,
        Matcher_Parser_287,
        Matcher_Parser_288
    ])
def Matcher_Parser_290(stream):
    return stream.with_scope(Matcher_Parser_289)
def Matcher_Parser_291(stream):
    return rules['Parser.var'](stream)
def Matcher_Parser_292(stream):
    return stream.bind('x', Matcher_Parser_291(stream))
def Matcher_Parser_293(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_294(stream):
    return stream.match(lambda item: item == '(', "'('")
def Matcher_Parser_295(stream):
    return stream.operator_and([
        Matcher_Parser_294
    ])
def Matcher_Parser_296(stream):
    return rules['Parser.hostExpr'](stream)
def Matcher_Parser_297(stream):
    return stream.operator_star(Matcher_Parser_296)
def Matcher_Parser_298(stream):
    return stream.bind('ys', Matcher_Parser_297(stream))
def Matcher_Parser_299(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_300(stream):
    return stream.match(lambda item: item == ')', "')'")
def Matcher_Parser_301(stream):
    return stream.operator_and([
        Matcher_Parser_300
    ])
def Matcher_Parser_302(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'Call'),
        self.lookup('splice')(0, self.lookup('x')),
        self.lookup('splice')(1, self.lookup('ys'))
    ]))
def Matcher_Parser_303(stream):
    return stream.operator_and([
        Matcher_Parser_292,
        Matcher_Parser_293,
        Matcher_Parser_295,
        Matcher_Parser_298,
        Matcher_Parser_299,
        Matcher_Parser_301,
        Matcher_Parser_302
    ])
def Matcher_Parser_304(stream):
    return stream.with_scope(Matcher_Parser_303)
def Matcher_Parser_305(stream):
    return rules['Parser.var'](stream)
def Matcher_Parser_306(stream):
    return stream.operator_and([
        Matcher_Parser_305
    ])
def Matcher_Parser_307(stream):
    return stream.with_scope(Matcher_Parser_306)
def Matcher_Parser_308(stream):
    return stream.operator_or([
        Matcher_Parser_260,
        Matcher_Parser_266,
        Matcher_Parser_278,
        Matcher_Parser_290,
        Matcher_Parser_304,
        Matcher_Parser_307
    ])
def Matcher_Parser_309(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_310(stream):
    return stream.match(lambda item: item == '~', "'~'")
def Matcher_Parser_311(stream):
    return stream.operator_and([
        Matcher_Parser_310
    ])
def Matcher_Parser_312(stream):
    return stream.operator_star(Matcher_Parser_311)
def Matcher_Parser_313(stream):
    return stream.bind('ys', Matcher_Parser_312(stream))
def Matcher_Parser_314(stream):
    return rules['Parser.hostExpr'](stream)
def Matcher_Parser_315(stream):
    return stream.bind('x', Matcher_Parser_314(stream))
def Matcher_Parser_316(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'ListItem'),
        self.lookup('splice')(0, self.lookup('len')(
            self.lookup('ys')
        )),
        self.lookup('splice')(0, self.lookup('x'))
    ]))
def Matcher_Parser_317(stream):
    return stream.operator_and([
        Matcher_Parser_309,
        Matcher_Parser_313,
        Matcher_Parser_315,
        Matcher_Parser_316
    ])
def Matcher_Parser_318(stream):
    return stream.with_scope(Matcher_Parser_317)
def Matcher_Parser_319(stream):
    return stream.operator_or([
        Matcher_Parser_318
    ])
def Matcher_Parser_320(stream):
    return rules['Parser.name'](stream)
def Matcher_Parser_321(stream):
    return stream.bind('x', Matcher_Parser_320(stream))
def Matcher_Parser_322(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_323(stream):
    return stream.match(lambda item: item == '=', "'='")
def Matcher_Parser_324(stream):
    return stream.operator_and([
        Matcher_Parser_323
    ])
def Matcher_Parser_325(stream):
    return stream.operator_and([
        Matcher_Parser_322,
        Matcher_Parser_324
    ])
def Matcher_Parser_326(stream):
    return stream.with_scope(Matcher_Parser_325)
def Matcher_Parser_327(stream):
    return stream.operator_or([
        Matcher_Parser_326
    ])
def Matcher_Parser_328(stream):
    return stream.operator_not(Matcher_Parser_327)
def Matcher_Parser_329(stream):
    return stream.action(lambda self: self.lookup('concat')([
        self.lookup('splice')(0, 'Lookup'),
        self.lookup('splice')(0, self.lookup('x'))
    ]))
def Matcher_Parser_330(stream):
    return stream.operator_and([
        Matcher_Parser_321,
        Matcher_Parser_328,
        Matcher_Parser_329
    ])
def Matcher_Parser_331(stream):
    return stream.with_scope(Matcher_Parser_330)
def Matcher_Parser_332(stream):
    return stream.operator_or([
        Matcher_Parser_331
    ])
def Matcher_Parser_333(stream):
    return stream.match(lambda item: item == '"', '\'"\'')
def Matcher_Parser_334(stream):
    return stream.operator_and([
        Matcher_Parser_333
    ])
def Matcher_Parser_335(stream):
    return stream.match(lambda item: item == '"', '\'"\'')
def Matcher_Parser_336(stream):
    return stream.operator_and([
        Matcher_Parser_335
    ])
def Matcher_Parser_337(stream):
    return stream.operator_not(Matcher_Parser_336)
def Matcher_Parser_338(stream):
    return rules['Parser.innerChar'](stream)
def Matcher_Parser_339(stream):
    return stream.operator_and([
        Matcher_Parser_337,
        Matcher_Parser_338
    ])
def Matcher_Parser_340(stream):
    return stream.with_scope(Matcher_Parser_339)
def Matcher_Parser_341(stream):
    return stream.operator_or([
        Matcher_Parser_340
    ])
def Matcher_Parser_342(stream):
    return stream.operator_star(Matcher_Parser_341)
def Matcher_Parser_343(stream):
    return stream.bind('xs', Matcher_Parser_342(stream))
def Matcher_Parser_344(stream):
    return stream.match(lambda item: item == '"', '\'"\'')
def Matcher_Parser_345(stream):
    return stream.operator_and([
        Matcher_Parser_344
    ])
def Matcher_Parser_346(stream):
    return stream.action(lambda self: self.lookup('join')([
        self.lookup('xs')
    ]))
def Matcher_Parser_347(stream):
    return stream.operator_and([
        Matcher_Parser_334,
        Matcher_Parser_343,
        Matcher_Parser_345,
        Matcher_Parser_346
    ])
def Matcher_Parser_348(stream):
    return stream.with_scope(Matcher_Parser_347)
def Matcher_Parser_349(stream):
    return stream.operator_or([
        Matcher_Parser_348
    ])
def Matcher_Parser_350(stream):
    return stream.match(lambda item: item == "'", '"\'"')
def Matcher_Parser_351(stream):
    return stream.operator_and([
        Matcher_Parser_350
    ])
def Matcher_Parser_352(stream):
    return stream.match(lambda item: item == "'", '"\'"')
def Matcher_Parser_353(stream):
    return stream.operator_and([
        Matcher_Parser_352
    ])
def Matcher_Parser_354(stream):
    return stream.operator_not(Matcher_Parser_353)
def Matcher_Parser_355(stream):
    return rules['Parser.innerChar'](stream)
def Matcher_Parser_356(stream):
    return stream.bind('x', Matcher_Parser_355(stream))
def Matcher_Parser_357(stream):
    return stream.match(lambda item: item == "'", '"\'"')
def Matcher_Parser_358(stream):
    return stream.operator_and([
        Matcher_Parser_357
    ])
def Matcher_Parser_359(stream):
    return stream.action(lambda self: self.lookup('x'))
def Matcher_Parser_360(stream):
    return stream.operator_and([
        Matcher_Parser_351,
        Matcher_Parser_354,
        Matcher_Parser_356,
        Matcher_Parser_358,
        Matcher_Parser_359
    ])
def Matcher_Parser_361(stream):
    return stream.with_scope(Matcher_Parser_360)
def Matcher_Parser_362(stream):
    return stream.operator_or([
        Matcher_Parser_361
    ])
def Matcher_Parser_363(stream):
    return stream.match(lambda item: item == '\\', "'\\\\'")
def Matcher_Parser_364(stream):
    return stream.operator_and([
        Matcher_Parser_363
    ])
def Matcher_Parser_365(stream):
    return rules['Parser.escape'](stream)
def Matcher_Parser_366(stream):
    return stream.operator_and([
        Matcher_Parser_364,
        Matcher_Parser_365
    ])
def Matcher_Parser_367(stream):
    return stream.with_scope(Matcher_Parser_366)
def Matcher_Parser_368(stream):
    return stream.match(lambda item: True, 'any')
def Matcher_Parser_369(stream):
    return stream.operator_and([
        Matcher_Parser_368
    ])
def Matcher_Parser_370(stream):
    return stream.with_scope(Matcher_Parser_369)
def Matcher_Parser_371(stream):
    return stream.operator_or([
        Matcher_Parser_367,
        Matcher_Parser_370
    ])
def Matcher_Parser_372(stream):
    return stream.match(lambda item: item == '\\', "'\\\\'")
def Matcher_Parser_373(stream):
    return stream.operator_and([
        Matcher_Parser_372
    ])
def Matcher_Parser_374(stream):
    return stream.action(lambda self: '\\')
def Matcher_Parser_375(stream):
    return stream.operator_and([
        Matcher_Parser_373,
        Matcher_Parser_374
    ])
def Matcher_Parser_376(stream):
    return stream.with_scope(Matcher_Parser_375)
def Matcher_Parser_377(stream):
    return stream.match(lambda item: item == "'", '"\'"')
def Matcher_Parser_378(stream):
    return stream.operator_and([
        Matcher_Parser_377
    ])
def Matcher_Parser_379(stream):
    return stream.action(lambda self: "'")
def Matcher_Parser_380(stream):
    return stream.operator_and([
        Matcher_Parser_378,
        Matcher_Parser_379
    ])
def Matcher_Parser_381(stream):
    return stream.with_scope(Matcher_Parser_380)
def Matcher_Parser_382(stream):
    return stream.match(lambda item: item == '"', '\'"\'')
def Matcher_Parser_383(stream):
    return stream.operator_and([
        Matcher_Parser_382
    ])
def Matcher_Parser_384(stream):
    return stream.action(lambda self: '"')
def Matcher_Parser_385(stream):
    return stream.operator_and([
        Matcher_Parser_383,
        Matcher_Parser_384
    ])
def Matcher_Parser_386(stream):
    return stream.with_scope(Matcher_Parser_385)
def Matcher_Parser_387(stream):
    return stream.match(lambda item: item == 'n', "'n'")
def Matcher_Parser_388(stream):
    return stream.operator_and([
        Matcher_Parser_387
    ])
def Matcher_Parser_389(stream):
    return stream.action(lambda self: '\n')
def Matcher_Parser_390(stream):
    return stream.operator_and([
        Matcher_Parser_388,
        Matcher_Parser_389
    ])
def Matcher_Parser_391(stream):
    return stream.with_scope(Matcher_Parser_390)
def Matcher_Parser_392(stream):
    return stream.operator_or([
        Matcher_Parser_376,
        Matcher_Parser_381,
        Matcher_Parser_386,
        Matcher_Parser_391
    ])
def Matcher_Parser_393(stream):
    return stream.match(lambda item: '0' <= item <= '9', "'0'-'9'")
def Matcher_Parser_394(stream):
    return stream.bind('x', Matcher_Parser_393(stream))
def Matcher_Parser_395(stream):
    return stream.match(lambda item: '0' <= item <= '9', "'0'-'9'")
def Matcher_Parser_396(stream):
    return stream.operator_star(Matcher_Parser_395)
def Matcher_Parser_397(stream):
    return stream.bind('xs', Matcher_Parser_396(stream))
def Matcher_Parser_398(stream):
    return stream.action(lambda self: self.lookup('int')(
        self.lookup('join')([
            self.lookup('x'),
            self.lookup('xs')
        ])
    ))
def Matcher_Parser_399(stream):
    return stream.operator_and([
        Matcher_Parser_394,
        Matcher_Parser_397,
        Matcher_Parser_398
    ])
def Matcher_Parser_400(stream):
    return stream.with_scope(Matcher_Parser_399)
def Matcher_Parser_401(stream):
    return stream.operator_or([
        Matcher_Parser_400
    ])
def Matcher_Parser_402(stream):
    return rules['Parser.space'](stream)
def Matcher_Parser_403(stream):
    return rules['Parser.nameStart'](stream)
def Matcher_Parser_404(stream):
    return stream.bind('x', Matcher_Parser_403(stream))
def Matcher_Parser_405(stream):
    return rules['Parser.nameChar'](stream)
def Matcher_Parser_406(stream):
    return stream.operator_star(Matcher_Parser_405)
def Matcher_Parser_407(stream):
    return stream.bind('xs', Matcher_Parser_406(stream))
def Matcher_Parser_408(stream):
    return stream.action(lambda self: self.lookup('join')([
        self.lookup('x'),
        self.lookup('xs')
    ]))
def Matcher_Parser_409(stream):
    return stream.operator_and([
        Matcher_Parser_402,
        Matcher_Parser_404,
        Matcher_Parser_407,
        Matcher_Parser_408
    ])
def Matcher_Parser_410(stream):
    return stream.with_scope(Matcher_Parser_409)
def Matcher_Parser_411(stream):
    return stream.operator_or([
        Matcher_Parser_410
    ])
def Matcher_Parser_412(stream):
    return stream.match(lambda item: 'a' <= item <= 'z', "'a'-'z'")
def Matcher_Parser_413(stream):
    return stream.operator_and([
        Matcher_Parser_412
    ])
def Matcher_Parser_414(stream):
    return stream.with_scope(Matcher_Parser_413)
def Matcher_Parser_415(stream):
    return stream.match(lambda item: 'A' <= item <= 'Z', "'A'-'Z'")
def Matcher_Parser_416(stream):
    return stream.operator_and([
        Matcher_Parser_415
    ])
def Matcher_Parser_417(stream):
    return stream.with_scope(Matcher_Parser_416)
def Matcher_Parser_418(stream):
    return stream.operator_or([
        Matcher_Parser_414,
        Matcher_Parser_417
    ])
def Matcher_Parser_419(stream):
    return stream.match(lambda item: 'a' <= item <= 'z', "'a'-'z'")
def Matcher_Parser_420(stream):
    return stream.operator_and([
        Matcher_Parser_419
    ])
def Matcher_Parser_421(stream):
    return stream.with_scope(Matcher_Parser_420)
def Matcher_Parser_422(stream):
    return stream.match(lambda item: 'A' <= item <= 'Z', "'A'-'Z'")
def Matcher_Parser_423(stream):
    return stream.operator_and([
        Matcher_Parser_422
    ])
def Matcher_Parser_424(stream):
    return stream.with_scope(Matcher_Parser_423)
def Matcher_Parser_425(stream):
    return stream.match(lambda item: '0' <= item <= '9', "'0'-'9'")
def Matcher_Parser_426(stream):
    return stream.operator_and([
        Matcher_Parser_425
    ])
def Matcher_Parser_427(stream):
    return stream.with_scope(Matcher_Parser_426)
def Matcher_Parser_428(stream):
    return stream.operator_or([
        Matcher_Parser_421,
        Matcher_Parser_424,
        Matcher_Parser_427
    ])
def Matcher_Parser_429(stream):
    return stream.match(lambda item: item == ' ', "' '")
def Matcher_Parser_430(stream):
    return stream.operator_and([
        Matcher_Parser_429
    ])
def Matcher_Parser_431(stream):
    return stream.operator_and([
        Matcher_Parser_430
    ])
def Matcher_Parser_432(stream):
    return stream.with_scope(Matcher_Parser_431)
def Matcher_Parser_433(stream):
    return stream.match(lambda item: item == '\n', "'\\n'")
def Matcher_Parser_434(stream):
    return stream.operator_and([
        Matcher_Parser_433
    ])
def Matcher_Parser_435(stream):
    return stream.operator_and([
        Matcher_Parser_434
    ])
def Matcher_Parser_436(stream):
    return stream.with_scope(Matcher_Parser_435)
def Matcher_Parser_437(stream):
    return stream.operator_or([
        Matcher_Parser_432,
        Matcher_Parser_436
    ])
def Matcher_Parser_438(stream):
    return stream.operator_star(Matcher_Parser_437)
def Matcher_Parser_439(stream):
    return stream.operator_and([
        Matcher_Parser_438
    ])
def Matcher_Parser_440(stream):
    return stream.with_scope(Matcher_Parser_439)
def Matcher_Parser_441(stream):
    return stream.operator_or([
        Matcher_Parser_440
    ])
rules['Parser.run'] = Matcher_Parser_8
rules['Parser.file'] = Matcher_Parser_22
rules['Parser.actor'] = Matcher_Parser_37
rules['Parser.rule'] = Matcher_Parser_48
rules['Parser.choice'] = Matcher_Parser_71
rules['Parser.sequence'] = Matcher_Parser_80
rules['Parser.expr'] = Matcher_Parser_106
rules['Parser.expr1'] = Matcher_Parser_140
rules['Parser.expr2'] = Matcher_Parser_209
rules['Parser.matchChar'] = Matcher_Parser_215
rules['Parser.maybeAction'] = Matcher_Parser_224
rules['Parser.actionExpr'] = Matcher_Parser_254
rules['Parser.hostExpr'] = Matcher_Parser_308
rules['Parser.hostListItem'] = Matcher_Parser_319
rules['Parser.var'] = Matcher_Parser_332
rules['Parser.string'] = Matcher_Parser_349
rules['Parser.char'] = Matcher_Parser_362
rules['Parser.innerChar'] = Matcher_Parser_371
rules['Parser.escape'] = Matcher_Parser_392
rules['Parser.number'] = Matcher_Parser_401
rules['Parser.name'] = Matcher_Parser_411
rules['Parser.nameStart'] = Matcher_Parser_418
rules['Parser.nameChar'] = Matcher_Parser_428
rules['Parser.space'] = Matcher_Parser_441
class Parser:
    def __init__(self):
        pass
    def run(self, stream):
        return rules['Parser.run'](stream)
def Matcher_CodeGenerator_0(stream):
    return stream.match(lambda item: item == 'Ast', "'Ast'")
def Matcher_CodeGenerator_1(stream):
    return rules['CodeGenerator.asts'](stream)
def Matcher_CodeGenerator_2(stream):
    return stream.bind('x', Matcher_CodeGenerator_1(stream))
def Matcher_CodeGenerator_3(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_2
    ])
def Matcher_CodeGenerator_4(stream):
    return stream.match_list(Matcher_CodeGenerator_3)
def Matcher_CodeGenerator_5(stream):
    return stream.action(lambda self: self.lookup('write')(
        self.lookup('x')
    ))
def Matcher_CodeGenerator_6(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_0,
        Matcher_CodeGenerator_4,
        Matcher_CodeGenerator_5
    ])
def Matcher_CodeGenerator_7(stream):
    return stream.with_scope(Matcher_CodeGenerator_6)
def Matcher_CodeGenerator_8(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_7
    ])
def Matcher_CodeGenerator_9(stream):
    return rules['CodeGenerator.ast'](stream)
def Matcher_CodeGenerator_10(stream):
    return stream.operator_star(Matcher_CodeGenerator_9)
def Matcher_CodeGenerator_11(stream):
    return stream.bind('xs', Matcher_CodeGenerator_10(stream))
def Matcher_CodeGenerator_12(stream):
    return stream.match(lambda item: True, 'any')
def Matcher_CodeGenerator_13(stream):
    return stream.operator_not(Matcher_CodeGenerator_12)
def Matcher_CodeGenerator_14(stream):
    return stream.action(lambda self: self.lookup('join')([
        self.lookup('xs')
    ]))
def Matcher_CodeGenerator_15(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_11,
        Matcher_CodeGenerator_13,
        Matcher_CodeGenerator_14
    ])
def Matcher_CodeGenerator_16(stream):
    return stream.with_scope(Matcher_CodeGenerator_15)
def Matcher_CodeGenerator_17(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_16
    ])
def Matcher_CodeGenerator_18(stream):
    return stream.match_call_rule('CodeGenerator')
def Matcher_CodeGenerator_19(stream):
    return stream.bind('x', Matcher_CodeGenerator_18(stream))
def Matcher_CodeGenerator_20(stream):
    return stream.match(lambda item: True, 'any')
def Matcher_CodeGenerator_21(stream):
    return stream.operator_not(Matcher_CodeGenerator_20)
def Matcher_CodeGenerator_22(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_19,
        Matcher_CodeGenerator_21
    ])
def Matcher_CodeGenerator_23(stream):
    return stream.match_list(Matcher_CodeGenerator_22)
def Matcher_CodeGenerator_24(stream):
    return stream.action(lambda self: self.lookup('x'))
def Matcher_CodeGenerator_25(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_23,
        Matcher_CodeGenerator_24
    ])
def Matcher_CodeGenerator_26(stream):
    return stream.with_scope(Matcher_CodeGenerator_25)
def Matcher_CodeGenerator_27(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_26
    ])
def Matcher_CodeGenerator_28(stream):
    return stream.match(lambda item: True, 'any')
def Matcher_CodeGenerator_29(stream):
    return stream.bind('x', Matcher_CodeGenerator_28(stream))
def Matcher_CodeGenerator_30(stream):
    return rules['CodeGenerator.ast'](stream)
def Matcher_CodeGenerator_31(stream):
    return stream.operator_star(Matcher_CodeGenerator_30)
def Matcher_CodeGenerator_32(stream):
    return stream.bind('ys', Matcher_CodeGenerator_31(stream))
def Matcher_CodeGenerator_33(stream):
    return stream.action(lambda self: self.bind('namespace', self.lookup('x'), lambda: self.bind('ids', self.lookup('concat')([
    
    ]), lambda: self.bind('matchers', self.lookup('concat')([
    
    ]), lambda: self.lookup('join')([
        self.lookup('matchers'),
        self.lookup('ys'),
        'class ',
        self.lookup('x'),
        ':\n',
        self.lookup('indent')(
            self.lookup('join')([
                'def __init__(self):\n',
                self.lookup('indent')(
                    self.lookup('join')([
                        'pass\n'
                    ])
                ),
                'def run(self, stream):\n',
                self.lookup('indent')(
                    self.lookup('join')([
                        "return rules['",
                        self.lookup('x'),
                        ".run'](stream)\n"
                    ])
                )
            ])
        )
    ])))))
def Matcher_CodeGenerator_34(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_29,
        Matcher_CodeGenerator_32,
        Matcher_CodeGenerator_33
    ])
def Matcher_CodeGenerator_35(stream):
    return stream.with_scope(Matcher_CodeGenerator_34)
def Matcher_CodeGenerator_36(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_35
    ])
def Matcher_CodeGenerator_37(stream):
    return stream.match(lambda item: True, 'any')
def Matcher_CodeGenerator_38(stream):
    return stream.bind('x', Matcher_CodeGenerator_37(stream))
def Matcher_CodeGenerator_39(stream):
    return rules['CodeGenerator.ast'](stream)
def Matcher_CodeGenerator_40(stream):
    return stream.bind('y', Matcher_CodeGenerator_39(stream))
def Matcher_CodeGenerator_41(stream):
    return stream.action(lambda self: self.lookup('join')([
        "rules['",
        self.lookup('namespace'),
        '.',
        self.lookup('x'),
        "'] = ",
        self.lookup('y'),
        '\n'
    ]))
def Matcher_CodeGenerator_42(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_38,
        Matcher_CodeGenerator_40,
        Matcher_CodeGenerator_41
    ])
def Matcher_CodeGenerator_43(stream):
    return stream.with_scope(Matcher_CodeGenerator_42)
def Matcher_CodeGenerator_44(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_43
    ])
def Matcher_CodeGenerator_45(stream):
    return rules['CodeGenerator.matcher'](stream)
def Matcher_CodeGenerator_46(stream):
    return stream.bind('m', Matcher_CodeGenerator_45(stream))
def Matcher_CodeGenerator_47(stream):
    return rules['CodeGenerator.astList'](stream)
def Matcher_CodeGenerator_48(stream):
    return stream.bind('x', Matcher_CodeGenerator_47(stream))
def Matcher_CodeGenerator_49(stream):
    return stream.action(lambda self: self.bind('body', self.lookup('join')([
        'stream.operator_or([',
        self.lookup('x'),
        '])'
    ]), lambda: self.lookup('m')))
def Matcher_CodeGenerator_50(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_46,
        Matcher_CodeGenerator_48,
        Matcher_CodeGenerator_49
    ])
def Matcher_CodeGenerator_51(stream):
    return stream.with_scope(Matcher_CodeGenerator_50)
def Matcher_CodeGenerator_52(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_51
    ])
def Matcher_CodeGenerator_53(stream):
    return rules['CodeGenerator.matcher'](stream)
def Matcher_CodeGenerator_54(stream):
    return stream.bind('m', Matcher_CodeGenerator_53(stream))
def Matcher_CodeGenerator_55(stream):
    return rules['CodeGenerator.ast'](stream)
def Matcher_CodeGenerator_56(stream):
    return stream.bind('x', Matcher_CodeGenerator_55(stream))
def Matcher_CodeGenerator_57(stream):
    return stream.action(lambda self: self.bind('body', self.lookup('join')([
        'stream.with_scope(',
        self.lookup('x'),
        ')'
    ]), lambda: self.lookup('m')))
def Matcher_CodeGenerator_58(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_54,
        Matcher_CodeGenerator_56,
        Matcher_CodeGenerator_57
    ])
def Matcher_CodeGenerator_59(stream):
    return stream.with_scope(Matcher_CodeGenerator_58)
def Matcher_CodeGenerator_60(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_59
    ])
def Matcher_CodeGenerator_61(stream):
    return rules['CodeGenerator.matcher'](stream)
def Matcher_CodeGenerator_62(stream):
    return stream.bind('m', Matcher_CodeGenerator_61(stream))
def Matcher_CodeGenerator_63(stream):
    return rules['CodeGenerator.astList'](stream)
def Matcher_CodeGenerator_64(stream):
    return stream.bind('x', Matcher_CodeGenerator_63(stream))
def Matcher_CodeGenerator_65(stream):
    return stream.action(lambda self: self.bind('body', self.lookup('join')([
        'stream.operator_and([',
        self.lookup('x'),
        '])'
    ]), lambda: self.lookup('m')))
def Matcher_CodeGenerator_66(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_62,
        Matcher_CodeGenerator_64,
        Matcher_CodeGenerator_65
    ])
def Matcher_CodeGenerator_67(stream):
    return stream.with_scope(Matcher_CodeGenerator_66)
def Matcher_CodeGenerator_68(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_67
    ])
def Matcher_CodeGenerator_69(stream):
    return rules['CodeGenerator.matcher'](stream)
def Matcher_CodeGenerator_70(stream):
    return stream.bind('m', Matcher_CodeGenerator_69(stream))
def Matcher_CodeGenerator_71(stream):
    return rules['CodeGenerator.repr'](stream)
def Matcher_CodeGenerator_72(stream):
    return stream.bind('x', Matcher_CodeGenerator_71(stream))
def Matcher_CodeGenerator_73(stream):
    return rules['CodeGenerator.ast'](stream)
def Matcher_CodeGenerator_74(stream):
    return stream.bind('y', Matcher_CodeGenerator_73(stream))
def Matcher_CodeGenerator_75(stream):
    return stream.action(lambda self: self.bind('body', self.lookup('join')([
        'stream.bind(',
        self.lookup('x'),
        ', ',
        self.lookup('y'),
        '(stream))'
    ]), lambda: self.lookup('m')))
def Matcher_CodeGenerator_76(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_70,
        Matcher_CodeGenerator_72,
        Matcher_CodeGenerator_74,
        Matcher_CodeGenerator_75
    ])
def Matcher_CodeGenerator_77(stream):
    return stream.with_scope(Matcher_CodeGenerator_76)
def Matcher_CodeGenerator_78(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_77
    ])
def Matcher_CodeGenerator_79(stream):
    return rules['CodeGenerator.matcher'](stream)
def Matcher_CodeGenerator_80(stream):
    return stream.bind('m', Matcher_CodeGenerator_79(stream))
def Matcher_CodeGenerator_81(stream):
    return rules['CodeGenerator.ast'](stream)
def Matcher_CodeGenerator_82(stream):
    return stream.bind('x', Matcher_CodeGenerator_81(stream))
def Matcher_CodeGenerator_83(stream):
    return stream.action(lambda self: self.bind('body', self.lookup('join')([
        'stream.operator_star(',
        self.lookup('x'),
        ')'
    ]), lambda: self.lookup('m')))
def Matcher_CodeGenerator_84(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_80,
        Matcher_CodeGenerator_82,
        Matcher_CodeGenerator_83
    ])
def Matcher_CodeGenerator_85(stream):
    return stream.with_scope(Matcher_CodeGenerator_84)
def Matcher_CodeGenerator_86(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_85
    ])
def Matcher_CodeGenerator_87(stream):
    return rules['CodeGenerator.matcher'](stream)
def Matcher_CodeGenerator_88(stream):
    return stream.bind('m', Matcher_CodeGenerator_87(stream))
def Matcher_CodeGenerator_89(stream):
    return rules['CodeGenerator.ast'](stream)
def Matcher_CodeGenerator_90(stream):
    return stream.bind('x', Matcher_CodeGenerator_89(stream))
def Matcher_CodeGenerator_91(stream):
    return stream.action(lambda self: self.bind('body', self.lookup('join')([
        'stream.operator_not(',
        self.lookup('x'),
        ')'
    ]), lambda: self.lookup('m')))
def Matcher_CodeGenerator_92(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_88,
        Matcher_CodeGenerator_90,
        Matcher_CodeGenerator_91
    ])
def Matcher_CodeGenerator_93(stream):
    return stream.with_scope(Matcher_CodeGenerator_92)
def Matcher_CodeGenerator_94(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_93
    ])
def Matcher_CodeGenerator_95(stream):
    return rules['CodeGenerator.matcher'](stream)
def Matcher_CodeGenerator_96(stream):
    return stream.bind('m', Matcher_CodeGenerator_95(stream))
def Matcher_CodeGenerator_97(stream):
    return stream.action(lambda self: self.bind('body', self.lookup('join')([
        "stream.match_call_rule('",
        self.lookup('namespace'),
        "')"
    ]), lambda: self.lookup('m')))
def Matcher_CodeGenerator_98(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_96,
        Matcher_CodeGenerator_97
    ])
def Matcher_CodeGenerator_99(stream):
    return stream.with_scope(Matcher_CodeGenerator_98)
def Matcher_CodeGenerator_100(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_99
    ])
def Matcher_CodeGenerator_101(stream):
    return rules['CodeGenerator.matcher'](stream)
def Matcher_CodeGenerator_102(stream):
    return stream.bind('m', Matcher_CodeGenerator_101(stream))
def Matcher_CodeGenerator_103(stream):
    return stream.match(lambda item: True, 'any')
def Matcher_CodeGenerator_104(stream):
    return stream.bind('x', Matcher_CodeGenerator_103(stream))
def Matcher_CodeGenerator_105(stream):
    return stream.action(lambda self: self.bind('body', self.lookup('join')([
        "rules['",
        self.lookup('namespace'),
        '.',
        self.lookup('x'),
        "'](stream)"
    ]), lambda: self.lookup('m')))
def Matcher_CodeGenerator_106(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_102,
        Matcher_CodeGenerator_104,
        Matcher_CodeGenerator_105
    ])
def Matcher_CodeGenerator_107(stream):
    return stream.with_scope(Matcher_CodeGenerator_106)
def Matcher_CodeGenerator_108(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_107
    ])
def Matcher_CodeGenerator_109(stream):
    return rules['CodeGenerator.matcher'](stream)
def Matcher_CodeGenerator_110(stream):
    return stream.bind('m', Matcher_CodeGenerator_109(stream))
def Matcher_CodeGenerator_111(stream):
    return rules['CodeGenerator.ast'](stream)
def Matcher_CodeGenerator_112(stream):
    return stream.bind('x', Matcher_CodeGenerator_111(stream))
def Matcher_CodeGenerator_113(stream):
    return stream.action(lambda self: self.bind('body', self.lookup('join')([
        'stream.match(lambda item: ',
        self.lookup('x'),
        ')'
    ]), lambda: self.lookup('m')))
def Matcher_CodeGenerator_114(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_110,
        Matcher_CodeGenerator_112,
        Matcher_CodeGenerator_113
    ])
def Matcher_CodeGenerator_115(stream):
    return stream.with_scope(Matcher_CodeGenerator_114)
def Matcher_CodeGenerator_116(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_115
    ])
def Matcher_CodeGenerator_117(stream):
    return rules['CodeGenerator.matcher'](stream)
def Matcher_CodeGenerator_118(stream):
    return stream.bind('m', Matcher_CodeGenerator_117(stream))
def Matcher_CodeGenerator_119(stream):
    return rules['CodeGenerator.ast'](stream)
def Matcher_CodeGenerator_120(stream):
    return stream.bind('x', Matcher_CodeGenerator_119(stream))
def Matcher_CodeGenerator_121(stream):
    return stream.action(lambda self: self.bind('body', self.lookup('join')([
        'stream.match_list(',
        self.lookup('x'),
        ')'
    ]), lambda: self.lookup('m')))
def Matcher_CodeGenerator_122(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_118,
        Matcher_CodeGenerator_120,
        Matcher_CodeGenerator_121
    ])
def Matcher_CodeGenerator_123(stream):
    return stream.with_scope(Matcher_CodeGenerator_122)
def Matcher_CodeGenerator_124(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_123
    ])
def Matcher_CodeGenerator_125(stream):
    return rules['CodeGenerator.matcher'](stream)
def Matcher_CodeGenerator_126(stream):
    return stream.bind('m', Matcher_CodeGenerator_125(stream))
def Matcher_CodeGenerator_127(stream):
    return rules['CodeGenerator.ast'](stream)
def Matcher_CodeGenerator_128(stream):
    return stream.bind('x', Matcher_CodeGenerator_127(stream))
def Matcher_CodeGenerator_129(stream):
    return stream.action(lambda self: self.bind('body', self.lookup('join')([
        'stream.action(lambda self: ',
        self.lookup('x'),
        ')'
    ]), lambda: self.lookup('m')))
def Matcher_CodeGenerator_130(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_126,
        Matcher_CodeGenerator_128,
        Matcher_CodeGenerator_129
    ])
def Matcher_CodeGenerator_131(stream):
    return stream.with_scope(Matcher_CodeGenerator_130)
def Matcher_CodeGenerator_132(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_131
    ])
def Matcher_CodeGenerator_133(stream):
    return stream.action(lambda self: self.lookup('join')([
        'True',
        ", 'any'"
    ]))
def Matcher_CodeGenerator_134(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_133
    ])
def Matcher_CodeGenerator_135(stream):
    return stream.with_scope(Matcher_CodeGenerator_134)
def Matcher_CodeGenerator_136(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_135
    ])
def Matcher_CodeGenerator_137(stream):
    return rules['CodeGenerator.repr'](stream)
def Matcher_CodeGenerator_138(stream):
    return stream.bind('x', Matcher_CodeGenerator_137(stream))
def Matcher_CodeGenerator_139(stream):
    return stream.action(lambda self: self.lookup('join')([
        'item == ',
        self.lookup('x'),
        ', ',
        self.lookup('repr')(
            self.lookup('x')
        )
    ]))
def Matcher_CodeGenerator_140(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_138,
        Matcher_CodeGenerator_139
    ])
def Matcher_CodeGenerator_141(stream):
    return stream.with_scope(Matcher_CodeGenerator_140)
def Matcher_CodeGenerator_142(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_141
    ])
def Matcher_CodeGenerator_143(stream):
    return rules['CodeGenerator.repr'](stream)
def Matcher_CodeGenerator_144(stream):
    return stream.bind('x', Matcher_CodeGenerator_143(stream))
def Matcher_CodeGenerator_145(stream):
    return rules['CodeGenerator.repr'](stream)
def Matcher_CodeGenerator_146(stream):
    return stream.bind('y', Matcher_CodeGenerator_145(stream))
def Matcher_CodeGenerator_147(stream):
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
def Matcher_CodeGenerator_148(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_144,
        Matcher_CodeGenerator_146,
        Matcher_CodeGenerator_147
    ])
def Matcher_CodeGenerator_149(stream):
    return stream.with_scope(Matcher_CodeGenerator_148)
def Matcher_CodeGenerator_150(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_149
    ])
def Matcher_CodeGenerator_151(stream):
    return rules['CodeGenerator.repr'](stream)
def Matcher_CodeGenerator_152(stream):
    return stream.bind('x', Matcher_CodeGenerator_151(stream))
def Matcher_CodeGenerator_153(stream):
    return rules['CodeGenerator.ast'](stream)
def Matcher_CodeGenerator_154(stream):
    return stream.bind('y', Matcher_CodeGenerator_153(stream))
def Matcher_CodeGenerator_155(stream):
    return rules['CodeGenerator.ast'](stream)
def Matcher_CodeGenerator_156(stream):
    return stream.bind('z', Matcher_CodeGenerator_155(stream))
def Matcher_CodeGenerator_157(stream):
    return stream.action(lambda self: self.lookup('join')([
        'self.bind(',
        self.lookup('x'),
        ', ',
        self.lookup('y'),
        ', lambda: ',
        self.lookup('z'),
        ')'
    ]))
def Matcher_CodeGenerator_158(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_152,
        Matcher_CodeGenerator_154,
        Matcher_CodeGenerator_156,
        Matcher_CodeGenerator_157
    ])
def Matcher_CodeGenerator_159(stream):
    return stream.with_scope(Matcher_CodeGenerator_158)
def Matcher_CodeGenerator_160(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_159
    ])
def Matcher_CodeGenerator_161(stream):
    return rules['CodeGenerator.repr'](stream)
def Matcher_CodeGenerator_162(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_161
    ])
def Matcher_CodeGenerator_163(stream):
    return stream.with_scope(Matcher_CodeGenerator_162)
def Matcher_CodeGenerator_164(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_163
    ])
def Matcher_CodeGenerator_165(stream):
    return rules['CodeGenerator.repr'](stream)
def Matcher_CodeGenerator_166(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_165
    ])
def Matcher_CodeGenerator_167(stream):
    return stream.with_scope(Matcher_CodeGenerator_166)
def Matcher_CodeGenerator_168(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_167
    ])
def Matcher_CodeGenerator_169(stream):
    return rules['CodeGenerator.astList'](stream)
def Matcher_CodeGenerator_170(stream):
    return stream.bind('x', Matcher_CodeGenerator_169(stream))
def Matcher_CodeGenerator_171(stream):
    return stream.action(lambda self: self.lookup('join')([
        "self.lookup('concat')([",
        self.lookup('x'),
        '])'
    ]))
def Matcher_CodeGenerator_172(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_170,
        Matcher_CodeGenerator_171
    ])
def Matcher_CodeGenerator_173(stream):
    return stream.with_scope(Matcher_CodeGenerator_172)
def Matcher_CodeGenerator_174(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_173
    ])
def Matcher_CodeGenerator_175(stream):
    return rules['CodeGenerator.repr'](stream)
def Matcher_CodeGenerator_176(stream):
    return stream.bind('x', Matcher_CodeGenerator_175(stream))
def Matcher_CodeGenerator_177(stream):
    return rules['CodeGenerator.ast'](stream)
def Matcher_CodeGenerator_178(stream):
    return stream.bind('y', Matcher_CodeGenerator_177(stream))
def Matcher_CodeGenerator_179(stream):
    return stream.action(lambda self: self.lookup('join')([
        "self.lookup('splice')(",
        self.lookup('x'),
        ', ',
        self.lookup('y'),
        ')'
    ]))
def Matcher_CodeGenerator_180(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_176,
        Matcher_CodeGenerator_178,
        Matcher_CodeGenerator_179
    ])
def Matcher_CodeGenerator_181(stream):
    return stream.with_scope(Matcher_CodeGenerator_180)
def Matcher_CodeGenerator_182(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_181
    ])
def Matcher_CodeGenerator_183(stream):
    return rules['CodeGenerator.astList'](stream)
def Matcher_CodeGenerator_184(stream):
    return stream.bind('x', Matcher_CodeGenerator_183(stream))
def Matcher_CodeGenerator_185(stream):
    return stream.action(lambda self: self.lookup('join')([
        "self.lookup('join')([",
        self.lookup('x'),
        '])'
    ]))
def Matcher_CodeGenerator_186(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_184,
        Matcher_CodeGenerator_185
    ])
def Matcher_CodeGenerator_187(stream):
    return stream.with_scope(Matcher_CodeGenerator_186)
def Matcher_CodeGenerator_188(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_187
    ])
def Matcher_CodeGenerator_189(stream):
    return rules['CodeGenerator.ast'](stream)
def Matcher_CodeGenerator_190(stream):
    return stream.bind('x', Matcher_CodeGenerator_189(stream))
def Matcher_CodeGenerator_191(stream):
    return rules['CodeGenerator.astList'](stream)
def Matcher_CodeGenerator_192(stream):
    return stream.bind('y', Matcher_CodeGenerator_191(stream))
def Matcher_CodeGenerator_193(stream):
    return stream.action(lambda self: self.lookup('join')([
        self.lookup('x'),
        '(',
        self.lookup('y'),
        ')'
    ]))
def Matcher_CodeGenerator_194(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_190,
        Matcher_CodeGenerator_192,
        Matcher_CodeGenerator_193
    ])
def Matcher_CodeGenerator_195(stream):
    return stream.with_scope(Matcher_CodeGenerator_194)
def Matcher_CodeGenerator_196(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_195
    ])
def Matcher_CodeGenerator_197(stream):
    return rules['CodeGenerator.repr'](stream)
def Matcher_CodeGenerator_198(stream):
    return stream.bind('x', Matcher_CodeGenerator_197(stream))
def Matcher_CodeGenerator_199(stream):
    return stream.action(lambda self: self.lookup('join')([
        'self.lookup(',
        self.lookup('x'),
        ')'
    ]))
def Matcher_CodeGenerator_200(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_198,
        Matcher_CodeGenerator_199
    ])
def Matcher_CodeGenerator_201(stream):
    return stream.with_scope(Matcher_CodeGenerator_200)
def Matcher_CodeGenerator_202(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_201
    ])
def Matcher_CodeGenerator_203(stream):
    return rules['CodeGenerator.ast'](stream)
def Matcher_CodeGenerator_204(stream):
    return stream.operator_star(Matcher_CodeGenerator_203)
def Matcher_CodeGenerator_205(stream):
    return stream.bind('xs', Matcher_CodeGenerator_204(stream))
def Matcher_CodeGenerator_206(stream):
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
def Matcher_CodeGenerator_207(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_205,
        Matcher_CodeGenerator_206
    ])
def Matcher_CodeGenerator_208(stream):
    return stream.with_scope(Matcher_CodeGenerator_207)
def Matcher_CodeGenerator_209(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_208
    ])
def Matcher_CodeGenerator_210(stream):
    return stream.action(lambda self: self.bind('id', self.lookup('join')([
        'Matcher_',
        self.lookup('namespace'),
        '_',
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
            '(stream):\n',
            self.lookup('indent')(
                self.lookup('join')([
                    'return ',
                    self.lookup('body'),
                    '\n'
                ])
            )
        ])
    ), lambda: self.lookup('join')([
        self.lookup('id')
    ])))))
def Matcher_CodeGenerator_211(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_210
    ])
def Matcher_CodeGenerator_212(stream):
    return stream.with_scope(Matcher_CodeGenerator_211)
def Matcher_CodeGenerator_213(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_212
    ])
def Matcher_CodeGenerator_214(stream):
    return stream.match(lambda item: True, 'any')
def Matcher_CodeGenerator_215(stream):
    return stream.bind('x', Matcher_CodeGenerator_214(stream))
def Matcher_CodeGenerator_216(stream):
    return stream.action(lambda self: self.lookup('repr')(
        self.lookup('x')
    ))
def Matcher_CodeGenerator_217(stream):
    return stream.operator_and([
        Matcher_CodeGenerator_215,
        Matcher_CodeGenerator_216
    ])
def Matcher_CodeGenerator_218(stream):
    return stream.with_scope(Matcher_CodeGenerator_217)
def Matcher_CodeGenerator_219(stream):
    return stream.operator_or([
        Matcher_CodeGenerator_218
    ])
rules['CodeGenerator.run'] = Matcher_CodeGenerator_8
rules['CodeGenerator.asts'] = Matcher_CodeGenerator_17
rules['CodeGenerator.ast'] = Matcher_CodeGenerator_27
rules['CodeGenerator.Actor'] = Matcher_CodeGenerator_36
rules['CodeGenerator.Rule'] = Matcher_CodeGenerator_44
rules['CodeGenerator.Or'] = Matcher_CodeGenerator_52
rules['CodeGenerator.Scope'] = Matcher_CodeGenerator_60
rules['CodeGenerator.And'] = Matcher_CodeGenerator_68
rules['CodeGenerator.Bind'] = Matcher_CodeGenerator_78
rules['CodeGenerator.Star'] = Matcher_CodeGenerator_86
rules['CodeGenerator.Not'] = Matcher_CodeGenerator_94
rules['CodeGenerator.MatchCallRule'] = Matcher_CodeGenerator_100
rules['CodeGenerator.MatchRule'] = Matcher_CodeGenerator_108
rules['CodeGenerator.MatchObject'] = Matcher_CodeGenerator_116
rules['CodeGenerator.MatchList'] = Matcher_CodeGenerator_124
rules['CodeGenerator.Action'] = Matcher_CodeGenerator_132
rules['CodeGenerator.Any'] = Matcher_CodeGenerator_136
rules['CodeGenerator.Eq'] = Matcher_CodeGenerator_142
rules['CodeGenerator.Range'] = Matcher_CodeGenerator_150
rules['CodeGenerator.Set'] = Matcher_CodeGenerator_160
rules['CodeGenerator.String'] = Matcher_CodeGenerator_164
rules['CodeGenerator.Number'] = Matcher_CodeGenerator_168
rules['CodeGenerator.List'] = Matcher_CodeGenerator_174
rules['CodeGenerator.ListItem'] = Matcher_CodeGenerator_182
rules['CodeGenerator.Format'] = Matcher_CodeGenerator_188
rules['CodeGenerator.Call'] = Matcher_CodeGenerator_196
rules['CodeGenerator.Lookup'] = Matcher_CodeGenerator_202
rules['CodeGenerator.astList'] = Matcher_CodeGenerator_209
rules['CodeGenerator.matcher'] = Matcher_CodeGenerator_213
rules['CodeGenerator.repr'] = Matcher_CodeGenerator_219
class CodeGenerator:
    def __init__(self):
        pass
    def run(self, stream):
        return rules['CodeGenerator.run'](stream)
if __name__ == "__main__":
    #run_simulation(
    #    [
    #        Cli(),
    #        Parser(),
    #        CodeGenerator(),
    #    ],
    #    {
    #        "SUPPORT": SUPPORT,
    #    }
    #)
    import sys
    def read(path):
        if path == "-":
            return sys.stdin.read()
        with open(path) as f:
            return f.read()
    args = sys.argv[1:] or ["--compile", "-"]
    while args:
        command = args.pop(0)
        if command == "--support":
            sys.stdout.write(SUPPORT)
        elif command == "--copy":
            sys.stdout.write(read(args.pop(0)))
        elif command == "--embed":
            sys.stdout.write("{} = {}\n".format(
                args.pop(0),
                repr(read(args.pop(0)))
            ))
        elif command == "--compile":
            sys.stdout.write(compile_chain(
                ["Parser.file", "CodeGenerator.asts"],
                read(args.pop(0))
            ))
        else:
            sys.exit("ERROR: Unknown command '{}'".format(command))
