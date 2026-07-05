"""REPL 실행 중 발생하는 종료 상태를 관리한다."""

import sys

SUCCESS_EXIT_CODE = 0
KEYBOARD_INTERRUPT_EXIT_CODE = 1
COMMAND_ERROR_EXIT_CODE = 2


def is_error_response(response):
    """실행 결과가 Redis 스타일 에러 응답인지 확인한다."""
    return response.startswith("(error)")


class ReplRuntime:
    """REPL의 종료 코드와 입력 예외 처리를 담당한다."""

    def __init__(self):
        self.exit_code = SUCCESS_EXIT_CODE

    def record_output(self, output):
        """출력 결과에 에러가 포함되어 있으면 종료 코드를 갱신한다."""
        if is_error_response(output):
            self.exit_code = COMMAND_ERROR_EXIT_CODE

    def handle_keyboard_interrupt(self):
        """Ctrl+C 입력을 처리하고 지정된 코드로 종료한다."""
        print("\n강제 종료되었습니다.")
        sys.exit(KEYBOARD_INTERRUPT_EXIT_CODE)

    def handle_eof(self):
        """입력 종료 시 안내 문구를 출력한다."""
        print("\n입력을 종료합니다.")

    def exit(self):
        """현재까지 기록된 상태에 맞는 코드로 종료한다."""
        sys.exit(self.exit_code)
