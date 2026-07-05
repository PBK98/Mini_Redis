"""Mini Redis CLI 실행 진입점."""

try:
    from .cli import run_repl
except ImportError:
    from cli import run_repl


if __name__ == "__main__":
    run_repl()
