import heapq
import re
from collections import deque

import debug_functions


def generate_cspm_tree_nodes_from_bitset(cspm_tree_node_bitset, NODE_MAPPER):
    # nodes are generated from the bitset
    assert (cspm_tree_node_bitset is not None and NODE_MAPPER is not None)
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
        # linked list version
        self.closed_patterns = ClosedPatternsLinkedList()
        # Trie version
        temp = PatternTrie()
        self.closed_patterns_with_trie = [temp, temp]
        self.caphe_node = None

    def add_closed_pattern(self, support_table_entry, pattern, cspm_tree_nodes, cspm_tree_node_bitset):
        #print(f"closed e came {pattern} {support_table_entry.closed_patterns_with_trie[0].pattern} "
        #      f"{support_table_entry.closed_patterns_with_trie[1].pattern}",)
        #if support_table_entry.closed_patterns_with_trie[1].prev is not None:
            # print(f"{support_table_entry.closed_patterns_with_trie[1].prev.pattern}")
        # adding a closed pattern in the trie
        root = support_table_entry.closed_patterns_with_trie[0]
        assert (isinstance(root, PatternTrie))
        new_node = root.insert(root=root, pattern=pattern, current_end=support_table_entry.closed_patterns_with_trie[1],
                               cspm_tree_nodes=cspm_tree_nodes, cspm_tree_node_bitset=cspm_tree_node_bitset, s_ex=None,
                               i_ex=None, flag=None, work_with_sex=None)
        #  print(f"{new_node.pattern} {support_table_entry.closed_patterns_with_trie[0] == support_table_entry.closed_patterns_with_trie[1]}")
        assert(support_table_entry.closed_patterns_with_trie[1].next == new_node)
        assert(new_node.prev == support_table_entry.closed_patterns_with_trie[1])
        support_table_entry.closed_patterns_with_trie[1] = new_node
        """
        sanity_verdict = debug_functions.print_sanity_check_pattern_trie(head=support_table_entry.closed_patterns_with_trie[0],
                                                        tail=support_table_entry.closed_patterns_with_trie[1])
        print(f"sanity_verdict = {sanity_verdict}")
        #print("special closed printing")
        #support_table_entry.closed_patterns_with_trie[0].print_patterns(type=0)
        """
        return new_node

    def remove_closed_pattern(self, support_table_entry, node_to_delete):
        # removing a closed pattern/node from trie
        # print(f"Node to delete = {node_to_delete.pattern}")
        assert(node_to_delete.pattern is not None)
        assert(node_to_delete.prev is not None)
        prev_node = node_to_delete.prev
        # print(f"prev_node {prev_node.pattern}")
        support_table_entry.closed_patterns_with_trie[0].delete(prev_node=node_to_delete.prev,
                                                                current=node_to_delete)
        if support_table_entry.closed_patterns_with_trie[1] == node_to_delete:
            assert(node_to_delete.next is None)
            support_table_entry.closed_patterns_with_trie[1] = prev_node
            #assert(support_table_entry.closed_patterns_with_trie[0].next is None or
            #        support_table_entry.closed_patterns_with_trie[0].next == prev_node)
        elif support_table_entry.closed_patterns_with_trie[0].next is None:
            support_table_entry.closed_patterns_with_trie[1] = support_table_entry.closed_patterns_with_trie[0]
        """
        # complete debug section
        # print(f"special closed printing deletion {support_table_entry.closed_patterns_with_trie[0].next}")
        ct, save = support_table_entry.closed_patterns_with_trie[0].print_patterns(type=0)
        if len(save) > 0:
            # print(save[-1][0],  support_table_entry.closed_patterns_with_trie[1].pattern)
            assert(str(save[-1][0]) == str(support_table_entry.closed_patterns_with_trie[1].pattern))

        sanity_verdict = debug_functions.print_sanity_check_pattern_trie(
            head=support_table_entry.closed_patterns_with_trie[0],
            tail=support_table_entry.closed_patterns_with_trie[1])
        print(f"sanity_verdict = {sanity_verdict}")
        """
        node_to_delete.clear_all_the_attributes(current=node_to_delete)
        del node_to_delete


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
            prev_node.next_link.prev_link = node

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
        assert (len(ll_nodes) == len(updated_cspm_tree_nodes))
        if len(updated_cspm_tree_nodes) == 0:
            assert (old_linked_list_node is not None)
            if old_linked_list_node.next_link is not None:  # (a b c) -> (a c)
                old_linked_list_node.prev_link.next_link = old_linked_list_node.next_link
                old_linked_list_node.next_link.prev_link = old_linked_list_node.prev_link
            elif old_linked_list_node.next_link is None:  # (a b) -> (a)
                old_linked_list_node.prev_link.next_link = None
            old_linked_list_node.prev_link = None
            old_linked_list_node.next_link = None
            del old_linked_list_node
        return ll_nodes

    def print(self, node):
        print("printing all pattern extension LL nodes")
        current = node
        while current is not None:
            if current.node is not None:
                print("main ", current.node.node_id)
                if current.prev_link.node is not None:
                    print("prev  ", current.prev_link.node.node_id)
                else:
                    print("None")
            current = current.next_link


class PatternTrie:
    # Trie to hold all the candidate and closed patterns
    def __init__(self):
        # basic info
        self.parent_node = None
        self.pattern = None
        self.item = None
        self.ex_type = None
        self.cnt = 0

        # any one of them will be activated
        self.cspm_tree_node_bitset = None  # [1, 2] -> [110]: node ids bitset representation
        self.cspm_tree_nodes = None  # node representation
        self.child = None
        self.s_ex = None
        self.i_ex = None
        self.flag = None  # [0: Can never be closed, None: no decision]
        self.work_with_sex = True  # [True: work with it, False: It is abosrbed, do not work with it even if exists]
        # links
        self.next = None
        self.prev = None

    def insert_a_pattern(self, root, pattern):
        # inserting a pattern in the trie in reverse order
        current = root
        for event in range(0, len(pattern)):
            ex_type = 0  # SE
            for item in range(0, len(pattern[event])):
                if current.child is None:
                    current.child = {}
                if current.child.get(pattern[event][item]) is None:
                    current.child[pattern[event][item]] = {}
                if current.child[pattern[event][item]].get(ex_type) is None:
                    current.child[pattern[event][item]][ex_type] = PatternTrie()
                    current.child[pattern[event][item]][ex_type].item = pattern[event][item]
                    current.child[pattern[event][item]][ex_type].ex_type = ex_type
                    current.child[pattern[event][item]][ex_type].parent_node = current
                current.child[pattern[event][item]][ex_type].cnt += 1  # ovelapping count
                current = current.child[pattern[event][item]][ex_type]
                ex_type = 1  # IE
        current.pattern = pattern  # putting the element there
        return current

    def create_link(self, current_end, new_end):
        current_end.next = new_end
        new_end.prev = current_end
        return

    def update_attributes(self, new_node, cspm_tree_nodes=None, cspm_tree_node_bitset=None, s_ex=None, i_ex=None,
                          flag=None, work_with_sex=None):
        if cspm_tree_nodes is not None:
            new_node.cspm_tree_nodes = cspm_tree_nodes
        if cspm_tree_node_bitset is not None:
            new_node.cspm_tree_node_bitset = cspm_tree_node_bitset
        if s_ex is not None:
            new_node.s_ex = s_ex
        if i_ex is not None:
            new_node.i_ex = i_ex
        if flag is not None:
            new_node.flag = flag
        if work_with_sex is not None:
            new_node.work_with_sex = work_with_sex
        return

    def insert(self, root, pattern, current_end, cspm_tree_nodes=None, cspm_tree_node_bitset=None, s_ex=None, i_ex=None,
               flag=None, work_with_sex=None):
        # inserting a pattern in the trie
        new_node = self.insert_a_pattern(root=root, pattern=pattern)
        # update the attributes: Candidates and closed
        self.update_attributes(new_node=new_node, cspm_tree_nodes=cspm_tree_nodes,
                               cspm_tree_node_bitset=cspm_tree_node_bitset, s_ex=s_ex, i_ex=i_ex, flag=flag,
                               work_with_sex=work_with_sex)
        # creating new link
        self.create_link(current_end=current_end, new_end=new_node)
        return new_node

    def delete(self, prev_node, current):
        assert (current.prev == prev_node)
        if current.next is None:
            prev_node.next = None
        if current.next is not None:
            prev_node.next = current.next
            current.next.prev = prev_node

        temp = current
        while temp is not None:
            temp.cnt -= 1
            temp = temp.parent_node
        # parent node trying to forget this child
        self.parent_node_forgetting(current=current)

        current.next = None
        current.prev = None
        return current

    def clear_all_the_attributes(self, current):
        current.cspm_tree_nodes = None
        current.cspm_tree_node_bitset = None
        current.s_ex = None
        current.i_ex = None
        current.pattern = None


    def parent_node_forgetting(self, current):
        if current is None:  # If I try to persist the cnt attribute
            return
        # assert(current.parent_node is not None)
        if current.cnt == 0:
            # print(f"{current.pattern} {current.parent_node.child} {current.ex_type} {current.item}")
            assert (current.parent_node.child[current.item][current.ex_type] == current)
            del current.parent_node.child[current.item][current.ex_type]
            rev_ex_type = (current.ex_type + 1) % 2  # just alternate checking
            if current.parent_node.child[current.item].get(rev_ex_type) is None:
                del current.parent_node.child[current.item]
            self.parent_node_forgetting(current=current.parent_node)  # recursive deletion

    def extract_cspm_tree_nodes(self, trie_node, NODE_MAPPER=None):
        # extracting the cspm tree nodes for a node
        if trie_node is not None and trie_node.cspm_tree_nodes is not None:
            # nodes are explicitly provided
            return trie_node.cspm_tree_nodes
        elif trie_node is not None and trie_node.cspm_tree_node_bitset is not None:
            cspm_tree_nodes = generate_cspm_tree_nodes_from_bitset(trie_node.cspm_tree_node_bitset, NODE_MAPPER)
            return cspm_tree_nodes

    def print_pattern_trie(self, root, info):
        print(
            f"root.pattern={root.pattern}, root.item={root.item}, root.ex_type={root.ex_type}, root.cnt={root.cnt}, info={info}")
        if root.child is not None:
            for item in root.child:
                for ex_type in root.child[item]:
                    info.append([item, ex_type])
                    self.print_pattern_trie(root=root.child[item][ex_type], info=info)
                    info.pop()
        else:
            print("reached leaf")

    def print_patterns(self, type=0):
        # traversing from bottom to the main node
        if type == 0:
            print("printing the closed nodes-revised")
        st = self
        ct = 0
        save = []
        while st is not None:
            ct += 1
            print(st.pattern)
            if st.pattern is not None:
                save.append([st.pattern])
            st = st.next
        print("DONE")
        return ct, save


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
            current.next.prev = current.prev
        elif current.next is None:  # last node deletion
            assert (current.prev is not None)
            current.prev.next = None
        current.prev = None
        current.next = None
        del current

    def print(self):
        # traversing from bottom to the main node
        print("printing the closed nodes")
        st = self
        ct = 0
        save = []
        while st is not None:
            ct += 1
            print(st.pattern)
            if st.pattern is not None:
                save.append([st.pattern])
            st = st.next
        print("DONE")
        return ct, save


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
        self.work_with_sex = True  # [True: work with it, False: It is abosrbed, do not work with it even if exists]
        # linked lists
        self.next = None
        self.prev = None

    def create_node(self, pattern, cspm_tree_node_bitset, current, cspm_tree_nodes, s_ex, i_ex, flag=None,
                    work_with_sex=True):
        n = CandidatePatternLinkedListNode()
        n.pattern = pattern
        n.cspm_tree_node_bitset = cspm_tree_node_bitset
        n.cspm_tree_nodes = cspm_tree_nodes
        n.s_ex = s_ex
        n.i_ex = i_ex
        n.flag = flag
        n.work_with_sex = work_with_sex
        # creating the links
        current.next = n
        n.prev = current
        return n

    def delete_node(self, node, base_caphe_node):
        if node.prev is not None and node.next is not None:
            node.prev.next = node.next
            node.next.prev = node.prev
        elif node.next is None:
            print(f"DEBUG {node.pattern}")
            assert (node.prev is not None)
            node.prev.next = None
        if base_caphe_node.pattern_ll_node[1] == node:
            # it was ending node, adjusting [st, end]
            assert (node.prev is not None)
            base_caphe_node.pattern_ll_node[1] = node.prev

        node.prev = None
        node.next = None
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
        # temp = CandidatePatternLinkedListNode() # Linked list version
        temp = PatternTrie()  # Trie version
        self.pattern_ll_node = [temp, temp]  # head with pattern None, end with pattern none
        self.idx_in_heap = -1  # where the node is in heap

    def __lt__(self, other):
        if self.support < other.support:  # comparison between supports, higher support will come earlier
            return True
        return False

    def insert_pattern(self, caphe_node, pattern, cspm_tree_nodes, cspm_tree_node_bitset, s_ex, i_ex, flag=None,
                       work_with_sex=True):
        # adding patterns as ll list, new pattern to explore
        # adding after end
        if caphe_node.pattern_ll_node[0].next is None:
            # candidates have been removed
            caphe_node.pattern_ll_node[1] = caphe_node.pattern_ll_node[0]
        current = caphe_node.pattern_ll_node[1]
        # creating new entry in trie version
        assert (isinstance(current, PatternTrie))
        pattern_ll_node = current.insert(root=caphe_node.pattern_ll_node[0], pattern=pattern, current_end=current,
                                         cspm_tree_nodes=cspm_tree_nodes,
                                         cspm_tree_node_bitset=cspm_tree_node_bitset, s_ex=s_ex, i_ex=i_ex,
                                         flag=flag, work_with_sex=work_with_sex)
        caphe_node.pattern_ll_node[1] = pattern_ll_node
        return pattern_ll_node
        """
        # old linked list version 
        pattern_ll_node = current.create_node(pattern=pattern, cspm_tree_node_bitset=cspm_tree_node_bitset,
                                              current=current, cspm_tree_nodes=cspm_tree_nodes, s_ex=s_ex, i_ex=i_ex,
                                              flag=flag, work_with_sex=work_with_sex)
        # new ending node
        caphe_node.pattern_ll_node[1] = pattern_ll_node
        # caphe_node.print_caphe_node()
        return pattern_ll_node
        """

    def pop_last_element(self, caphe_node,
                         NODE_MAPPER=None):  # extracting the last pattern and its information from a node
        assert (caphe_node is not None)
        # sanity code
        if caphe_node.pattern_ll_node[0].next is None:
            # somehow all the candidates has been deleted, fixing the starting and ending pointer
            caphe_node.pattern_ll_node[1] = caphe_node.pattern_ll_node[0]
        if caphe_node.pattern_ll_node[0] != caphe_node.pattern_ll_node[1]:
            # some patterns in the bucket
            pattern_ll_node = caphe_node.pattern_ll_node[0].next
            if pattern_ll_node.next is None:
                # this was the last node
                caphe_node.pattern_ll_node[1] = caphe_node.pattern_ll_node[0]
            pattern_ll_node.delete(prev_node=pattern_ll_node.prev, current=pattern_ll_node)
            """
            if pattern_ll_node.next is None:
                # reached last node
                pattern_ll_node.prev.next = None
                caphe_node.pattern_ll_node[1] = caphe_node.pattern_ll_node[0]
            else:
                # None -> a->b : None->b
                pattern_ll_node.prev.next = pattern_ll_node.next
                pattern_ll_node.next.prev = pattern_ll_node.prev
            """
            pattern = pattern_ll_node.pattern
            cspm_tree_nodes = pattern_ll_node.extract_cspm_tree_nodes(trie_node=pattern_ll_node,
                                                                      NODE_MAPPER=NODE_MAPPER)
            cspm_tree_node_bitset = pattern_ll_node.cspm_tree_node_bitset
            s_ex = pattern_ll_node.s_ex
            i_ex = pattern_ll_node.i_ex
            flag = pattern_ll_node.flag
            work_with_sex = pattern_ll_node.work_with_sex

            # before deletion
            pattern_ll_node.clear_all_the_attributes(current=pattern_ll_node)
            assert (pattern_ll_node.prev is None)
            assert (pattern_ll_node.next is None)
            del pattern_ll_node
            return pattern, cspm_tree_nodes, cspm_tree_node_bitset, s_ex, i_ex, flag, work_with_sex
        else:  # no pattern in the bucket
            return None  # no entry here

    def print_caphe_node(self):
        print("Printing the candidates in caphe node")
        st = self.pattern_ll_node[0]
        en = self.pattern_ll_node[1]
        while st is not None:
            print(st.pattern)
            st = st.next

    def clear_attributes(self):
        # clearing all the attributes, so that can be detected during deletion
        self.support = self.pattern_ll_heap = self.idx_in_heap = None
        return


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
            self.nodes[-1].clear_attributes()
            del self.nodes[-1]
            if len(self.nodes) > 0:
                self.sort_nodes(current_idx=0)
        else:  # arbitrary node
            idx = special_node.idx_in_heap
            ending_node = False
            if idx == len(self.nodes) - 1:
                ending_node = True
            self.swap(idx, len(self.nodes) - 1)
            self.nodes[-1].clear_attributes()
            del self.nodes[-1]
            if len(self.nodes) > 0:
                if ending_node is False:
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
    """
    caphe_node = CapheNode(support=10)
    node = caphe_node.insert_pattern(caphe_node=caphe_node, pattern=[[1]], cspm_tree_nodes=[[1]],
                                     cspm_tree_node_bitset=None, s_ex=None, i_ex=None, flag=None, work_with_sex=True)
    node = caphe_node.insert_pattern(caphe_node=caphe_node, pattern=[[2]], cspm_tree_nodes=[[1]],
                                     cspm_tree_node_bitset=None, s_ex=None, i_ex=None, flag=None, work_with_sex=True)
    node = caphe_node.insert_pattern(caphe_node=caphe_node, pattern=[[3]], cspm_tree_nodes=[[1]],
                                     cspm_tree_node_bitset=None, s_ex=None, i_ex=None, flag=None, work_with_sex=True)
    node = caphe_node.insert_pattern(caphe_node=caphe_node, pattern=[[1], [2]], cspm_tree_nodes=[[1]],
                                     cspm_tree_node_bitset=None, s_ex=None, i_ex=None, flag=None, work_with_sex=True)
    node = caphe_node.insert_pattern(caphe_node=caphe_node, pattern=[[1, 2]], cspm_tree_nodes=[[1]],
                                     cspm_tree_node_bitset=None, s_ex=None, i_ex=None, flag=None, work_with_sex=True)
    node = caphe_node.insert_pattern(caphe_node=caphe_node, pattern=[[1, 2, 3]], cspm_tree_nodes=[[1]],
                                     cspm_tree_node_bitset=None, s_ex=None, i_ex=None, flag=None, work_with_sex=True)
    caphe_node.print_caphe_node()
    caphe_node.pattern_ll_node[0].print_pattern_trie(root=caphe_node.pattern_ll_node[0], info=[])
    from pattern_quality_measure import *

    # closure_check_with_trie(trie_head=caphe_node.pattern_ll_node[0], p=[[1, 2, 3]], type_flag=1)
    closure_check_with_trie(trie_head=caphe_node.pattern_ll_node[0], p=[[1, 2]], type_flag=1)
    """
    pass
