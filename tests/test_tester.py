from agents.tester import test_code

code = """
def divide(a, b):
    return a / b
"""

result = test_code(code)

print(result)