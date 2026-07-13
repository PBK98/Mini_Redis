"""체이닝 방식으로 구현한 해시맵.

Python 내장 매핑 타입에 키 조회를 맡기지 않고,
과제의 핵심 자료구조 동작이 코드에 드러나도록 구현한다.
"""


class HashNode:
    """버킷 체인 안에 저장되는 단일 키/값 노드."""

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None


class HashMap:
    """직접 만든 해시 함수, 체이닝, 자동 확장을 사용하는 해시맵."""

    def __init__(self, initial_capacity=8):
        self.capacity = initial_capacity
        self.buckets = [None] * self.capacity
        self.count = 0

    def _hash(self, key):
        """UTF-8 바이트를 사용하는 단순 다항 롤링 해시."""
        total = 0
        for byte in key.encode("utf-8"):
            total = (total * 31 + byte) % self.capacity
        return total

    def _load_factor(self):
        return self.count / self.capacity

    def _resize_if_needed(self):
        if self._load_factor() <= 0.75:
            return

        old_buckets = self.buckets
        self.capacity *= 2
        self.buckets = [None] * self.capacity
        old_count = self.count
        self.count = 0

        for bucket in old_buckets:
            current = bucket
            while current is not None:
                self.put(current.key, current.value)
                current = current.next

        if self.count != old_count:
            raise RuntimeError(
                "해시맵 리사이즈 중 키 개수가 일치하지 않습니다. 리사이즈 전: "
                + str(old_count)
                + ", 리사이즈 후: "
                + str(self.count)
            )

    def put(self, key, value):
        """키에 해당하는 값을 삽입하거나 덮어쓴다."""
        index = self._hash(key)
        current = self.buckets[index]

        while current is not None:
            if current.key == key:
                current.value = value
                return
            current = current.next

        node = HashNode(key, value)
        node.next = self.buckets[index]
        self.buckets[index] = node
        self.count += 1
        self._resize_if_needed()

    def get(self, key):
        """저장된 값을 반환하고, 없으면 None을 반환한다."""
        index = self._hash(key)
        current = self.buckets[index]

        while current is not None:
            if current.key == key:
                return current.value
            current = current.next

        return None

    def remove(self, key):
        """키를 삭제하고 값을 반환한다. 없으면 None을 반환한다."""
        index = self._hash(key)
        current = self.buckets[index]
        previous = None

        while current is not None:
            if current.key == key:
                if previous is None:
                    self.buckets[index] = current.next
                else:
                    previous.next = current.next
                self.count -= 1
                return current.value
            previous = current
            current = current.next

        return None

    def contains(self, key):
        return self.get(key) is not None

    def keys(self):
        """전체 키를 일반 리스트로 반환한다."""
        result = []
        for bucket in self.buckets:
            current = bucket
            while current is not None:
                result.append(current.key)
                current = current.next
        return result

    def size(self):
        return self.count
