"""Minimal heap helpers implemented without Python's heapq module."""


def heappush(heap: list, item) -> None:
    """Push an item into the heap and preserve min-heap order."""
    heap.append(item)
    _sift_up(heap, len(heap) - 1)


def heappop(heap: list):
    """Pop and return the smallest item from the heap."""
    if not heap:
        raise IndexError("heappop from empty heap")
    if len(heap) == 1:
        return heap.pop()

    top = heap[0]
    heap[0] = heap.pop()
    _sift_down(heap, 0)
    return top


def _sift_up(heap: list, index: int) -> None:
    """Move a node upward until the min-heap property is restored."""
    while index > 0:
        parent = (index - 1) // 2
        if heap[index] < heap[parent]:
            heap[index], heap[parent] = heap[parent], heap[index]
            index = parent
        else:
            break


def _sift_down(heap: list, index: int) -> None:
    """Move a node downward until the min-heap property is restored."""
    size = len(heap)
    while True:
        smallest = index
        left = 2 * index + 1
        right = 2 * index + 2

        if left < size and heap[left] < heap[smallest]:
            smallest = left
        if right < size and heap[right] < heap[smallest]:
            smallest = right

        if smallest != index:
            heap[index], heap[smallest] = heap[smallest], heap[index]
            index = smallest
        else:
            break
