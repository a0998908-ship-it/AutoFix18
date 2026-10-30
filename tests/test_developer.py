from agents.developer import improve_code

code = """
def divide(a, b):
    return a / b
"""

task = "Fix the division by zero problem"

result = improve_code(code, task)

print(result)