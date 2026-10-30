import os
import re
import tempfile
import subprocess
from pathlib import Path

from google import genai


def extract_python_code(response_text):
    match = re.search(
        r"```(?:python)?\s*(.*?)```",
        response_text,
        re.DOTALL | re.IGNORECASE
    )

    if not match:
        raise ValueError(
            "Gemini did not return valid test code in a code block."
        )

    return match.group(1).strip()


def generate_tests(task, source_code):

    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY")
    )

    prompt = f"""
    You are an expert Python software testing engineer.

    USER TASK:
    {task}

    CODE TO TEST:
    {source_code}

    Generate Python unit tests using the unittest framework.

    Requirements:
    1. Test the expected behaviour described in the user task.
    2. Include normal cases and important edge cases.
    3. Import functions from solution.py.
    4. Use unittest.TestCase.
    5. Do not modify solution.py.
    6. Do not use network access or external services.
    7. Return only executable Python test code inside one
       ```python code block.

    The test file will be named test_solution.py.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return extract_python_code(response.text)


def execute_tests(code, generated_tests):

    with tempfile.TemporaryDirectory() as temp_dir:

        folder = Path(temp_dir)

        solution_file = folder / "solution.py"
        test_file = folder / "test_solution.py"

        solution_file.write_text(code, encoding="utf-8")
        test_file.write_text(generated_tests, encoding="utf-8")

        command = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "256m",
            "--cpus", "0.5",
            "--pids-limit", "64",
            "--read-only",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "--tmpfs", "/tmp:rw,noexec,nosuid,size=16m",
            "--mount",
            f"type=bind,source={folder.resolve()},target=/workspace,readonly",
            "--workdir", "/workspace",
            "--env", "PYTHONDONTWRITEBYTECODE=1",
            "autofix-sandbox",
            "python", "-m", "unittest",
            "discover", "-s", "/workspace",
            "-p", "test_solution.py", "-v"
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )

            output = result.stdout + "\n" + result.stderr

            match = re.search(
                r"Ran\s+(\d+)\s+tests?",
                output
            )

            test_count = int(match.group(1)) if match else 0

            passed = (
                result.returncode == 0
                and test_count > 0
            )

            return {
                "passed": passed,
                "output": output,
                "exit_code": result.returncode,
                "test_count": test_count
            }

        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "output": "Docker test execution timed out.",
                "exit_code": -1,
                "test_count": 0
            }

        except FileNotFoundError:
            raise RuntimeError(
                "Docker command not found. Check Docker Desktop."
            )


def test_code(code, task, generated_tests=None):

    if generated_tests is None:
        generated_tests = generate_tests(task, code)

    result = execute_tests(code, generated_tests)

    return {
        "generated_tests": generated_tests,
        "passed": result["passed"],
        "report": result["output"],
        "exit_code": result["exit_code"],
        "test_count": result["test_count"]
    }