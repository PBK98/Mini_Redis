"""Executable entry point for the Mini Redis CLI."""

try:
    from .cli import run_repl
except ImportError:
    from cli import run_repl


if __name__ == "__main__":
    run_repl()
