import unittest

from hospital_team1.structures import SortedLinkedList


class TestSortedLinkedList(unittest.TestCase):
    def test_insert_keeps_values_sorted(self) -> None:
        linked_list = SortedLinkedList()
        for value in [4, 1, 3, 2]:
            linked_list.insert(value)

        self.assertEqual(linked_list.to_list(), [1, 2, 3, 4])
        self.assertEqual(linked_list.peek(), 1)
        self.assertEqual(len(linked_list), 4)

    def test_pop_returns_smallest_value(self) -> None:
        linked_list = SortedLinkedList()
        linked_list.insert(3)
        linked_list.insert(1)

        self.assertEqual(linked_list.pop(), 1)
        self.assertEqual(linked_list.pop(), 3)
        self.assertIsNone(linked_list.pop())
        self.assertTrue(linked_list.is_empty())


if __name__ == "__main__":
    unittest.main()
