
import streamlit as st

st.set_page_config(
    page_title="AutoFix AI",
    page_icon="🛠️",
    layout="wide"
)

st.title("🛠️ AutoFix AI")
st.caption("AI-powered Python debugging and automated testing")

task = st.text_area(
    "Describe the bug or what you want to fix",
    placeholder="Example: Fix the index error in this code..."
)

code = st.text_area(
    "Paste your Python code",
    height=350,
    placeholder="Paste your Python code here..."
)

if st.button("Fix My Code", type="primary"):
    if not task.strip() or not code.strip():
        st.warning("Please enter both a task and Python code.")
    else:
        with st.spinner("AutoFix is working..."):
            try:
                from core.workflow import run_project
                result = run_project(task, code)

                st.subheader("Corrected Code")
                st.code(result["improvement"], language="python")

                st.subheader("Explanation")
                st.write(result["explanation"])

                st.subheader("Generated Tests")
                st.code(result["generated_tests"], language="python")

                st.subheader("Test Results")
                st.code(result["test_report"])

                st.write("Tests passed:", result["test_passed"])
                st.write("Correction attempts:", result["attempts"])

            except Exception as e:
                st.error(f"AutoFix failed: {e}")
