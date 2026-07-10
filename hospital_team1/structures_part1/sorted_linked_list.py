"""Sorted singly linked list implemented without Python container helpers."""


class SortedListNode:
    def __init__(self, data):
        self.data = data
        self.next = None


class SortedLinkedList:
    """Keep elements sorted in ascending order according to <."""

    def __init__(self) -> None:
        self.head = None
        self._size = 0

    def insert(self, item) -> None:
        new_node = SortedListNode(item)
        self._size += 1

        if self.head is None or item < self.head.data:
            new_node.next = self.head
            self.head = new_node
            return

        current = self.head
        while current.next is not None and not (item < current.next.data):
            current = current.next

        new_node.next = current.next
        current.next = new_node

    def pop(self):
        if self.head is None:
            return None

        data = self.head.data
        self.head = self.head.next
        self._size -= 1
        return data

    def peek(self):
        if self.head is None:
            return None
        return self.head.data

    def to_list(self) -> list:
        result = []
        current = self.head
        while current is not None:
            result.append(current.data)
            current = current.next
        return result

    def is_empty(self) -> bool:
        return self._size == 0

    def __len__(self) -> int:
        return self._size
