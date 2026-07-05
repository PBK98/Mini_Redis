"""Mini Redis 명령어 파서와 REPL."""

import shlex

try:
    from . import redis_errors
    from .mini_redis import MiniRedis
    from .runtime import ReplRuntime
except ImportError:
    import redis_errors
    from mini_redis import MiniRedis
    from runtime import ReplRuntime


class ParsedCommand:
    """파싱된 명령어 토큰과 에러 메시지를 담는다."""

    def __init__(self, parts=None, error=None):
        self.parts = parts or []
        self.error = error

    def is_empty(self):
        return not self.parts and self.error is None


class CommandSpec:
    """명령어 이름, 전체 토큰 수, 실행 함수를 정의한다."""

    def __init__(self, tokens, expected_length, handler):
        self.tokens = tokens
        self.expected_length = expected_length
        self.handler = handler

    def matches(self, parts):
        if len(parts) < len(self.tokens):
            return False

        for index, token in enumerate(self.tokens):
            if parts[index].upper() != token:
                return False
        return True

    def validate(self, parts):
        return len(parts) == self.expected_length

    def execute(self, parts):
        return self.handler(parts)


class CommandParser:
    """입력 문자열을 토큰화하고 실행할 명령어 스펙을 찾는다."""

    def __init__(self, specs):
        self.specs = specs

    def parse(self, line):
        try:
            parts = shlex.split(line)
        except ValueError as error:
            return ParsedCommand(error=redis_errors.parse_error(error))

        return ParsedCommand(parts=parts)

    def find_spec(self, parts):
        for spec in self.specs:
            if spec.matches(parts):
                return spec
        return None

    def has_command(self, command):
        command = command.upper()
        for spec in self.specs:
            if spec.tokens[0] == command:
                return True
        return False


class CommandProcessor:
    """CLI 입력 토큰을 MiniRedis 메서드 호출로 변환한다."""

    def __init__(self, database=None):
        self.database = database or MiniRedis()
        self.parser = CommandParser(self._build_specs())

    def execute(self, line):
        parsed = self.parser.parse(line)
        if parsed.error:
            return parsed.error

        if parsed.is_empty():
            return ""

        spec = self.parser.find_spec(parsed.parts)
        if spec is None:
            if self.parser.has_command(parsed.parts[0]):
                return self._wrong_args(parsed.parts[0].upper())
            return redis_errors.unknown_command(parsed.parts[0])

        if not spec.validate(parsed.parts):
            return self._wrong_args(parsed.parts[0].upper())

        return spec.execute(parsed.parts)

    def _build_specs(self):
        return [
            CommandSpec(("SET",), 3, lambda parts: self.database.set(parts[1], parts[2])),
            CommandSpec(("GET",), 2, lambda parts: self.database.get(parts[1])),
            CommandSpec(("DEL",), 2, lambda parts: self.database.delete(parts[1])),
            CommandSpec(("EXISTS",), 2, lambda parts: self.database.exists(parts[1])),
            CommandSpec(("DBSIZE",), 1, lambda parts: self.database.dbsize()),
            CommandSpec(("KEYS",), 1, lambda parts: self.database.keys()),
            CommandSpec(
                ("CONFIG", "SET", "MAXMEMORY"),
                4,
                lambda parts: self.database.config_set_maxmemory(parts[3]),
            ),
            CommandSpec(("INFO", "MEMORY"), 2, lambda parts: self.database.info_memory()),
            CommandSpec(("EXPIRE",), 3, lambda parts: self.database.expire(parts[1], parts[2])),
            CommandSpec(("TTL",), 2, lambda parts: self.database.ttl(parts[1])),
        ]

    def _wrong_args(self, command):
        return redis_errors.wrong_arguments(command)


def run_repl():
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
