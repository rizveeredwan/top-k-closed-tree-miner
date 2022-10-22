import heapq
import re


def event_enclose_check(event_A, event_B):
    # will check if event_A encloses event_B
    j = 0
    for i in range(0, len(event_B)):
        found = False
        while j < len(event_A):
            if event_B[i] == event_A[j]:
                j += 1
                found = True  # item found
                break
            elif event_B[i] < event_A[j]:  # A's item is bigger, can't hold B[i]
                break
            elif event_B[i] > event_A[j]:  # still a big item in A can be found
                j += 1
                continue
        if found is False:
            return False
    return True  # encloses


def two_pattern_enclose_check(A, B):
    # will check if A encloses B
    if len(B) > len(A):  # B is huge, A can never include B
        return False
    event_A, event_B = 0, 0
    while event_B < len(B):
        if event_A == len(A):
            return False  # all the events have been checked, not encloses
        verdict = event_enclose_check(event_A=A[event_A], event_B=B[event_B])
        if verdict is True:
            event_B += 1
        event_A += 1  # next event shift
    if event_B == len(B):
        return True  # A completely encloses B
    return False


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

    def insert(self, node, prev_node): # A->B
        if prev_node.next_link is not None:
            node.next_link = prev_node.next_link
        prev_node.next_link = node
        return

    def replace(self, old_linked_list_node, updated_cspm_tree_nodes):
        # A->B->C : A->(D->E)->C
        current_node = old_linked_list_node.prev
        ll_nodes = []
        for i in range(0, len(updated_cspm_tree_nodes)):
            ll_node = PatternExtensionLinkedList(node=updated_cspm_tree_nodes[i], level=old_linked_list_node.level+1)
            self.insert(node=ll_node, prev_node=current_node)
            current_node = ll_node
            ll_nodes.append(ll_node) # newly created linked list nodes
        del old_linked_list_node
        return ll_nodes


class ClosedPatternsLinkedList: # closed1->closed2->...
    # Linked list to store the closed patterns for a particular support mapped to dictionary
    # Linked list for storing the closed patterns
    def __init__(self):
        self.pattern = None
        self.cpsm_tree_nodes = None
        self.cspm_tree_node_bitset = None
        self.next = None
        self.prev = None

    def add(self, current, pattern, cspm_tree_nodes, cspm_tree_node_bitset):
        n = ClosedPatternsLinkedList()
        n.pattern = pattern
        n.cspm_tree_nodes = cspm_tree_nodes
        n.cspm_tree_node_bitset = cspm_tree_node_bitset

        current.next = n
        n.prev = current
        return

    def delete(self, current):
        if current.prev is not None:
            current.prev.next = current
        save = current.prev
        del current
        return save


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
        self.flag = None # [0: Can never be closed, None: no decision]
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
            assert(NODE_MAPPER is not None)
            # nodes are provided using bitset (implicit provided)
            cspm_tree_nodes = []
            number = linked_list_node.cspm_tree_node_bitset
            while number > 0:
                value = number & (-number)
                cspm_tree_nodes.append(NODE_MAPPER[value])
                number = number ^ value
            return cspm_tree_nodes


class CapheNode:
    # Candidate Pattern Max Heap
    def __init__(self, support): # single node multiple pattern
        self.support = support
        temp = CandidatePatternLinkedListNode()
        self.pattern_ll_node = [temp, temp] # head with pattern None, end with pattern none
        self.idx_in_heap = -1 # where the node is in heap

    def __lt__(self, other):
        if self.support < other.support:  # comparison between supports, higher support will come earlier
            return True
        return False

    def insert_pattern(self, caphe_node, pattern, cspm_tree_nodes, cspm_tree_node_bitset, s_ex, i_ex, flag=None):
        # adding patterns as ll list, new pattern to explore
        # adding after en
        current = caphe_node.pattern_ll_node[1]
        pattern_ll_node = current.create_node(pattern=pattern, cspm_tree_node_bitset=cspm_tree_node_bitset,
                                              cspm_tree_nodes=cspm_tree_nodes, current=current, s_ex=s_ex, i_ex=i_ex, flag=flag)
        # new ending node
        caphe_node.pattern_ll_node[1] = pattern_ll_node
        return pattern_ll_node

    def pop_last_element(self, caphe_node, NODE_MAPPER=None): # extracting the last pattern and its information from a node
        assert(caphe_node is not None)
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
        else: # no pattern in the bucket
            return None # no entry here


class Caphe:
    def __init__(self):
        self.nodes = [] # where all the Caphe nodes are kept

    def find_parent_idx(self, number):
        if number%2 == 1:
            return int(number/2)
        if number%2 == 0:
            return int(number/2)-1

    def push(self, caphe_node):
        # pushing in heap
        self.nodes.append(caphe_node)
        # improve it
        current_idx = len(self.nodes)-1
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

    def front(self): # O(1)
        # top of heap
        return self.nodes[0]

    def sort_nodes(self, current_idx): # O(logn)
        # can only go bottom
        while True:
            left = 2 * current_idx + 1
            right = 2 * current_idx + 2
            _list = [(current_idx, self.nodes[current_idx])]
            if right < len(self.nodes):
                _list.append((right, self.nodes[right]))
            if left < len(self.nodes):
                _list.append((left, self.nodes[left]))
            _list.sort(key=lambda x:x[1], reverse=True) # sorting the nodes
            if _list[0][0] == current_idx: # parent have the highest value
                self.nodes[current_idx].idx_in_heap = current_idx
                break
            else:
                self.swap(current_idx, _list[0][0])
                current_idx = _list[0][0]

    def pop(self, special_node=None): # O(logn)
        # pop from heap
        if special_node is None: # remove top
            self.swap(0, len(self.nodes)-1)
            del self.nodes[-1]
            self.sort_nodes(current_idx=0) 
        else: # arbitrary node
            idx = special_node.idx_in_heap
            self.swap(idx, len(self.nodes)-1)
            del self.nodes[-1]
            self.sort_nodes(current_idx=idx)

    def print(self):
        for i in range(0, len(self.nodes)):
            print(self.nodes[i].support, self.nodes[i].pattern,  self.nodes[i].idx_in_heap)
        print()


class MaxHeap:
    # max heap to control which patterns have the most frequency
    def __init__(self, node, cspm_tree_nodes):
        self.node = node
        self.cspm_tree_nodes = cspm_tree_nodes

    def __lt__(self, other):
        if self.node.support < other.node.support:  # comparison between supports, higher support will come earlier
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


class DataStructure:
    def __init__(self):
        # E.g., 6: {0: all cosed, 1: intermediate}
        self.support_table = {}

    def insert(self, support, pattern, cspm_tree_node_bitset, cspm_tree_nodes, NODE_MAPPER=None,
               type_of_extension=0):
        # inserting a pattern in support table
        if self.support_table.get(support) is None:
            h1, h2 = CandidatePatternLinkedListNode(), CandidatePatternLinkedListNode()  # two heads for closed and intermediate
            self.support_table[support] = {0: [h1, h1], 1: [h2, h2]}  # creating head and tail
        # getting the status
        # first sending the linked list of closed nodes, having the condition
        # clo_absorption_status_new: new pattern is absorbing which old nodes
        # clo_absorption_status_old: which old nodes are absorbing new pattern
        clo_absorption_status_new, clo_absorption_status_old = self.check_closed_status(pattern_p=pattern,
                                                                                        cspm_tree_nodes=cspm_tree_nodes,
                                                                                        linked_list_of_nodes_head=
                                                                                        self.support_table[support][0][
                                                                                            1],
                                                                                        NODE_MAPPER=NODE_MAPPER,
                                                                                        type_of_extension=type_of_extension)
        final_status = None # None, closed/0, intermediate/1
        if len(clo_absorption_status_new) > 0 and len(clo_absorption_status_old) > 0:
            # old_B absorbing A, A absorbing old_C: not possible
            ERROR = False
            print("Circuler closed pattern problem")
            assert (ERROR == True)
        if len(clo_absorption_status_new) == 0 and len(clo_absorption_status_old) == 0:
            final_status = 0 # closed
        if len(clo_absorption_status_new) > 0 and len(clo_absorption_status_old) == 0:
            # new pattern is absorbing some old patterns: new pattern is closed
            final_status = 0 # closed 
        if len(clo_absorption_status_new) == 0 and len(clo_absorption_status_old) > 0:
            # some old patterns is absorbing the new one
            pass
        # decision to put the given pattern as closed/intermediate
        if final_status == 0: # putting it in the closed linked list
            parent = self.support_table[support][0][1]
            end = parent.create_node(pattern=pattern, current=parent,
                                     cspm_tree_node_bitset=cspm_tree_node_bitset, cspm_tree_nodes=cspm_tree_nodes)
            self.support_table[support][0][1] = end
        elif final_status == 1: # putting it in the closed linked list
            parent = self.support_table[support][1][1]
            end = parent.create_node(pattern=pattern, current=parent,
                                     cspm_tree_node_bitset=cspm_tree_node_bitset, cspm_tree_nodes=cspm_tree_nodes)
            self.support_table[support][0][1] = end

    def check_closed_status(self, pattern_p, cspm_tree_nodes, linked_list_of_nodes_head, NODE_MAPPER,
                            type_of_extension):
        # pattern_p = [[1, 2, 3], [2, 4]]
        # need to check if pattern_p encloses some linked nodes of linked_list_of_nodes_head
        curr = linked_list_of_nodes_head
        assert (curr.pattern is None)  # generic head
        curr = curr.next
        pattern_status = 0  # 0->closed, 1:intermediate, None: nothing to do
        absorption_status_new = []
        absorption_status_old = []
        while curr is not None:  # if curr is none then break
            if two_pattern_enclose_check(A=pattern_p, B=curr.pattern) is True:  # new (A) encloses old(B)
                nodes_of_A = cspm_tree_nodes
                nodes_of_B = curr.extract_cspm_tree_nodes(linked_list_node=curr, NODE_MAPPER=NODE_MAPPER)
                absorption_status_new.append([curr, 0])  # only pattern absorption
                # seeing if the nodes are also absorbed or not
                node_absorption = self.pattern_absorption_by_node_presence(nodes_of_A=nodes_of_A,
                                                                           nodes_of_B=nodes_of_B,
                                                                           type_of_extension=type_of_extension)
                if node_absorption is True:
                    absorption_status_new[-1][1] = 1
            elif two_pattern_enclose_check(A=curr.pattern, B=pattern_p) is True:  # old encloses new
                nodes_of_A = curr.extract_cspm_tree_nodes(linked_list_node=curr, NODE_MAPPER=NODE_MAPPER)
                nodes_of_B = cspm_tree_nodes
                absorption_status_old.append([curr, 0])  # only pattern absorption
                # seeing if the nodes are also absorbed or not
                node_absorption = self.pattern_absorption_by_node_presence(nodes_of_A=nodes_of_A,
                                                                           nodes_of_B=nodes_of_B,
                                                                           type_of_extension=type_of_extension)
                if node_absorption is True:
                    absorption_status_old[-1][1] = 1  # node is also absorbed
            curr = curr.next
        return absorption_status_new, absorption_status_old  # new nodes absorbing which, old nodes which absorbing new node

    def same_subtree_checking(self, pattern_node, super_pattern_node):
        # if supper_pattern_node and pattern_node are in the same subtree or not
        for i in range(0, len(pattern_node.subtree_detection_code)):
            if len(super_pattern_node.subtree_detection_code) - 1 >= i and \
                    super_pattern_node.subtree_detection_code[i] == pattern_node.subtree_detection_code[i]:
                continue
            elif len(super_pattern_node.subtree_detection_code) - 1 >= i and \
                    super_pattern_node.subtree_detection_code[i] < pattern_node.subtree_detection_code[i]:
                return -1  # small
            elif len(super_pattern_node.subtree_detection_code) - 1 >= i and \
                    super_pattern_node.subtree_detection_code[i] > pattern_node.subtree_detection_code[i]:
                return 1  # big
        return 0  # perfectly matched

    def pattern_absorption_by_node_presence(self, nodes_of_A, nodes_of_B, type_of_extension):
        # A has enclosed B, type of extension 0(IE) and 1(SE)
        # decision if it is enough to keep A only
        if type_of_extension == 0:  # IE A = {a, b, c}l B = {a, c}
            # same subtree, same event number
            a_ptr, b_ptr = 0, 0
            assert (len(nodes_of_A) >= len(nodes_of_B))  # as in underlying and super pattern
            while a_ptr < len(nodes_of_A):
                subtree_verdict = self.same_subtree_checking(pattern_node=nodes_of_B[b_ptr],
                                                             super_pattern_node=nodes_of_A[a_ptr])
                assert (subtree_verdict <= 0)
                if subtree_verdict == 0 and nodes_of_A[a_ptr].event_no == nodes_of_B[b_ptr].event_no:
                    # same subtree and same event number, super pattern should be enough
                    a_ptr += 1
                elif subtree_verdict == 0 and nodes_of_A[a_ptr].event_no > nodes_of_B[b_ptr].event_no:
                    return False  # A can not completely absorb B, A's occurrence not in the same event
                elif subtree_verdict < 0:
                    b_ptr += 1
            return True  # A can fully absorb B including nodes , ends in same event always
        elif type_of_extension == 1:
            pass
        pass


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


