def calculate_number_of_characters(pattern):
    # return the number of characters
    _cnt = 0
    for i in range(0, len(pattern)):
        _cnt += len(pattern[i])
    return _cnt


class SupportTableEntry:
    def __init__(self):
        # linked list version
        self.caphe_node_dict = {}  # For each support holds the corresponding CaPHe node


class PatternBlock:
    # Each Pattern Block will use this to store candidates or closed patterns
    def __init__(self, pattern, cspm_tree_node_bitset, cspm_tree_nodes, projection_status, s_ex, i_ex, closed_flag=1):
        self.pattern = pattern
        self.cspm_tree_node_bitset = cspm_tree_node_bitset  # [1, 2] -> [110]: node ids bitset representation
        self.cspm_tree_nodes = cspm_tree_nodes  # node representation
        self.projection_status = projection_status  # ["0": intermediate processing, "1": processed] will be a list
        self.s_ex = s_ex  # possible items to expand as sequence extension (SE)
        self.i_ex = i_ex  # possible items to expand as sequence extension (IE)
        self.closed_flag = closed_flag  # [1: Can be closed, 0: can not be closed]
        self.s_ex_needed = 1 # [1: SE Needed, 0: Not Needed]

        # links
        self.next = None
        self.prev = None

    def create_link(self, current_node, new_node):
        if current_node.next is None:
            current_node.next = new_node
            new_node.prev = current_node
        elif current_node.next is not None:
            new_node.next = current_node.next
            current_node.next.prev = new_node
            current_node.next = new_node
            new_node.prev = current_node

    def delete(self, current):
        # to remove current node from the tracking
        prev_node = current.prev
        assert (current.prev is not None)
        if current.next is None:
            prev_node.next = None
        if current.next is not None:
            prev_node.next = current.next
            current.next.prev = prev_node

        current.next = None
        current.prev = None
        del current
        return

    def print_connected_blocks(self, head):
        # print all the blocks come after head
        curr = head
        while curr is not None:
            print(f"{curr.pattern}")
            curr = curr.next


class PatternExtensionLinkedList:
    # Linkedlist used during pattern extension using breadth-first search
    # to process the nodes during extension in O(N) complexity, no sorting required here
    # all the nodes will follow the same subtree code's ascending order
    def __init__(self, node, projection_status="1"):
        self.node = node
        self.prev = None
        self.next = None
        self.projection_status = projection_status # 0: incomplete, 1: complete projection

    def insert(self, node, prev_node):  # A->B
        if prev_node.next is not None:
            node.next = prev_node.next
            prev_node.next.prev = node

            node.prev = prev_node
            prev_node.next = node
        else:
            prev_node.next = node
            node.prev = prev_node
        return

    def replace_with_subtree(self, old_linked_list_node, updated_cspm_tree_nodes):
        # A->B->C : A->(D->E)->C
        current_node = old_linked_list_node
        # removing this current node from the linked list
        prev_node = old_linked_list_node.prev
        if old_linked_list_node.next is None:
            prev_node.next = None
            old_linked_list_node.prev = None
            old_linked_list_node.next = None
        else: # bypass
            prev_node.next = old_linked_list_node.next
            old_linked_list_node.next.prev = prev_node
            old_linked_list_node.prev = None
            old_linked_list_node.next = None
        ll_nodes = []
        for i in range(0, len(updated_cspm_tree_nodes)):
            if i == 0:
                # First delete, then add new one
                ll_node = PatternExtensionLinkedList(node=updated_cspm_tree_nodes[i], projection_status="0")
                self.insert(node=ll_node, prev_node=prev_node)
                current_node = ll_node
            else:
                # adding new nodes after current node
                ll_node = PatternExtensionLinkedList(node=updated_cspm_tree_nodes[i], projection_status="0")
                self.insert(node=ll_node, prev_node=current_node)
                current_node = ll_node
            ll_nodes.append(current_node)  # newly created linked list nodes
        assert (len(ll_nodes) == len(updated_cspm_tree_nodes))
        return ll_nodes

    def print(self, node):
        print("printing all pattern extension LL nodes")
        current = node
        while current is not None:
            if current.node is not None:
                print("main ", current.node.node_id, current.node.count, current.node.event_no, current.node.item,
                      current.node.parent_item_bitset)
                """
                if current.prev.node is not None:
                    print("prev  ", current.prev.node.node_id)
                else:
                    print("None")
                """
            current = current.next



class Caphe:
    # The heap controlling data structure
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
            ending_node = False
            if idx == len(self.nodes) - 1:
                ending_node = True
            self.swap(idx, len(self.nodes) - 1)
            del self.nodes[-1]
            if len(self.nodes) > 0:
                if ending_node is False:
                    self.sort_nodes(current_idx=idx)

    def print(self, caphe_node=None):
        print("########Starting printing")
        if caphe_node is None:
            for i in range(0, len(self.nodes)):
                print(f"support = {self.nodes[i].support}, idx_in_heap = {self.nodes[i].idx_in_heap}")
                print("printing candidates")
                if self.nodes[i].stored_patterns["candidate"] is not None:
                    for length in self.nodes[i].stored_patterns["candidate"]:
                        print(f"length = {length}")
                        # 1: candidate, length of pattern , head/0
                        self.nodes[i].stored_patterns["candidate"][length][0].print_connected_blocks(head=self.nodes[i].stored_patterns["candidate"][length][0])
        else:
            print(f"support = {caphe_node.support}, idx_in_heap = {caphe_node.idx_in_heap}")
            print("printing candidates")
            if caphe_node.stored_patterns["candidate"] is not None:
                for length in caphe_node.stored_patterns["candidate"]:
                    print(f"length = {length}")
                    # 1: candidate, length of pattern , head/0
                    caphe_node.stored_patterns["candidate"][length][0].print_connected_blocks(
                        head=caphe_node.stored_patterns["candidate"][length][0])

        print()

    def print_all_closed_patterns(self, support_table_entry):
        all_support = list(support_table_entry.caphe_node_dict.keys())
        all_support.sort(reverse=True)
        for i in range(0, len(all_support)):
            print(f"support = {all_support[i]}")
            caphe_node = support_table_entry.caphe_node_dict[all_support[i]]
            if caphe_node.stored_patterns['closed'] is not None:
                lengths = list(caphe_node.stored_patterns['closed'].keys())
                lengths.sort(reverse=True)
                for j in range(0, len(lengths)):
                    print(f"length = {lengths[j]}")
                    caphe_node.stored_patterns["closed"][lengths[j]][0].print_connected_blocks(
                        head=caphe_node.stored_patterns["closed"][lengths[j]][0])

    def extract_all_closed_patterns(self, support_table_entry):
        mined_closed_patterns = {}
        all_support = list(support_table_entry.caphe_node_dict.keys())
        all_support.sort(reverse=True)
        for i in range(0, len(all_support)):
            mined_closed_patterns[all_support[i]] = []
            # print(f"support = {all_support[i]}")
            caphe_node = support_table_entry.caphe_node_dict[all_support[i]]
            if caphe_node.stored_patterns['closed'] is not None:
                lengths = list(caphe_node.stored_patterns['closed'].keys())
                lengths.sort(reverse=True)
                for j in range(0, len(lengths)):
                    head = caphe_node.stored_patterns["closed"][lengths[j]][0].next
                    while head is not None:
                        mined_closed_patterns[all_support[i]].append(head.pattern)
                        head = head.next
            if len(mined_closed_patterns[all_support[i]]) == 0:
                del mined_closed_patterns[all_support[i]]
        return mined_closed_patterns


class CapheNode:
    # Will hold both candidates and closed patterns using PatternBlock DS
    def __init__(self, support):  # single node multiple pattern
        self.support = support
        self.stored_patterns = {
            "candidate": None, # candidates
            "closed": None  # closed
        }
        self.idx_in_heap = -1  # where the node is in heap

    def __lt__(self, other):
        if self.support < other.support:  # comparison between supports, higher support will come earlier
            return True
        return False

    def insert_pattern(self, pattern_type, caphe_node, pattern, cspm_tree_nodes, cspm_tree_node_bitset,
                       projection_status, s_ex, i_ex, closed_flag=1):
        # adding pattern based on pattern_type = "closed" and "candidate"
        # adding patterns based on lengths, FIFO Wise addition/end at bottom
        type_idx = None  # 0: Closed, 1: Candidate
        if pattern_type == "candidate":
            type_idx = "candidate"
            pb = PatternBlock(pattern=pattern, cspm_tree_node_bitset=cspm_tree_node_bitset,
                              cspm_tree_nodes=cspm_tree_nodes, projection_status=projection_status, s_ex=s_ex,
                              i_ex=i_ex, closed_flag=closed_flag)

        else:
            # closed
            type_idx = "closed"
            pb = PatternBlock(pattern=pattern, cspm_tree_node_bitset=cspm_tree_node_bitset,
                              cspm_tree_nodes=cspm_tree_nodes, projection_status=projection_status, s_ex=None,
                              i_ex=None, closed_flag=1)
        count = calculate_number_of_characters(pattern=pattern)
        if caphe_node.stored_patterns[type_idx] is None:
            caphe_node.stored_patterns[type_idx] = {}  # 0: {} or 1: {}
        if caphe_node.stored_patterns[type_idx].get(count) is None:  # 0 : [pattern length]: Linker start
            head = PatternBlock(pattern=None, cspm_tree_node_bitset=None,
                                cspm_tree_nodes=None, projection_status=None,
                                s_ex=None, i_ex=None, closed_flag=1)
            caphe_node.stored_patterns[type_idx][count] = [head, head]
        # current end->end
        caphe_node.stored_patterns[type_idx][count][0].create_link(
            current_node=caphe_node.stored_patterns[type_idx][count][1],
            new_node=pb)
        caphe_node.stored_patterns[type_idx][count][1] = pb # new end updated
        return pb

    def pop(self, caphe_node, deleted_pb, pattern_type, NODE_MAPPER=None):
        # if deleted_pb is specified that will be deleted else the first one is deleted after head
        # pattern_type: closed/candidate selects the buffer
        if pattern_type == "closed":
            type_idx = "closed"
        else:
            type_idx = "candidate"
        if deleted_pb is None:  # delete the first entry from the longest length
            length = None  # largest length tracking
            for l in caphe_node.stored_patterns[type_idx]:
                if length is None:
                    length = l
                elif length > l:
                    length = l
            if length is None: # no more candidates
                return None
            assert (caphe_node.stored_patterns[type_idx][length][0].next is not None)  # at least one pattern is there
            deleted_pb = caphe_node.stored_patterns[type_idx][length][0].next
        else:  # a specific entry to be deleted
            length = calculate_number_of_characters(pattern=deleted_pb.pattern)
            assert (caphe_node.stored_patterns[type_idx][length][0].next is not None)  # at least one pattern is there
        if deleted_pb.next is None:  # last node is deleted in linked list
            caphe_node.stored_patterns[type_idx][length][1] = deleted_pb.prev # updating the end
            deleted_pb.prev.next = None
            if caphe_node.stored_patterns[type_idx][length][0] == caphe_node.stored_patterns[type_idx][length][1]:
                # only head remains - deleted
                del caphe_node.stored_patterns[type_idx][length]
        else:  # adjusting the links
            deleted_pb.next.prev = deleted_pb.prev
            deleted_pb.prev.next = deleted_pb.next
            deleted_pb.prev = None
            deleted_pb.next = None
        return deleted_pb

    def clear_attributes(self):
        self.support = self.idx_in_heap = None
        self.stored_patterns.clear()


class MinHeap:
    # min heap to hold the support only
    def __init__(self, priority):
        self.priority = priority

    def __lt__(self, other):
        if self.priority < other.priority:
            return True
        return False
