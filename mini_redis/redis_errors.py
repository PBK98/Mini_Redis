"""Redis 스타일 에러 메시지를 생성하는 모듈."""


def parse_error(message: object) -> str:
    """명령어 파싱 실패 메시지를 반환한다."""
    return "(error) ERR " + str(message)


def unknown_command(command: str) -> str:
    """알 수 없는 명령어 에러 메시지를 반환한다."""
    return "(error) ERR unknown command '" + command + "'"


def wrong_arguments(command: str) -> str:
    """인자 개수 오류 메시지를 반환한다."""
    return "(error) ERR wrong number of arguments for '" + command + "' command"


def integer_out_of_range() -> str:
    """정수 파싱 실패 또는 범위 오류 메시지를 반환한다."""
    return "(error) ERR value is not an integer or out of range"


def out_of_memory() -> str:
    """maxmemory 제한을 넘는 단일 엔트리 저장 시 OOM 메시지를 반환한다."""
    return "(error) OOM command not allowed when used_memory > 'maxmemory'"
