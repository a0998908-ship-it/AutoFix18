import os
import re
from google import genai


def extract_python_code(response_text):
    match = re.search(
        r"```(?:python)?\s*(.*?)```",
        response_text,
        re.DOTALL | re.IGNORECASE
    )

    if not match:
        raise ValueError(
            "Gemini did not return code inside a Python code block."
        )

    return match.group(1).strip()


def improve_code(code, task, context="", feedback=""):

    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY")
    )

    prompt = f"""
    You are an expert Python software developer.

    USER TASK:
    {task}

    ORIGINAL CODE:
    {code}

    RELEVANT CODEBASE CONTEXT:
    {context}

    PREVIOUS TEST FEEDBACK:
    {feedback}

    Your responsibilities:
    1. Understand the intended behaviour.
    2. Find bugs and logical errors.
    3. Correct the code.
    4. Preserve the original functionality where possible.
    5. Do not invent unnecessary features.

    Return your answer in this exact format:

    ```python
    # Complete corrected Python code
    ```

    Explanation:
    Explain the bugs and the corrections you made.

    Return the complete code, not just the changed lines.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    corrected_code = extract_python_code(response.text)

    explanation = re.sub(
        r"```(?:python)?\s*.*?```",
        "",
        response.text,
        count=1,
        flags=re.DOTALL | re.IGNORECASE
    ).strip()

    return {
        "code": corrected_code,
        "explanation": explanation
    }