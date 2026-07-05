"""Command parser and REPL for Mini Redis."""

import shlex

try:
    from .mini_redis import MiniRedis
except ImportError:
    from mini_redis import MiniRedis


class CommandProcessor:
    """Translate CLI tokens into MiniRedis method calls."""

    def __init__(self, database=None):
        self.database = database or MiniRedis()

    def execute(self, line):
        try:
            parts = shlex.split(line)
        except ValueError as error:
            return "(error) ERR " + str(error)

        if not parts:
            return ""

        command = parts[0].upper()

        if command == "SET":
            if len(parts) != 3:
                return self._wrong_args("SET")
            return self.database.set(parts[1], parts[2])

        if command == "GET":
            if len(parts) != 2:
                return self._wrong_args("GET")
            return self.database.get(parts[1])

        if command == "DEL":
            if len(parts) != 2:
                return self._wrong_args("DEL")
            return self.database.delete(parts[1])

        if command == "EXISTS":
            if len(parts) != 2:
                return self._wrong_args("EXISTS")
            return self.database.exists(parts[1])

        if command == "DBSIZE":
            if len(parts) != 1:
                return self._wrong_args("DBSIZE")
            return self.database.dbsize()

        if command == "KEYS":
            if len(parts) != 1:
                return self._wrong_args("KEYS")
            return self.database.keys()

        if command == "CONFIG":
            if len(parts) != 4 or parts[1].upper() != "SET" or parts[2].lower() != "maxmemory":
                return self._wrong_args("CONFIG")
            return self.database.config_set_maxmemory(parts[3])

        if command == "INFO":
            if len(parts) != 2 or parts[1].lower() != "memory":
                return self._wrong_args("INFO")
            return self.database.info_memory()

        if command == "EXPIRE":
            if len(parts) != 3:
                return self._wrong_args("EXPIRE")
            return self.database.expire(parts[1], parts[2])

        if command == "TTL":
            if len(parts) != 2:
                return self._wrong_args("TTL")
            return self.database.ttl(parts[1])

        return "(error) ERR unknown command '" + parts[0] + "'"

    def _wrong_args(self, command):
        return "(error) ERR wrong number of arguments for '" + command + "' command"


def run_repl():
    """Start the interactive mini-redis prompt."""
    processor = CommandProcessor()

    while True:
        try:
            line = input("mini-redis> ")
        except EOFError:
            print()
            break

        if line.strip().lower() in ("exit", "quit"):
            break

        output = processor.execute(line)
        if output:
            print(output)
