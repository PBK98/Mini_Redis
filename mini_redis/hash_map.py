"""Hash map implemented with separate chaining.

The implementation keeps the mission's core data-structure behavior visible
instead of delegating key lookup to Python's built-in mapping types.
"""


class HashNode:
    """A single key/value node stored inside a bucket chain."""

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None


class HashMap:
    """Hash map with custom hash function, chaining, and automatic resizing."""

    def __init__(self, initial_capacity=8):
        self.capacity = initial_capacity
        self.buckets = [None] * self.capacity
        self.count = 0

    def _hash(self, key):
        """A simple polynomial rolling hash over UTF-8 bytes."""
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

        self.count = old_count

    def put(self, key, value):
        """Insert or overwrite a value by key."""
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
        """Return the stored value, or None when absent."""
        index = self._hash(key)
        current = self.buckets[index]

        while current is not None:
            if current.key == key:
                return current.value
            current = current.next

        return None

    def remove(self, key):
        """Remove a key and return its value, or None when absent."""
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
        """Return all keys as a plain list."""
        result = []
        for bucket in self.buckets:
            current = bucket
            while current is not None:
                result.append(current.key)
                current = current.next
        return result

    def size(self):
        return self.count
