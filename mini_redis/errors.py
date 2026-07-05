"""Redis 스타일 에러 메시지와 종료 코드를 모아둔 모듈."""

SUCCESS_EXIT_CODE = 0
KEYBOARD_INTERRUPT_EXIT_CODE = 1
COMMAND_ERROR_EXIT_CODE = 2


def is_error_response(response):
    """실행 결과가 Redis 스타일 에러 응답인지 확인한다."""
    return response.startswith("(error)")


def parse_error(message):
    """명령어 파싱 실패 메시지를 반환한다."""
    return "(error) ERR " + str(message)


def unknown_command(command):
    """알 수 없는 명령어 에러 메시지를 반환한다."""
    return "(error) ERR unknown command '" + command + "'"


def wrong_arguments(command):
    """인자 개수 오류 메시지를 반환한다."""
    return "(error) ERR wrong number of arguments for '" + command + "' command"


def integer_out_of_range():
    """정수 파싱 실패 또는 범위 오류 메시지를 반환한다."""
    return "(error) ERR value is not an integer or out of range"


def out_of_memory():
    """maxmemory 제한을 넘는 단일 엔트리 저장 시 OOM 메시지를 반환한다."""
    return "(error) OOM command not allowed when used_memory > 'maxmemory'"
