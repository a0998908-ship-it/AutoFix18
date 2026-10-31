# ⚡ AutoFix — AI-Powered Code Debugging Assistant

AutoFix is an AI-assisted software debugging prototype that analyzes Python code, identifies potential issues, generates corrected code, and validates the proposed solution using automated unit tests inside Docker containers.

The project uses multiple specialized agents coordinated through LangGraph to create a structured debugging workflow.

## 🚀 Features

- **AI Planning:** Uses Gemini to understand the debugging task and generate a plan.
- **Code Analysis:** Uses Sentence Transformers embeddings and ChromaDB to retrieve relevant code context.
- **Code Improvement:** Generates corrected Python code and an explanation using Gemini.
- **Automated Testing:** Generates Python unit tests using `unittest`.
- **Docker Isolation:** Executes generated tests inside restricted Docker containers.
- **Conditional Retry:** Uses test feedback to request another code improvement when validation fails.
- **Interactive UI:** Provides a Streamlit interface for submitting code and viewing debugging results.

## 🏗️ Architecture

AutoFix follows a multi-agent workflow:

1. **Planner Agent** — Understands the user's task and creates a debugging plan.
2. **Code Analyst Agent** — Retrieves relevant code context using embeddings and ChromaDB.
3. **Developer Agent** — Generates improved code using Gemini.
4. **Tester Agent** — Generates unit tests and executes them inside Docker.
5. **Retry Mechanism** — If tests fail, the workflow can send the test feedback back to the Developer Agent for another attempt.

### Workflow

`User Input → Planner → Code Analyst → Developer → Tester`

- If tests pass, the workflow finishes.
- If tests fail and retry attempts remain, the Developer receives feedback and tries again.
- The workflow stops when tests pass or the retry limit is reached.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Google Gemini | Planning and code generation |
| LangGraph | Agent workflow orchestration |
| Sentence Transformers | Text and code embeddings |
| ChromaDB | Vector storage and retrieval |
| Streamlit | User interface |
| unittest | Automated test framework |
| Docker | Isolated test execution |

## 📁 Project Structure

```text
AutoFix/
│
├── agents/
│   ├── planner.py
│   ├── code_analyst.py
│   ├── developer.py
│   └── tester.py
│
├── core/
│   └── workflow.py
│
├── codebase/
│   └── calculator.py
│
├── sandbox/
├── tests/
├── data/
│
├── app.py
├── frontend.py
├── requirements.txt
├── Dockerfile
└── .gitignore
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/a0998908-ship-it/AutoFix18.git
cd AutoFix18
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
```

Never upload your actual API key to GitHub.

### 5. Install and start Docker

Install Docker Desktop and make sure the Docker engine is running.

Verify Docker:

```bash
docker run hello-world
```

### 6. Run AutoFix

Start the Streamlit interface:

```bash
python -m streamlit run frontend.py
```

Open the local URL displayed in the terminal, usually:

`http://localhost:8501`

## 🧪 Example

Input code:

```python
arr = [1, 2, 3, 4, 5]

for i in range(len(arr)):
    print(arr[i + 1])
```

Task:

```text
Fix the IndexError. I want to print every element of the array.
```

AutoFix analyzes the task, retrieves code context, generates an improved solution, creates unit tests, and executes the tests in Docker.

The intended correction is:

```python
arr = [1, 2, 3, 4, 5]

for i in range(len(arr)):
    print(arr[i])
```

## ☁️ Deployment

AutoFix currently depends on a running Docker engine to execute generated tests.

For a complete deployment, the hosting environment must support:
- Python and the required packages.
- Access to the Gemini API.
- A working Docker engine accessible to the application.
- Sufficient memory and CPU for embeddings and test execution.

**Streamlit Community Cloud:** It can host Streamlit applications, but the current AutoFix testing workflow requires Docker access. Therefore, the full application cannot be deployed there unchanged. A UI-only demonstration would require a separate demo mode or a remote test-execution service.

For the complete workflow, use a cloud virtual machine or server where Docker is installed and accessible to the application. Protect the Docker environment and API credentials carefully.

## ⚠️ Current Limitations

- This is a prototype, not a production-grade autonomous software engineering system.
- Code retrieval is based on the indexed project files and may return irrelevant context.
- Generated code and tests depend on the quality of the Gemini responses.
- Passing generated tests does not guarantee that code is bug-free.
- Docker restrictions reduce execution risk but do not guarantee complete sandbox security.
- The retry mechanism has a limited number of attempts.

## 🔮 Future Improvements

- Function-level code indexing.
- More comprehensive test generation.
- Support for additional programming languages.
- Better test coverage and validation reporting.
- Remote isolated execution infrastructure.

## 👨‍💻 Author

**Ayush Yadav**  
B.Tech — Information Technology  
National Institute of Technology Srinagar

---

*AutoFix — Making debugging more structured through AI-assisted software engineering.*