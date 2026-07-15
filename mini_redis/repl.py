"""Mini Redis 대화형 입력 루프."""

try:
    from .cli import CommandProcessor
    from .runtime import ReplRuntime
except ImportError:
    from cli import CommandProcessor
    from runtime import ReplRuntime


def run_repl() -> None:
    """대화형 mini-redis 프롬프트를 시작한다."""
    processor = CommandProcessor()
    runtime = ReplRuntime()

    while True:
        try:
            line = input("mini-redis> ")
        except KeyboardInterrupt:
            runtime.handle_keyboard_interrupt()
        except EOFError:
            runtime.handle_eof()
            break

        if line.strip().lower() in ("exit", "quit"):
            break

        output = processor.execute(line)
        if output:
            print(output)
            runtime.record_output(output)

    runtime.exit()
