
import os
import re
import tempfile
import subprocess
from pathlib import Path

from google import genai


MODEL_NAME = "gemini-3.5-flash-lite"
DOCKER_IMAGE = "autofix-sandbox"
TEST_TIMEOUT = 30


def extract_python_code(response_text):

    match = re.search(
        r"```(?:python)?\s*(.*?)```",
        response_text,
        re.DOTALL | re.IGNORECASE
    )

    if not match:
        raise ValueError(
            "Gemini did not return valid Python code."
        )

    return match.group(1).strip()


def generate_tests(task, source_code):

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing.")

    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are an expert Python software testing engineer.

    USER TASK:
    {task}

    CODE TO TEST:
    {source_code}

    Generate Python unit tests using unittest.

    Requirements:
    1. Test expected behaviour.
    2. Include normal and edge cases.
    3. Import functions or variables from solution.py.
    4. Use unittest.TestCase.
    5. Do not modify solution.py.
    6. Do not use network access.
    7. Return complete executable Python tests
       inside one python code block.

    The test file will be named test_solution.py.
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return extract_python_code(response.text)


def execute_tests(code, generated_tests):

    with tempfile.TemporaryDirectory() as temp_dir:

        folder = Path(temp_dir)

        solution_file = folder / "solution.py"
        test_file = folder / "test_solution.py"

        solution_file.write_text(
            code,
            encoding="utf-8"
        )

        test_file.write_text(
            generated_tests,
            encoding="utf-8"
        )

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
            DOCKER_IMAGE,
            "python", "-m", "unittest",
            "discover", "-s", "/workspace",
            "-p", "test_solution.py", "-v"
        ]

        try:

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=TEST_TIMEOUT
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
                "Docker was not found. Check Docker Desktop."
            )


def test_code(code, task, generated_tests=None):

    if generated_tests is None:
        generated_tests = generate_tests(task, code)

    result = execute_tests(
        code,
        generated_tests
    )

    return {
        "generated_tests": generated_tests,
        "passed": result["passed"],
        "report": result["output"],
        "exit_code": result["exit_code"],
        "test_count": result["test_count"]
    }
