
import streamlit as st
import os
import re
import time
from datetime import datetime
from core.workflow import run_project

# Cloud mode: syntax validation only. Local mode: Docker + unittest.
CLOUD_MODE = os.getenv("TEST_MODE", "docker").lower() == "cloud"

def status_text(passed):
    if CLOUD_MODE:
        return "SYNTAX VALID" if passed else "SYNTAX ERROR"
    return "PASSED" if passed else "FAILED"

# =====================================================
# CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="AutoFix | Engineering Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

if CLOUD_MODE:
    st.info("Cloud demo mode: Python syntax is checked without executing code. Unit tests and Docker are available only in the local version.")

# =====================================================
# DESIGN SYSTEM
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #080d18;
    --panel: #101827;
    --panel2: #141f30;
    --border: #263348;
    --text: #e8edf5;
    --muted: #8795a9;
    --accent: #818cf8;
    --green: #34d399;
    --red: #fb7185;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: var(--bg);
    color: var(--text);
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1500px;
    padding: 2rem 3rem 3rem 3rem;
}

section[data-testid="stSidebar"] {
    background: #0c1422;
    border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] .block-container {
    padding: 2rem 1rem;
}

.brand {
    font-size: 25px;
    font-weight: 800;
    letter-spacing: -1px;
    color: white;
    margin-bottom: 4px;
}

.brand span {
    color: #818cf8;
}

.brand-caption {
    font-size: 11px;
    color: #8190a5;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 35px;
}

.nav-label {
    color: #68778d;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.8px;
    margin: 25px 0 10px 8px;
}

.sidebar-info {
    background: #111d2e;
    border: 1px solid #263348;
    border-radius: 10px;
    padding: 14px;
    margin-top: 30px;
}

.sidebar-info p {
    color: #9aa8ba;
    font-size: 11px;
    margin: 5px 0;
}

.page-heading {
    font-size: 30px;
    font-weight: 800;
    letter-spacing: -1px;
    color: #f8fafc;
    margin-bottom: 4px;
}

.page-subtitle {
    color: var(--muted);
    font-size: 13px;
    margin-bottom: 28px;
}

.panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 18px;
}

.panel-title {
    color: #f1f5f9;
    font-size: 15px;
    font-weight: 700;
    margin-bottom: 5px;
}

.panel-caption {
    color: var(--muted);
    font-size: 11px;
    margin-bottom: 18px;
}

.metric-card {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px;
    min-height: 105px;
}

.metric-label {
    font-size: 11px;
    color: #8795a9;
    margin-bottom: 12px;
}

.metric-value {
    font-size: 25px;
    font-weight: 800;
    color: #f8fafc;
}

.metric-green {
    color: var(--green);
}

.metric-red {
    color: var(--red);
}

.status-dot {
    display: inline-block;
    height: 8px;
    width: 8px;
    background: #34d399;
    border-radius: 50%;
    margin-right: 7px;
}

div[data-testid="stTextArea"] textarea {
    background: #0b1321 !important;
    color: #e2e8f0 !important;
    border: 1px solid #2c3b51 !important;
    border-radius: 8px !important;
    font-family: Consolas, monospace !important;
    font-size: 13px !important;
}

div[data-testid="stTextArea"] textarea:focus {
    border: 1px solid #818cf8 !important;
    box-shadow: 0 0 0 1px #818cf8 !important;
}

.stButton > button {
    background: #6366f1;
    color: white;
    border: 1px solid #818cf8;
    border-radius: 8px;
    font-weight: 700;
    min-height: 43px;
    transition: 0.2s;
}

.stButton > button:hover {
    background: #4f46e5;
    color: white;
    border-color: #a5b4fc;
}

div[data-testid="stMetric"] {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 15px;
}

div[data-testid="stMetricLabel"] {
    color: #8795a9;
}

div[data-testid="stMetricValue"] {
    color: white;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 20px;
    border-bottom: 1px solid var(--border);
}

.stTabs [data-baseweb="tab"] {
    color: #9aa8ba;
    font-size: 12px;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    color: #a5b4fc !important;
}

div[data-testid="stCode"] {
    border: 1px solid #29384d;
    border-radius: 9px;
}

div[data-testid="stAlert"] {
    border-radius: 9px;
}

hr {
    border-color: var(--border);
}

.footer {
    border-top: 1px solid var(--border);
    margin-top: 45px;
    padding-top: 20px;
    color: #64748b;
    font-size: 11px;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:
    st.markdown("""
    <div class="brand">⚡ Auto<span>Fix</span></div>
    <div class="brand-caption">Engineering Intelligence</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-label">WORKSPACE</div>',
                unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["Overview", "Code Debugger", "Test Reports"],
        label_visibility="collapsed"
    )

    st.markdown('<div class="nav-label">SYSTEM</div>',
                unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sidebar-info">
        <p><span class="status-dot"></span> Application online</p>
        <p>AI Engine: Gemini</p>
        <p>Workflow: LangGraph</p>
        <p>Validation: {"Syntax only" if CLOUD_MODE else "Docker + unittest"}</p>
        <p>Retrieval: ChromaDB</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sidebar-info">
        <p style="color:white;font-weight:700;">AutoFix</p>
        <p>AI-assisted software debugging and code validation.</p>
        <p>{"Cloud demo environment" if CLOUD_MODE else "Local development environment"}</p>
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# SESSION STATE
# =====================================================

if "autofix_result" not in st.session_state:
    st.session_state.autofix_result = None

if "last_task" not in st.session_state:
    st.session_state.last_task = ""

if "last_code" not in st.session_state:
    st.session_state.last_code = ""

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def metric_card(label, value, color=""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value {color}">{value}</div>
    </div>
    """, unsafe_allow_html=True)


def get_test_count(report):
    match = re.search(r"Ran\s+(\d+)\s+tests?", str(report))
    return int(match.group(1)) if match else 0

# =====================================================
# OVERVIEW
# =====================================================

if page == "Overview":
    st.markdown('<div class="page-heading">Engineering Overview</div>',
                unsafe_allow_html=True)

    st.markdown(
        '<div class="page-subtitle">Monitor your debugging workspace and testing activity.</div>',
        unsafe_allow_html=True
    )

    result = st.session_state.autofix_result

    if result:
        passed = result.get("test_passed", False)
        attempts = result.get("attempts", 0)
        report = result.get("test_report", "")
        count = get_test_count(report)

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            metric_card("LATEST VALIDATION STATUS",
                        status_text(passed),
                        "metric-green" if passed else "metric-red")

        with c2:
            metric_card("CHECKS PERFORMED" if CLOUD_MODE else "TEST CASES EXECUTED",
                        "Syntax" if CLOUD_MODE else count)

        with c3:
            metric_card("DEVELOPMENT ATTEMPTS", attempts)

        with c4:
            metric_card("WORKFLOW STATUS", "Completed")

        st.markdown("### Latest execution")
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.write("**Task:**", st.session_state.last_task)

        st.write(
            "**Completed at:**",
            datetime.now().strftime("%d %b %Y, %H:%M")
        )

        st.write("**Result:**", ("Python syntax is valid" if passed else "Python syntax error detected")
                 if CLOUD_MODE else
                 ("All tests passed" if passed else "Tests failed or could not complete"))
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        c1, c2, c3 = st.columns(3)

        with c1:
            metric_card("VALIDATIONS" if CLOUD_MODE else "TEST EXECUTIONS", "0")

        with c2:
            metric_card("ACTIVE WORKFLOWS", "0")

        with c3:
            metric_card("LATEST STATUS", "Idle")

        st.info(
            "Your workspace is ready. Open Code Debugger to start your first analysis."
        )

# =====================================================
# CODE DEBUGGER
# =====================================================

elif page == "Code Debugger":
    st.markdown('<div class="page-heading">Code Debugger</div>',
                unsafe_allow_html=True)

    st.markdown(
        '<div class="page-subtitle">Analyze source code, identify issues, generate improvements and validate results.</div>',
        unsafe_allow_html=True
    )

    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown("""
        <div class="panel">
            <div class="panel-title">01   Problem Definition</div>
            <div class="panel-caption">Describe the expected behavior or issue.</div>
        </div>
        """, unsafe_allow_html=True)

        task = st.text_area(
            "Problem description",
            placeholder="Example: Fix the IndexError caused by accessing an invalid array index.",
            height=150,
            key="debug_task"
        )

    with right:
        st.markdown("""
        <div class="panel">
            <div class="panel-title">02   Source Code</div>
            <div class="panel-caption">Provide the Python source code for analysis.</div>
        </div>
        """, unsafe_allow_html=True)

        source_code = st.text_area(
            "Python source",
            placeholder="def calculate_total(numbers):\n    ...",
            height=150,
            key="debug_code"
        )

    st.markdown("### Execution Configuration")

    config1, config2 = st.columns(2)

    with config1:
        st.selectbox(
            "Programming language",
            ["Python"],
            disabled=True
        )

    with config2:
        st.selectbox(
            "Validation engine",
            ["Syntax validation" if CLOUD_MODE else "Docker + unittest"],
            disabled=True
        )

    st.markdown("")

    run_col, clear_col = st.columns([3, 1])

    with run_col:
        run_button = st.button(
            "⚡  RUN ANALYSIS & VALIDATE" if CLOUD_MODE else "⚡  RUN ANALYSIS & TESTS",
            use_container_width=True
        )

    with clear_col:
        def clear_inputs():
            st.session_state.debug_task = ""
            st.session_state.debug_code = ""

        st.button(
            "Clear inputs",
            use_container_width=True,
            on_click=clear_inputs
        )

    if run_button:
        if not task.strip():
            st.warning("Enter a problem description.")

        elif not source_code.strip():
            st.warning("Enter source code to analyze.")

        else:
            try:
                with st.status(
                    "Executing AutoFix workflow...",
                    expanded=True
                ) as status:

                    st.write("Generating execution plan...")
                    st.write("Retrieving relevant code context...")
                    st.write("Generating code improvement...")
                    if CLOUD_MODE:
                        st.write("Checking Python syntax (no code execution)...")
                    else:
                        st.write("Creating unit tests...")
                        st.write("Running tests inside Docker sandbox...")

                    result = run_project(
                        task=task,
                        source_code=source_code
                    )

                    status.update(
                        label="Workflow execution completed",
                        state="complete",
                        expanded=False
                    )

                st.session_state.autofix_result = result
                st.session_state.last_task = task
                st.session_state.last_code = source_code

                st.success("Analysis completed. View the results below.")

            except Exception as error:
                st.error("Workflow execution failed.")
                st.exception(error)

    # =================================================
    # RESULTS
    # =================================================

    result = st.session_state.autofix_result

    if result:
        st.divider()
        st.markdown("## Execution Results")

        passed = result.get("test_passed", False)
        attempts = result.get("attempts", 0)
        report = result.get("test_report", "")
        count = get_test_count(report)

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            metric_card(
                "VALIDATION",
                status_text(passed),
                "metric-green" if passed else "metric-red"
            )

        with c2:
            metric_card("SYNTAX CHECK" if CLOUD_MODE else "TEST CASES",
                            "1" if CLOUD_MODE else count)

        with c3:
            metric_card("ATTEMPTS", attempts)

        with c4:
            metric_card("EXECUTION", "Finished")

        st.markdown("")

        t1, t2, t3, t4, t5 = st.tabs([
            "Execution Plan",
            "Improved Code",
            "AI Explanation",
            "Unit Tests" if not CLOUD_MODE else "Test Availability",
            "Test Report" if not CLOUD_MODE else "Syntax Report"
        ])

        with t1:
            st.markdown("### Development Plan")
            st.write(result.get("plan", "No plan available."))

        with t2:
            st.markdown("### Generated Code")
            improved = result.get("improvement", "")

            if improved:
                st.code(improved, language="python")

                st.download_button(
                    "Download improved code",
                    data=improved,
                    file_name="improved_solution.py",
                    mime="text/x-python"
                )

            else:
                st.warning("No improved code was returned.")

        with t3:
            st.markdown("### Explanation")
            st.write(
                result.get("explanation", "No explanation available.")
            )

        with t4:
            st.markdown("### Generated Unit Tests" if not CLOUD_MODE else "### Cloud Validation Limitations")
            tests = result.get("generated_tests", "")

            if CLOUD_MODE:
                st.info("Unit tests are not generated or executed in cloud mode. Run AutoFix locally with Docker to execute them.")
            elif tests:
                st.code(tests, language="python")

                st.download_button(
                    "Download test file",
                    data=tests,
                    file_name="test_solution.py",
                    mime="text/x-python"
                )

            else:
                st.info("No tests were generated.")

        with t5:
            st.markdown("### Syntax Validation Output" if CLOUD_MODE else "### Test Execution Output")

            if passed:
                st.success("Python syntax is valid. Unit tests were not executed." if CLOUD_MODE else "All generated tests passed.")
            else:
                st.error("Python syntax validation failed." if CLOUD_MODE else "Tests failed or no tests completed successfully.")

            st.code(report if report else "No execution report available.")

            st.markdown("### Retrieved Code Context")
            st.code(
                result.get("context", "No context retrieved.")
            )

# =====================================================
# TEST REPORTS
# =====================================================

elif page == "Test Reports":
    st.markdown('<div class="page-heading">Test Reports</div>',
                unsafe_allow_html=True)

    st.markdown(
        '<div class="page-subtitle">Review the most recent test execution and generated test artifacts.</div>',
        unsafe_allow_html=True
    )

    result = st.session_state.autofix_result

    if not result:
        st.info("No test executions available. Run a debugging workflow first.")

    else:
        passed = result.get("test_passed", False)
        report = result.get("test_report", "")
        tests = result.get("generated_tests", "")

        if passed:
            st.success(f"Latest validation: {status_text(True)}")
        else:
            st.error(f"Latest validation: {status_text(False)}")

        st.markdown("### Execution summary")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric("Validation", "Syntax only" if CLOUD_MODE else f"{get_test_count(report)} tests")

        with c2:
            st.metric("Attempts", result.get("attempts", 0))

        with c3:
            st.metric("Status", status_text(passed))

        st.markdown("### Syntax check output" if CLOUD_MODE else "### Test output")
        st.code(report if report else "No report available.")

        if CLOUD_MODE:
            st.info("No unit tests were generated or executed. Use the local Docker version for full testing.")
        else:
            st.markdown("### Test suite")
            st.code(tests if tests else "No generated tests available.",
                    language="python")

# =====================================================
# FOOTER
# =====================================================

st.markdown(f"""
<div class="footer">
    AUTOFIX ENGINEERING INTELLIGENCE
    <br><br>
    AI-assisted debugging   •
    {"Syntax-only cloud validation" if CLOUD_MODE else "Automated validation   •   Isolated test execution"}
    <br><br>
    Powered by Python, LangGraph, Gemini, ChromaDB{"" if CLOUD_MODE else " and Docker"}
</div>
""", unsafe_allow_html=True)
