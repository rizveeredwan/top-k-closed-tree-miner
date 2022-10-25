import heapq
import re
from collections import deque


def generate_cspm_tree_nodes_from_bitset(cspm_tree_node_bitset, NODE_MAPPER):
    # nodes are generated from the bitset
    assert(cspm_tree_node_bitset is not None and NODE_MAPPER is not None)
    # nodes are provided using bitset (implicit provided)
    cspm_tree_nodes = []
    number = cspm_tree_node_bitset
    while number > 0:
        value = number & (-number)
        cspm_tree_nodes.append(NODE_MAPPER[value])
        number = number ^ value
    return cspm_tree_nodes


class SupportTableEntry:
    def __init__(self):
        self.closed_patterns = ClosedPatternsLinkedList()
        self.caphe_node = None


class PatternExtensionLinkedList:
    # Linkedlist used during pattern extension using breadth-first search
    # to process the nodes during extension in O(N) complexity, no sorting required here
    # all the nodes will follow the same subtree code's ascending order
    def __init__(self, node, level):
        self.node = node
        self.level = level
        self.prev_link = None
        self.next_link = None

    def insert(self, node, prev_node):  # A->B
        if prev_node.next_link is not None:
            node.next_link = prev_node.next_link
            node.prev_link = prev_node
            prev_node.next_link = node
        else:
            prev_node.next_link = node
            node.prev_link = prev_node
        return

    def value_update(self, ll_node, cspm_tree_node, level):
        ll_node.node = cspm_tree_node
        ll_node.level = level
        return

    def replace(self, old_linked_list_node, updated_cspm_tree_nodes):
        # A->B->C : A->(D->E)->C
        current_node = old_linked_list_node
        old_level = old_linked_list_node.level
        ll_nodes = []
        for i in range(0, len(updated_cspm_tree_nodes)):
            if i == 0:
                # current node's value is replaced
                self.value_update(ll_node=current_node, cspm_tree_node=updated_cspm_tree_nodes[i],
                                  level=old_level + 1)
            else:
                # adding new nodes after current node
                ll_node = PatternExtensionLinkedList(node=updated_cspm_tree_nodes[i], level=old_level + 1)
                self.insert(node=ll_node, prev_node=current_node)
                current_node = ll_node
            ll_nodes.append(current_node)  # newly created linked list nodes
        del old_linked_list_node
        return ll_nodes


class ClosedPatternsLinkedList:  # closed1->closed2->...
    # Linked list to store the closed patterns for a particular support mapped to dictionary
    # Linked list for storing the closed patterns
    def __init__(self):
        self.pattern = None
        self.cpsm_tree_nodes = None
        self.cspm_tree_node_bitset = None
        self.next = None
        self.prev = None

    def insert(self, current, pattern, cspm_tree_nodes, cspm_tree_node_bitset):
        # adding a closed pattern at the end
        n = ClosedPatternsLinkedList()
        n.pattern = pattern
        n.cspm_tree_nodes = cspm_tree_nodes
        n.cspm_tree_node_bitset = cspm_tree_node_bitset
        if current.next is not None:
            n.next = current.next
            n.prev = current
            current.next.prev = n
            current.next = n
        else:
            current.next = n
            n.prev = current
        return

    def delete(self, current):
        # deleting current node
        if current.next is not None:
            current.prev.next = current.next
        del current

    def print(self):
        # traversing from bottom to the main node
        print("printing the cosed nodes")
        st = self
        while st is not None:
            print(st.pattern)
            st = st.next
        return


class CandidatePatternLinkedListNode:
    # representing a particular pattern node of linked list, deletion of any type
    # Linked list for storing the candidate patterns
    def __init__(self):
        self.pattern = None  # [[1, 2]]
        # any one of them will be activated
        self.cspm_tree_node_bitset = None  # [1, 2] -> [110]: node ids bitset representation
        self.cspm_tree_nodes = None  # node representation
        self.s_ex = None
        self.i_ex = None
        self.flag = None  # [0: Can never be closed, None: no decision]
        # linked lists
        self.next = None
        self.prev = None

    def create_node(self, pattern, cspm_tree_node_bitset, current, cspm_tree_nodes, s_ex, i_ex, flag=None):
        n = CandidatePatternLinkedListNode()
        n.pattern = pattern
        n.cspm_tree_node_bitset = cspm_tree_node_bitset
        n.cspm_tree_nodes = cspm_tree_nodes
        n.s_ex = s_ex
        n.i_ex = i_ex
        n.flag = flag
        # creating the links
        current.next = n
        n.prev = current
        return n

    def delete_node(self, node):
        # this function is not used still
        if node.prev is not None and node.next is not None:
            node.prev.next = node.next
        del node
        return

    def extract_cspm_tree_nodes(self, linked_list_node, NODE_MAPPER=None):
        # extracting the cspm tree nodes for a particular linked list node
        if linked_list_node is not None and linked_list_node.cspm_tree_nodes is not None:
            # nodes are explicitly provided
            return linked_list_node.cspm_tree_nodes
        elif linked_list_node is not None and linked_list_node.cspm_tree_node_bitset is not None:
            cspm_tree_nodes = generate_cspm_tree_nodes_from_bitset(linked_list_node.cspm_tree_node_bitset, NODE_MAPPER)
            return cspm_tree_nodes


class CapheNode:
    # Candidate Pattern Max Heap
    def __init__(self, support):  # single node multiple pattern
        self.support = support
        temp = CandidatePatternLinkedListNode()
        self.pattern_ll_node = [temp, temp]  # head with pattern None, end with pattern none
        self.idx_in_heap = -1  # where the node is in heap

    def __lt__(self, other):
        if self.support < other.support:  # comparison between supports, higher support will come earlier
            return True
        return False

    def insert_pattern(self, caphe_node, pattern, cspm_tree_nodes, cspm_tree_node_bitset, s_ex, i_ex, flag=None):
        # adding patterns as ll list, new pattern to explore
        # adding after end
        # print("caphe ", caphe_node, pattern)
        # print("before ")
        # caphe_node.print_caphe_node()
        current = caphe_node.pattern_ll_node[1]
        pattern_ll_node = current.create_node(pattern=pattern, cspm_tree_node_bitset=cspm_tree_node_bitset,
                                              cspm_tree_nodes=cspm_tree_nodes, current=current, s_ex=s_ex, i_ex=i_ex,
                                              flag=flag)
        # new ending node
        caphe_node.pattern_ll_node[1] = pattern_ll_node
        # caphe_node.print_caphe_node()
        return pattern_ll_node

    def pop_last_element(self, caphe_node,
                         NODE_MAPPER=None):  # extracting the last pattern and its information from a node
        assert (caphe_node is not None)
        if caphe_node.pattern_ll_node[0] != caphe_node.pattern_ll_node[1]:
            # some patterns in the bucket
            pattern_ll_node = caphe_node.pattern_ll_node[1]
            caphe_node.pattern_ll_node[1].prev.next = None
            caphe_node.pattern_ll_node[1] = pattern_ll_node.prev

            pattern = pattern_ll_node.pattern
            cspm_tree_nodes = pattern_ll_node.extract_cspm_tree_nodes(linked_list_node=pattern_ll_node,
                                                                      NODE_MAPPER=NODE_MAPPER)
            cspm_tree_node_bitset = pattern_ll_node.cspm_tree_node_bitset
            s_ex = pattern_ll_node.s_ex
            i_ex = pattern_ll_node.i_ex
            flag = pattern_ll_node.flag
            del pattern_ll_node
            return pattern, cspm_tree_nodes, cspm_tree_node_bitset, s_ex, i_ex, flag
        else:  # no pattern in the bucket
            return None  # no entry here

    def print_caphe_node(self):
        print("Printing the candidates in caphe node")
        st = self.pattern_ll_node[0]
        en = self.pattern_ll_node[1]
        while st != None:
            print(st.pattern)
            st = st.next


class Caphe:
    def __init__(self):
        self.nodes = []  # where all the Caphe nodes are kept

    def find_parent_idx(self, number):
        if number % 2 == 1:
            return int(number / 2)
        if number % 2 == 0:
            return int(number / 2) - 1

    def push(self, caphe_node):
        # pushing in heap
        self.nodes.append(caphe_node)
        caphe_node.idx_in_heap = len(self.nodes) - 1
        # improve it
        current_idx = len(self.nodes) - 1
        while current_idx > 0:
            par_idx = self.find_parent_idx(number=current_idx)
            if par_idx < 0:
                return
            if self.nodes[par_idx] < self.nodes[current_idx]:
                self.swap(par_idx, current_idx)
                current_idx = par_idx
            else:
                self.nodes[current_idx].idx_in_heap = current_idx
                break

    def swap(self, i, j):
        temp = self.nodes[i]
        self.nodes[i] = self.nodes[j]
        self.nodes[j] = temp
        # main reference node is remembering where it is in the max heap
        self.nodes[j].idx_in_heap = j
        self.nodes[i].idx_in_heap = i

    def front(self):  # O(1)
        # top of heap
        return self.nodes[0]

    def sort_nodes(self, current_idx):  # O(logn)
        # can only go bottom
        while True:
            left = 2 * current_idx + 1
            right = 2 * current_idx + 2
            _list = [(current_idx, self.nodes[current_idx])]
            if right < len(self.nodes):
                _list.append((right, self.nodes[right]))
            if left < len(self.nodes):
                _list.append((left, self.nodes[left]))
            _list.sort(key=lambda x: x[1], reverse=True)  # sorting the nodes
            if _list[0][0] == current_idx:  # parent have the highest value
                self.nodes[current_idx].idx_in_heap = current_idx
                break
            else:
                self.swap(current_idx, _list[0][0])
                current_idx = _list[0][0]

    def pop(self, special_node=None):  # O(logn)
        if len(self.nodes) == 0:
            return
        # pop from heap
        if special_node is None:  # remove top
            self.swap(0, len(self.nodes) - 1)
            del self.nodes[-1]
            if len(self.nodes) > 0:
                self.sort_nodes(current_idx=0)
        else:  # arbitrary node
            idx = special_node.idx_in_heap
            self.swap(idx, len(self.nodes) - 1)
            del self.nodes[-1]
            if len(self.nodes) > 0:
                self.sort_nodes(current_idx=idx)

    def print(self):
        for i in range(0, len(self.nodes)):
            print(self.nodes[i].support, self.nodes[i].idx_in_heap)
        print()


class SimultaneousPatternExtensionMaxHeap:
    # max heap to control which patterns have the most frequency
    def __init__(self, support, item, ex_type, cspm_tree_nodes):
        self.support = support  # intial support
        self.item = item  # 1, 2, 3, etc
        self.ex_type = ex_type  # 0:SE/1:IE
        self.queue_pattern_ex_ll_nodes = deque([])
        current = PatternExtensionLinkedList(node=None, level=None)
        self.head = current  # to traverse and get the patterns
        for i in range(0, len(cspm_tree_nodes)):
            n = PatternExtensionLinkedList(node=cspm_tree_nodes, level=0)
            current.insert(node=n, prev_node=current)
            self.queue_pattern_ex_ll_nodes.append(n)
            current = n

    def __lt__(self, other):
        if self.support < other.support:  # comparison between supports, higher support will come earlier
            return False
        return True


class MinHeap:
    # min heap to hold the support only
    def __init__(self, priority):
        self.priority = priority

    def __lt__(self, other):
        if self.priority < other.priority:
            return True
        return False


if __name__ == '__main__':
    pass
    """
    import random
    caphe = Caphe()
    for i in range(0, 10):
        c1 = CapheNode(support=random.randint(1, 10), pattern=random.randint(1, 100), cspm_tree_nodes=None,
                       cspm_tree_node_bitset=None)
        caphe.push(caphe_node=c1)

    caphe.print()

    caphe.pop()
    caphe.print()

    caphe.pop()
    caphe.print()
    """
