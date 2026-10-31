import os
import ast

def test_code(code, task, generated_tests=None):
    try:
        ast.parse(code)

        return {
            "generated_tests": "",
            "passed": True,
            "report": "Syntax is valid. Unit tests were NOT executed in cloud mode.",
            "exit_code": 0,
            "test_count": 0
        }

    except SyntaxError as error:
        return {
            "generated_tests": "",
            "passed": False,
            "report": f"Syntax error at line {error.lineno}: {error.msg}. Unit tests were NOT executed.",
            "exit_code": 1,
            "test_count": 0
        }
