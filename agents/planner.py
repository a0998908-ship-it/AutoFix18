import os
from google import genai


def create_plan(task):

    client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY")
    )

    prompt = f"""
    You are a software engineering project planner.

    Break the following coding task into
    5 clear and simple steps.

    Task: {task}
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text