import heapq


class PatternLinkedListNode:
    # representing a particular pattern node of linked list
    def __init__(self):
        self.pattern = None  # [[1, 2]]
        self.next = None
        self.prev = None
        self.cspm_tree_node_bitset = None  # [1, 2] -> [110]

    def create_node(self, pattern, cspm_tree_node_bitset, current):
        n = PatternLinkedListNode()
        n.pattern = pattern
        n.cspm_tree_node_bitset = cspm_tree_node_bitset
        current.next = n
        n.prev = current
        return n

    def delete_node(self, node):
        if node.prev is not None and node.next is not None:
            node.prev.next = node.next
        del node
        return


class MaxHeap:
    # max heap to control which patterns have the most frequency
    def __init__(self, node):
        self.node = node

    def __lt__(self, other):
        if self.node.support < other.node.support: # comparison between supports, higher support will come earlier
            return False
        return True


class DataStructure:
    def __init__(self):
        # E.g., 6: {0: all cosed, 1: intermediate}
        self.support_table = {}

    def insert(self, support, pattern, cspm_tree_node_bitset, biased_entry=False):
        # inserting a pattern in support table
        if self.support_table.get(support) is None:
            h1, h2 = PatternLinkedListNode(), PatternLinkedListNode()  # two heads for closed and intermediate
            self.support_table[support] = {0: [h1, h1], 1: [h2, h2]}  # creating head and tail
        if biased_entry is True:
            # creating normal biased entry without checking
            parent = self.support_table[support][0][1]
            end = parent.create_node(pattern=pattern, current=parent,
                                     cspm_tree_node_bitset=cspm_tree_node_bitset)
            self.support_table[support][0][1] = end


"""
if __name__ == '__main__':
    obj1 = MaxHeap(10, None)
    obj2 = MaxHeap(20, None)
    obj3 = MaxHeap(30, None)
    H = []
    heapq.heapify(H)
    heapq.heappush(H, obj1)
    heapq.heappush(H, obj2)
    heapq.heappush(H, obj3)
    heapq.heappush(H, obj2)
    while len(H) > 0:
        u = heapq.heappop(H)
        print(u.priority)
"""