from orbit.diagnostics.system import (
    DiagnosticResult,
    run_diagnostics,
)


def test_diagnostics_report_runtime_components() -> None:
    results = run_diagnostics()

    assert results
    assert all(isinstance(result, DiagnosticResult) for result in results)
    assert {result.component for result in results} >= {
        "Python",
        "Textual",
        "Database",
        "GPU",
    }