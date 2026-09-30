"""Dependency and hardware diagnostics for the ORBIT runtime."""

from dataclasses import dataclass
import importlib.util
import platform
import sys


@dataclass(frozen=True)
class DiagnosticResult:
    """Result of one runtime diagnostic check."""

    component: str
    status: str
    detail: str


def run_diagnostics() -> list[DiagnosticResult]:
    """Collect local diagnostics without making external network calls."""

    return [
        _python_check(),
        _textual_check(),
        _database_check(),
        _gpu_check(),
    ]


def _python_check() -> DiagnosticResult:
    """Report the active Python runtime."""

    version = platform.python_version()
    return DiagnosticResult(
        "Python",
        "OK",
        f"{version} on {platform.system()}",
    )


def _textual_check() -> DiagnosticResult:
    """Report whether the terminal UI dependency is importable."""

    if importlib.util.find_spec("textual") is None:
        return DiagnosticResult(
            "Textual",
            "MISSING",
            "Install project requirements",
        )

    return DiagnosticResult(
        "Textual",
        "OK",
        "terminal UI available",
    )


def _database_check() -> DiagnosticResult:
    """Report whether a database URL is configured."""

    try:
        from app.core.config import settings
    except (ImportError, ModuleNotFoundError) as error:
        return DiagnosticResult(
            "Database",
            "ERROR",
            f"configuration unavailable: {error}",
        )

    database_url = settings.database_url.strip()

    if not database_url:
        return DiagnosticResult(
            "Database",
            "MISSING",
            "database URL is empty",
        )

    scheme = database_url.split(":", maxsplit=1)[0]
    return DiagnosticResult(
        "Database",
        "CONFIGURED",
        f"{scheme} backend",
    )


def _gpu_check() -> DiagnosticResult:
    """Report optional PyTorch GPU availability when installed."""

    if importlib.util.find_spec("torch") is None:
        return DiagnosticResult(
            "GPU",
            "UNAVAILABLE",
            "optional PyTorch runtime not installed",
        )

    try:
        import torch
    except ImportError as error:
        return DiagnosticResult(
            "GPU",
            "ERROR",
            f"PyTorch import failed: {error}",
        )

    if not torch.cuda.is_available():
        return DiagnosticResult(
            "GPU",
            "UNAVAILABLE",
            "no CUDA device detected; CPU fallback available",
        )

    device_name = torch.cuda.get_device_name(0)
    memory_gib = torch.cuda.get_device_properties(0).total_memory / 2**30
    return DiagnosticResult(
        "GPU",
        "ENABLED",
        f"{device_name}, {memory_gib:.1f} GiB VRAM",
    )