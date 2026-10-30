from core.workflow import run_project


def main():
    task = input("What should I fix? ")

    print("\nPaste your Python code below.")
    print("Type END on a new line when finished.\n")

    code_lines = []

    while True:
        line = input()

        if line.strip() == "END":
            break

        code_lines.append(line)

    source_code = "\n".join(code_lines)

    if not source_code.strip():
        print("No code was provided.")
        return

    print("\nStarting AutoFix...\n")

    try:
        result = run_project(task, source_code)

        print("\n========== PLANNER ==========")
        print(result["plan"])

        print("\n========== CODE ANALYST ==========")
        print(result["context"])

        print("\n========== CORRECTED CODE ==========")
        print(result["improvement"])

        print("\n========== DEVELOPER EXPLANATION ==========")
        print(result["explanation"])

        print("\n========== GENERATED TESTS ==========")
        print(result["generated_tests"])

        print("\n========== TEST RESULTS ==========")
        print(result["test_report"])

        print("\n========== FINAL STATUS ==========")
        print("Tests passed:", result["test_passed"])
        print("Correction attempts:", result["attempts"])

    except Exception as error:
        print("\nAutoFix encountered an error:")
        print(error)


if __name__ == "__main__":
    main()