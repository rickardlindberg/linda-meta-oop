#!/usr/bin/env python

import importlib
import os
import subprocess
import sys
import unittest

def make_next_version():
    final_compiler = meta_compile_rlmeta()
    test(final_compiler)
    mv(final_compiler, "rlmeta.py")

def meta_compile_rlmeta():
    compiler = "rlmeta.py"
    content = read(compiler)
    for i in range(4):
        next_compiler = "rlmeta{}.py".format(i+1)
        next_content = compile_rlmeta(compiler)
        log("Writing {}".format(next_compiler))
        write(next_compiler, next_content)
        if next_content == content:
            return next_compiler
        compiler = next_compiler
        content = next_content
    fail("Unable to produce metacompiler.")

def compile_rlmeta(rlmeta):
    log("Compiling rlmeta using {}".format(rlmeta))
    return run_rlmeta(rlmeta, [
        "--support",
        "--embed", "SUPPORT", "src/support.py",
        "--compile", "src/cli.rlmeta",
        "--compile", "src/parser.rlmeta",
        "--compile", "src/optimizer.rlmeta",
        "--compile", "src/codegenerator.rlmeta",
        "--compile", "src/stdlib.rlmeta",
        "--main",
    ])

def test(rlmeta):
    log("Test: Has its own support library")
    assert run_rlmeta(rlmeta, ["--support"]) == read("src/support.py")
    log("Test: Disallow semantic action in the middle")
    run_rlmeta(rlmeta, [], b"actor Grammar = . -> [] .", expect_failure=True)
    log("Test: Call unknown rule foo")
    assert test_grammar(
        rlmeta,
        b"actor Grammar = % | .:x -> print(x)",
        b"run_simulation(actors=[Grammar()], messages=[['foo']], extra={'print': print})"
    ) == b"foo\n"
    log("Test: unittest")
    global rlmeta_module
    rlmeta_module = importlib.import_module(rlmeta[:-3])
    if not unittest.main(exit=False).result.wasSuccessful():
        sys.exit(1)

def test_grammar(rlmeta, grammar, main_code):
    compiled = run_rlmeta(rlmeta, ["--support", "--compile", "-"], grammar)
    total = compiled + main_code
    process = subprocess.Popen(
        ["python"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    stdout, _ = process.communicate(total)
    return stdout

def run_rlmeta(rlmeta, args, stdin=b"", expect_failure=False):
    process = subprocess.Popen(
        ["python", rlmeta]+args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    stdout, _ = process.communicate(stdin)
    if expect_failure:
        if process.returncode == 0:
            fail("Expected failure")
    else:
        if process.returncode != 0:
            fail("Expected success")
    return stdout

def mv(src, dest):
    log("Moving {} -> {}".format(src, dest))
    os.remove(dest)
    os.rename(src, dest)

def cleanup():
    for path in [
        "rlmeta1.py",
        "rlmeta2.py",
        "rlmeta3.py",
        "rlmeta4.py",
    ]:
        if os.path.exists(path):
            log("Deleting {}".format(path))
            os.remove(path)

def read(path):
    with open(path, "rb") as f:
        return f.read()

def write(path, content):
    with open(path, "wb") as f:
        return f.write(content)

def log(message):
    sys.stderr.write(color(f"{message}\n", "33"))

def success(message):
    sys.stderr.write(color(f"{message}\n", "32"))

def fail(message):
    sys.exit(color(f"ERROR: {message}", "31"))

def color(message, color):
    if os.isatty(sys.stderr.fileno()):
        return f"\033[0;{color}m{message}\033[0m"
    else:
        return message

class RlmetaTests(unittest.TestCase):

    def run_simulation(self, actors, messages):
        return rlmeta_module.run_simulation(
            actors=actors,
            messages=messages,
            fail=False
        )

    def test_parse_optimize_1(self):
        parsed_messages = self.run_simulation(
            [rlmeta_module.Parser()],
            [["SourceCode", 0, "actor Grammar = ^'hello'"]]
        )
        self.assertEqual(parsed_messages,
            [['Ast',
              0,
              [['Actor',
                'Grammar',
                [],
                ['Rule',
                 '_main',
                 ['Or',
                  ['Scope',
                   ['And',
                    ['And',
                     ['MatchRule', 'space'],
                     ['And',
                      ['MatchObject', ['Eq', 'h']],
                      ['MatchObject', ['Eq', 'e']],
                      ['MatchObject', ['Eq', 'l']],
                      ['MatchObject', ['Eq', 'l']],
                      ['MatchObject', ['Eq', 'o']]]]]]]],
                ]]]]
        )
        optimized_messages = self.run_simulation(
            [rlmeta_module.Optimizer()],
            parsed_messages
        )
        self.assertEqual(optimized_messages,
            [['Optimized',
              0,
              [['Actor',
                'Grammar',
                [],
                ['Rule',
                 '_main',
                 ['Scope',
                  ['And',
                   ['MatchRule', 'space'],
                   ['MatchObject', ['Eq', 'h']],
                   ['MatchObject', ['Eq', 'e']],
                   ['MatchObject', ['Eq', 'l']],
                   ['MatchObject', ['Eq', 'l']],
                   ['MatchObject', ['Eq', 'o']]]]],
                ]]]]
        )

    def test_parse_optimize_2(self):
        parsed_and_optimized = self.run_simulation(
            [rlmeta_module.Parser(), rlmeta_module.Optimizer()],
            [["SourceCode", 0, "actor Grammar = ('a' | 'b')*"]]
        )
        self.assertEqual(parsed_and_optimized,
            [['Optimized',
              0,
              [['Actor',
                'Grammar',
                [],
                ['Rule',
                 '_main',
                 ['Scope',
                  ['Star',
                   ['Or',
                    ['Scope', ['MatchObject', ['Eq', 'a']]],
                    ['Scope', ['MatchObject', ['Eq', 'b']]]]]]],
                ]]]]
        )

if __name__ == "__main__":
    cleanup()
    if sys.argv[1:] == ["--compile"]:
        sys.stdout.buffer.write(compile_rlmeta("rlmeta.py"))
    else:
        make_next_version()
    cleanup()
    success("  O-----------------O")
    success("  | RLMeta compiled |")
    success("~~|     itself!     |")
    success("  O-----------------O")
