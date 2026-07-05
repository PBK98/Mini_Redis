"""O(1) LRU 순서 관리에 사용하는 이중 연결 리스트."""


class ListNode:
    """과제 요구사항에 맞게 prev, next, data 필드를 가진 노드."""

    def __init__(self, data):
        self.prev = None
        self.next = None
        self.data = data


class DoublyLinkedList:
    """삽입, 삭제, 이동을 상수 시간에 수행하는 이중 연결 리스트."""

    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0

    def insert_front(self, data):
        """데이터를 맨 앞에 삽입하고 생성된 노드를 반환한다."""
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
        """데이터를 맨 뒤에 삽입하고 생성된 노드를 반환한다."""
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
        """맨 앞 데이터를 삭제해 반환하고, 비어 있으면 None을 반환한다."""
        if self.head is None:
            return None
        return self.remove_node(self.head)

    def remove_back(self):
        """맨 뒤 데이터를 삭제해 반환하고, 비어 있으면 None을 반환한다."""
        if self.tail is None:
            return None
        return self.remove_node(self.tail)

    def remove_node(self, node):
        """이미 알고 있는 노드를 O(1)에 삭제하고 데이터를 반환한다."""
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
        """기존 노드를 O(1)에 맨 앞으로 이동한다."""
        if node is None or node is self.head:
            return node

        data = self.remove_node(node)
        return self.insert_front(data)

    def size(self):
        return self.length
