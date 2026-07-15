"""Mini Redis 명령어 파서와 실행 연결."""

import shlex
from typing import Callable, List, Optional, Sequence, Tuple

try:
    from . import redis_errors
    from .mini_redis import MiniRedis
except ImportError:
    import redis_errors
    from mini_redis import MiniRedis


class ParsedCommand:
    """파싱된 명령어 토큰과 에러 메시지를 담는다."""

    def __init__(self, parts: Optional[List[str]] = None, error: Optional[str] = None) -> None:
        self.parts = parts or []
        self.error = error

    def is_empty(self) -> bool:
        return not self.parts and self.error is None


class CommandSpec:
    """명령어 이름, 전체 토큰 수, 실행 함수를 정의한다."""

    def __init__(
        self,
        tokens: Tuple[str, ...],
        expected_length: int,
        handler: Callable[[List[str]], str],
    ) -> None:
        self.tokens = tokens
        self.expected_length = expected_length
        self.handler = handler

    def matches(self, parts: Sequence[str]) -> bool:
        if len(parts) < len(self.tokens):
            return False

        for index, token in enumerate(self.tokens):
            if parts[index].upper() != token:
                return False
        return True

    def validate(self, parts: Sequence[str]) -> bool:
        return len(parts) == self.expected_length

    def execute(self, parts: List[str]) -> str:
        return self.handler(parts)


class CommandParser:
    """입력 문자열을 토큰화하고 실행할 명령어 스펙을 찾는다."""

    def __init__(self, specs: List[CommandSpec]) -> None:
        self.specs = specs

    def parse(self, line: str) -> ParsedCommand:
        try:
            parts = shlex.split(line)
        except ValueError as error:
            return ParsedCommand(error=redis_errors.parse_error(error))

        return ParsedCommand(parts=parts)

    def find_spec(self, parts: Sequence[str]) -> Optional[CommandSpec]:
        for spec in self.specs:
            if spec.matches(parts):
                return spec
        return None

    def has_command(self, command: str) -> bool:
        command = command.upper()
        for spec in self.specs:
            if spec.tokens[0] == command:
                return True
        return False


class CommandProcessor:
    """CLI 입력 토큰을 MiniRedis 메서드 호출로 변환한다."""

    def __init__(self, database: Optional[MiniRedis] = None) -> None:
        self.database = database or MiniRedis()
        self.parser = CommandParser(self._build_specs())

    def execute(self, line: str) -> str:
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

    def _build_specs(self) -> List[CommandSpec]:
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

    def _wrong_args(self, command: str) -> str:
        return redis_errors.wrong_arguments(command)
