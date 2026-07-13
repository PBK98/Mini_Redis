"""Mini Redis 과제를 위한 작은 회귀 테스트."""

import time
import unittest

from mini_redis.cli import CommandProcessor


class MiniRedisTest(unittest.TestCase):
    def setUp(self):
        self.processor = CommandProcessor()

    def test_string_commands(self):
        self.assertEqual(self.processor.execute('SET user:1 "Alice"'), "OK")
        self.assertEqual(self.processor.execute("GET user:1"), '"Alice"')
        self.assertEqual(self.processor.execute("EXISTS user:1"), "(integer) 1")
        self.assertEqual(self.processor.execute("DBSIZE"), "(integer) 1")
        self.assertEqual(self.processor.execute("DEL user:1"), "(integer) 1")
        self.assertEqual(self.processor.execute("GET user:1"), "(nil)")

    def test_lru_eviction(self):
        self.assertEqual(self.processor.execute("CONFIG SET maxmemory 30"), "OK")
        self.assertEqual(self.processor.execute('SET user:1 "Alice"'), "OK")
        self.assertEqual(self.processor.execute('SET user:2 "Bob"'), "OK")
        self.assertEqual(self.processor.execute('SET user:3 "Charlie"'), "OK")
        self.assertEqual(self.processor.execute("GET user:1"), "(nil)")
        info = self.processor.execute("INFO memory")
        self.assertIn("evicted_keys:1", info)

    def test_ttl(self):
        self.assertEqual(self.processor.execute("SET temp value"), "OK")
        self.assertEqual(self.processor.execute("EXPIRE temp 1"), "(integer) 1")
        self.assertIn(self.processor.execute("TTL temp"), ("(integer) 0", "(integer) 1"))
        time.sleep(1.1)
        self.assertEqual(self.processor.execute("GET temp"), "(nil)")
        self.assertEqual(self.processor.execute("TTL temp"), "(integer) -2")

    def test_set_clears_existing_ttl(self):
        self.assertEqual(self.processor.execute("SET session old"), "OK")
        self.assertEqual(self.processor.execute("EXPIRE session 1"), "(integer) 1")
        self.assertEqual(self.processor.execute("SET session new"), "OK")
        self.assertEqual(self.processor.execute("TTL session"), "(integer) -1")
        time.sleep(1.1)
        self.assertEqual(self.processor.execute("GET session"), '"new"')

    def test_expire_zero_deletes_key(self):
        self.assertEqual(self.processor.execute("SET temp value"), "OK")
        self.assertEqual(self.processor.execute("EXPIRE temp 0"), "(integer) 1")
        self.assertEqual(self.processor.execute("EXISTS temp"), "(integer) 0")

    def test_single_entry_larger_than_maxmemory_is_rejected(self):
        self.assertEqual(self.processor.execute("CONFIG SET maxmemory 4"), "OK")
        self.assertEqual(
            self.processor.execute("SET username Alice"),
            "(error) OOM command not allowed when used_memory > 'maxmemory'",
        )
        self.assertEqual(self.processor.execute("DBSIZE"), "(integer) 0")

    def test_errors(self):
        self.assertEqual(
            self.processor.execute("CONFIG SET maxmemory abc"),
            "(error) ERR value is not an integer or out of range",
        )
        self.assertEqual(
            self.processor.execute("GET"),
            "(error) ERR wrong number of arguments for 'GET' command",
        )
        self.assertEqual(
            self.processor.execute("HELLO"),
            "(error) ERR unknown command 'HELLO'",
        )


if __name__ == "__main__":
    unittest.main()
