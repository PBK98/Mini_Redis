"""Mini Redis 명령 실행 핵심 로직."""

import time
from typing import Optional

try:
    from . import redis_errors
    from .hash_map import HashMap
    from .linked_list import DoublyLinkedList
    from .linked_list import ListNode
    from .min_heap import MinHeap
except ImportError:
    import redis_errors
    from hash_map import HashMap
    from linked_list import DoublyLinkedList
    from linked_list import ListNode
    from min_heap import MinHeap


class RedisEntry:
    """값과 메모리 계산, LRU, TTL 관리에 필요한 메타데이터."""

    def __init__(self, key: str, value: str, lru_node: ListNode) -> None:
        self.key = key
        self.value = value
        self.lru_node = lru_node
        self.expire_at: Optional[float] = None


class MiniRedis:
    """Redis 스타일 문자열 명령어를 지원하는 인메모리 키-값 저장소."""

    def __init__(self) -> None:
        self.store = HashMap()
        self.lru = DoublyLinkedList()
        self.expirations = MinHeap()
        self.used_memory = 0
        self.maxmemory = 0
        self.evicted_keys = 0

    def set(self, key: str, value: str) -> str:
        self._delete_if_expired(key)
        entry_memory = self._entry_size(key, value)

        if self.maxmemory > 0 and entry_memory > self.maxmemory:
            return redis_errors.out_of_memory()

        entry = self.store.get(key)
        if entry is None:
            node = self.lru.insert_front(key)
            entry = RedisEntry(key, value, node)
            self.store.put(key, entry)
            self.used_memory += entry_memory
        else:
            self.used_memory -= self._entry_size(key, entry.value)
            entry.value = value
            entry.expire_at = None
            entry.lru_node = self.lru.move_to_front(entry.lru_node)
            self.used_memory += entry_memory

        self._evict_until_within_limit()
        return "OK"

    def get(self, key: str) -> str:
        if self._delete_if_expired(key):
            return "(nil)"

        entry = self.store.get(key)
        if entry is None:
            return "(nil)"

        entry.lru_node = self.lru.move_to_front(entry.lru_node)
        return '"' + entry.value + '"'

    def delete(self, key: str) -> str:
        if self._remove_key(key, evicted=False):
            return "(integer) 1"
        return "(integer) 0"

    def exists(self, key: str) -> str:
        self._delete_if_expired(key)
        if self.store.contains(key):
            return "(integer) 1"
        return "(integer) 0"

    def dbsize(self) -> str:
        self._purge_expired()
        return "(integer) " + str(self.store.size())

    def keys(self) -> str:
        self._purge_expired()
        keys = self.store.keys()
        if not keys:
            return "(empty array)"

        lines = []
        for index, key in enumerate(keys, start=1):
            lines.append(str(index) + '. "' + key + '"')
        return "\n".join(lines)

    def config_set_maxmemory(self, value_text: str) -> str:
        value = self._parse_non_negative_int(value_text)
        if value is None:
            return redis_errors.integer_out_of_range()

        self.maxmemory = value
        self._evict_until_within_limit()
        return "OK"

    def info_memory(self) -> str:
        self._purge_expired()
        return (
            "used_memory:" + str(self.used_memory) + "\n"
            "maxmemory:" + str(self.maxmemory) + "\n"
            "evicted_keys:" + str(self.evicted_keys)
        )

    def expire(self, key: str, seconds_text: str) -> str:
        seconds = self._parse_int(seconds_text)
        if seconds is None:
            return redis_errors.integer_out_of_range()

        self._delete_if_expired(key)
        entry = self.store.get(key)
        if entry is None:
            return "(integer) 0"

        if seconds <= 0:
            self._remove_key(key, evicted=False)
            return "(integer) 1"

        expire_at = time.time() + seconds
        entry.expire_at = expire_at
        # 오래된 힙 레코드는 entry.expire_at과 더 이상 맞지 않으면 나중에 무시한다.
        self.expirations.push((expire_at, key))
        return "(integer) 1"

    def ttl(self, key: str) -> str:
        if self._delete_if_expired(key):
            return "(integer) -2"

        entry = self.store.get(key)
        if entry is None:
            return "(integer) -2"
        if entry.expire_at is None:
            return "(integer) -1"

        remaining = int(entry.expire_at - time.time())
        if remaining < 0:
            remaining = 0
        return "(integer) " + str(remaining)

    def _purge_expired(self) -> None:
        now = time.time()

        while self.expirations.size() > 0:
            item = self.expirations.peek()
            if item is None:
                break
            expire_at, key = item
            if expire_at > now:
                break

            self.expirations.pop()
            entry = self.store.get(key)
            if entry is not None and entry.expire_at == expire_at:
                self._remove_key(key, evicted=False)

    def _delete_if_expired(self, key: str) -> bool:
        entry = self.store.get(key)
        if entry is None or entry.expire_at is None:
            return False

        if entry.expire_at <= time.time():
            self._remove_key(key, evicted=False)
            return True
        return False

    def _remove_key(self, key: str, evicted: bool) -> bool:
        entry = self.store.remove(key)
        if entry is None:
            return False

        self.used_memory -= self._entry_size(key, entry.value)
        self.lru.remove_node(entry.lru_node)
        entry.expire_at = None

        if evicted:
            self.evicted_keys += 1
        return True

    def _evict_until_within_limit(self) -> None:
        if self.maxmemory <= 0:
            return

        self._purge_expired()
        while self.used_memory > self.maxmemory and self.lru.tail is not None:
            oldest_key = self.lru.tail.data
            self._remove_key(oldest_key, evicted=True)

    def _entry_size(self, key: str, value: str) -> int:
        return len(key.encode("utf-8")) + len(value.encode("utf-8"))

    def _parse_int(self, text: str) -> Optional[int]:
        try:
            return int(text)
        except ValueError:
            return None

    def _parse_non_negative_int(self, text: str) -> Optional[int]:
        value = self._parse_int(text)
        if value is None or value < 0:
            return None
        return value
