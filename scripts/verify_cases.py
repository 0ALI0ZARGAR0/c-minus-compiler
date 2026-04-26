#!/usr/bin/env python3

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output"
ROOT_OUTPUT = ROOT / "output.txt"
INPUT_FILE = ROOT / "input.txt"
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"
PYTHON = str(VENV_PYTHON if VENV_PYTHON.exists() else Path(sys.executable))


def reset_generated_outputs() -> None:
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    if ROOT_OUTPUT.exists():
        ROOT_OUTPUT.unlink()


def run_compiler(relative_input: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [PYTHON, "compiler.py", relative_input],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def run_tac() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [PYTHON, "Tools/tac_interpreter.py", "output/output.txt"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def assert_file_text(relative_path: str, expected_text: str) -> None:
    actual_text = (ROOT / relative_path).read_text(encoding="utf-8").strip()
    if actual_text != expected_text.strip():
        raise AssertionError(f"{relative_path} did not match expected text")


def assert_contains(relative_path: str, expected_text: str) -> None:
    actual_text = (ROOT / relative_path).read_text(encoding="utf-8")
    if expected_text not in actual_text:
        raise AssertionError(f"{relative_path} did not contain {expected_text!r}")


def verify_phase1() -> None:
    result = run_compiler("cases/phase1-lexical/T1/input.txt")
    if result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)
    expected = (ROOT / "cases/phase1-lexical/T1/lexical_errors.txt").read_text(
        encoding="utf-8"
    )
    assert_file_text("output/lexical_errors.txt", expected)
    assert_contains("output/tokens.txt", "(KEYWORD, void)")


def verify_phase2() -> None:
    result = run_compiler("cases/phase2-parser-expected/T1/input.txt")
    if result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)
    assert_file_text("output/syntax_errors.txt", "There is no syntax error.")


def verify_phase3() -> None:
    result = run_compiler("cases/phase3-semantic/Test6/input.txt")
    if result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)
    assert_file_text(
        "output/semantic_errors.txt", "The input program is semantically correct."
    )
    tac_result = run_tac()
    if tac_result.returncode != 0:
        raise AssertionError(tac_result.stderr or tac_result.stdout)
    if tac_result.stdout.strip() != "PRINT    11":
        raise AssertionError("TAC output did not match expected execution result")


def main() -> int:
    original_input = INPUT_FILE.read_text(encoding="utf-8") if INPUT_FILE.exists() else None
    checks = [
        ("phase1 lexical", verify_phase1),
        ("phase2 parser", verify_phase2),
        ("phase3 semantic", verify_phase3),
    ]
    failures: list[tuple[str, str]] = []

    try:
        for label, check in checks:
            reset_generated_outputs()
            try:
                check()
                print(f"PASS {label}")
            except Exception as exc:
                failures.append((label, str(exc)))
                print(f"FAIL {label}: {exc}")
    finally:
        if original_input is not None:
            INPUT_FILE.write_text(original_input, encoding="utf-8")

    if failures:
        print("\nVerification failed:")
        for label, message in failures:
            print(f"- {label}: {message}")
        return 1

    print("\nAll selected phase checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
