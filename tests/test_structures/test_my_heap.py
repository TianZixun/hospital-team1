import unittest

from hospital_team1.structures import heappop, heappush


class TestMyHeap(unittest.TestCase):
    def test_heappush_keeps_smallest_item_at_top(self) -> None:
        heap: list[int] = []

        for value in [5, 3, 8, 1, 4]:
            heappush(heap, value)

        self.assertEqual(heap[0], 1)

    def test_heappop_returns_values_in_ascending_order(self) -> None:
        heap: list[int] = []
        for value in [7, 2, 9, 2, 5]:
            heappush(heap, value)

        popped = [heappop(heap) for _ in range(5)]

        self.assertEqual(popped, [2, 2, 5, 7, 9])
        self.assertEqual(heap, [])

    def test_heappop_raises_error_for_empty_heap(self) -> None:
        with self.assertRaises(IndexError):
            heappop([])


if __name__ == "__main__":
    unittest.main()
