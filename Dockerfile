FROM python:3.13-slim

WORKDIR /workspace

CMD ["python", "-m", "unittest", "discover", "-s", "/workspace", "-p", "test_solution.py", "-v"]