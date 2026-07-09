"""自写最小堆（min-heap），不依赖 Python 标准库 heapq 模块。

用数组（list）实现二叉堆，索引从 0 开始：
- 节点 i 的父节点 = (i - 1) // 2
- 节点 i 的左子节点 = 2 * i + 1
- 节点 i 的右子节点 = 2 * i + 2

堆顶（heap[0]）始终是全局最小值。
"""


def heappush(heap: list, item) -> None:
    """向堆中插入一个元素，保持最小堆性质。

    步骤：
    1. 把新元素追加到数组末尾
    2. 调用 _sift_up 将其上浮到正确位置

    时间复杂度：O(log n)
    """
    heap.append(item)
    _sift_up(heap, len(heap) - 1)


def heappop(heap: list):
    """弹出并返回堆中最小的元素（堆顶）。

    步骤：
    1. 空堆抛 IndexError —— 和标准库 heapq 行为一致
    2. 只有一个元素直接 pop，不需要调整
    3. 否则取出堆顶，把最后一个元素移到堆顶，然后调用 _sift_down 下沉

    时间复杂度：O(log n)
    """
    if not heap:
        raise IndexError("heappop from empty heap")
    if len(heap) == 1:
        return heap.pop()

    top = heap[0]
    heap[0] = heap.pop()       # 末元素提到堆顶
    _sift_down(heap, 0)        # 向下调整，恢复堆序
    return top


def _sift_up(heap: list, index: int) -> None:
    """上浮：把 index 位置的元素向根部方向移动，直到最小堆性质恢复。

    逻辑：
    - 反复和父节点比较
    - 当前节点 < 父节点 → 交换，继续向上
    - 当前节点 >= 父节点 → 停止（堆序满足）
    """
    while index > 0:
        parent = (index - 1) // 2
        if heap[index] < heap[parent]:
            heap[index], heap[parent] = heap[parent], heap[index]
            index = parent
        else:
            break


def _sift_down(heap: list, index: int) -> None:
    """下沉：把 index 位置的元素向叶子方向移动，直到最小堆性质恢复。

    逻辑：
    - 在当前节点和左右子节点中找最小值
    - 最小值不是当前节点 → 交换，继续向下
    - 最小值就是当前节点 → 停止（堆序满足）
    """
    size = len(heap)
    while True:
        smallest = index
        left = 2 * index + 1
        right = 2 * index + 2

        # 找三者中最小的
        if left < size and heap[left] < heap[smallest]:
            smallest = left
        if right < size and heap[right] < heap[smallest]:
            smallest = right

        if smallest != index:
            heap[index], heap[smallest] = heap[smallest], heap[index]
            index = smallest
        else:
            break
