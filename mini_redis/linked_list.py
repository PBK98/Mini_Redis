"""Doubly linked list used for O(1) LRU ordering."""


class ListNode:
    """A node with prev, next, and data fields as required by the mission."""

    def __init__(self, data):
        self.prev = None
        self.next = None
        self.data = data


class DoublyLinkedList:
    """Doubly linked list with constant-time insert, remove, and move."""

    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def insert_front(self, data):
        """Insert data at the front and return the created node."""
        node = ListNode(data)
        node.next = self.head

        if self.head is not None:
            self.head.prev = node
        else:
            self.tail = node

        self.head = node
        self.length += 1
        return node

    def insert_back(self, data):
        """Insert data at the back and return the created node."""
        node = ListNode(data)
        node.prev = self.tail

        if self.tail is not None:
            self.tail.next = node
        else:
            self.head = node

        self.tail = node
        self.length += 1
        return node

    def remove_front(self):
        """Remove and return front data, or None when empty."""
        if self.head is None:
            return None
        return self.remove_node(self.head)

    def remove_back(self):
        """Remove and return back data, or None when empty."""
        if self.tail is None:
            return None
        return self.remove_node(self.tail)

    def remove_node(self, node):
        """Remove a known node in O(1) and return its data."""
        if node is None:
            return None

        if node.prev is not None:
            node.prev.next = node.next
        else:
            self.head = node.next

        if node.next is not None:
            node.next.prev = node.prev
        else:
            self.tail = node.prev

        data = node.data
        node.prev = None
        node.next = None
        self.length -= 1
        return data

    def move_to_front(self, node):
        """Move an existing node to the front in O(1)."""
        if node is None or node is self.head:
            return node

        data = self.remove_node(node)
        return self.insert_front(data)

    def size(self):
        return self.length
