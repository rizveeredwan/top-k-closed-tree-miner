import functools
from collections import deque


def find_parent_idx_in_heap(number):
    if number % 2 == 1:
        return int(number / 2)
    if number % 2 == 0:
        return int(number / 2) - 1


class MaximalHeap_ActualPattern:
    # A max heap to control push, pop, update
    def __init__(self, cspm_tree_leaf):
        self.cspm_tree_leaf = cspm_tree_leaf
        self.pattern_idx_list = []
        self.normal_heap_idx = 0

    def insert_pattern(self, node, pattern_idx, heap):  # inserting a new pattern
        node.pattern_idx_list.append(pattern_idx)
        if len(node.pattern_idx_list) == 1:
            self.insert_in_heap(heap=heap, node=node)
        else:
            self.update_in_heap(node=node, heap=heap)  # trying to reorder the node

    def print_particular_heap_node(self, heap, idx):
        print(f"{heap[idx]} {idx} {heap[idx].normal_heap_idx} {heap[idx].cspm_tree_leaf} {heap[idx].pattern_idx_list}")

    def remove_pattern(self, node, pattern_idx, heap):  # removing a pattern
        node.pattern_idx_list.remove(pattern_idx)
        if len(node.pattern_idx_list) == 0:
            self.delete_node(node_idx=node.normal_heap_idx, heap=heap)
        else:
            self.update_in_heap(node=node, heap=heap)  # trying to reorder the node

    def insert_in_heap(self, heap, node):  # inserting a new node in the heap
        heap.append(node)
        node.normal_heap_idx = len(heap) - 1

    def swap(self, idx1, idx2, heap):
        # print("swap er age ", heap[idx1], heap[idx2])
        temp = heap[idx1]
        heap[idx1] = heap[idx2]
        heap[idx2] = temp
        heap[idx1].normal_heap_idx = idx1
        heap[idx2].normal_heap_idx = idx2
        # print("swap er pore ", heap[idx1], heap[idx2])
        return heap

    def update_in_heap(self, node, heap):  # adjusting based on frequency
        # go up
        current_idx = node.normal_heap_idx
        while current_idx > 0:
            par_idx = find_parent_idx_in_heap(number=current_idx)
            if len(heap[par_idx].pattern_idx_list) >= len(heap[current_idx].pattern_idx_list):
                break  # parent have better priority
            else:
                # need to swap: parent has lesser priority
                heap = self.swap(idx1=par_idx, idx2=current_idx, heap=heap)
                current_idx = par_idx
        # go down
        current_idx = node.normal_heap_idx
        # print(f"current {current_idx} {len(heap)}")
        while True:
            par_idx = current_idx
            left_idx = 2 * par_idx
            right_idx = 2 * par_idx + 1
            if len(heap) > right_idx:  # both exists
                if len(heap[par_idx].pattern_idx_list) >= len(heap[left_idx].pattern_idx_list) and \
                        len(heap[par_idx].pattern_idx_list) >= len(heap[right_idx].pattern_idx_list):
                    break  # no more changing required
                if len(heap[left_idx].pattern_idx_list) >= len(heap[par_idx].pattern_idx_list) and len(
                        heap[left_idx].pattern_idx_list) >= len(heap[right_idx].pattern_idx_list):
                    self.swap(idx1=left_idx, idx2=par_idx, heap=heap)
                    current_idx = left_idx
                if len(heap[right_idx].pattern_idx_list) >= len(heap[par_idx].pattern_idx_list) and len(
                        heap[right_idx].pattern_idx_list) >= len(heap[left_idx].pattern_idx_list):
                    self.swap(idx1=right_idx, idx2=par_idx, heap=heap)
                    current_idx = right_idx
            elif (len(heap) - 1) >= left_idx:  # only left exists
                if len(heap[par_idx].pattern_idx_list) >= len(heap[left_idx].pattern_idx_list):  # no change required
                    break
                if len(heap[par_idx].pattern_idx_list) < len(heap[left_idx].pattern_idx_list):
                    self.swap(idx1=par_idx, idx2=left_idx, heap=heap)
                    break
            else:
                break
        return

    def delete_node(self, node_idx, heap):
        if len(heap) > 0:
            self.swap(idx1=node_idx, idx2=len(heap) - 1, heap=heap)
            del heap[-1]  # last idx deletion
            # print("size after deletion ", len(heap))
        if len(heap) > 0:
            if node_idx <= (len(heap) - 1): # A valid node
                self.update_in_heap(node=heap[node_idx], heap=heap)  # adjust the replaced node

    def front(self, heap):
        top_node = heap[0]
        self.delete_node(node_idx=0, heap=heap)
        return top_node

    def print_func(self, heap):
        print("printing heap")
        for i in range(0, len(heap)):
            print(heap[i].cspm_tree_leaf, heap[i].normal_heap_idx, heap[i].pattern_idx_list)


def find_absent_items(base, candidate):
    absent = []
    for i in range(0, len(candidate)):
        if candidate[i] not in base:
            absent.append(candidate[i])
    return absent


def calculate_maximal_pattern_light_constraint(pattern_cluster):
    # a single maximal pattern where the pattern does not need to be found in the database
    event = 0
    maximal_pattern = []
    while True:
        operation = False
        for i in range(0, len(pattern_cluster)):
            if len(pattern_cluster[i]) <= event:  # small pattern already covered
                continue
            if operation is False:
                operation = True
                maximal_pattern.append([])
            absent = find_absent_items(base=maximal_pattern[event], candidate=pattern_cluster[i][event])
            if len(absent) > 0:
                for j in range(0, len(absent)):
                    maximal_pattern[event].append(absent[j])
        event += 1
        if operation is False:
            break
    for i in range(0, len(maximal_pattern)):
        maximal_pattern[i].sort()  # Lexicographic sorting
    return maximal_pattern


def find_bitset(pattern, event, it):
    need = 0
    for i in range(0, it):
        need = need | (1 << pattern[event][i])
    return need


def search_projection_nodes(node, pattern, ev, it, projection_nodes):
    # For the pattern finding its projection nodes in the tree
    if ev == len(pattern):
        projection_nodes.append(node)
        return
    elif it == len(pattern[ev]):
        search_projection_nodes(node=node, pattern=pattern, ev=ev + 1, it=0, projection_nodes=projection_nodes)
    else:
        choices = []
        if node.down_next_link_ptr is not None and node.down_next_link_ptr.get(pattern[ev][it]) is not None:
            start = node.down_next_link_ptr[pattern[ev][it]][0]
            end = node.down_next_link_ptr[pattern[ev][it]][1]
            while True:
                choices.append(start)
                if start == end:
                    break
                start = start.side_next_link_next
        for i in range(0, len(choices)):
            if it == 0:  # SE
                if choices[i].event_no == node.event_no:  # not valid SE
                    search_projection_nodes(choices[i], pattern, ev, it, projection_nodes)
                elif choices[i].event_no > node.event_no:  # valid SE
                    search_projection_nodes(choices[i], pattern, ev, it + 1, projection_nodes)
            else:  # IE
                bitset = find_bitset(pattern=pattern, event=ev, it=it)
                assert (bitset > 0)
                if (choices[i].parent_item_bitset & bitset) == bitset:  # valid IE
                    search_projection_nodes(choices[i], pattern, ev, it + 1, projection_nodes)
                else:  # not valid IE
                    search_projection_nodes(choices[i], pattern, ev, it, projection_nodes)


def find_leaf_nodes(current_node, leaf_nodes):
    if current_node.child_link is None:
        leaf_nodes.append(current_node)
        return
    for ev in current_node.child_link:
        for it in current_node.child_link[ev]:
            find_leaf_nodes(current_node=current_node.child_link[ev][it], leaf_nodes=leaf_nodes)
    return


def extract_the_full_transaction(cspm_tree_node):
    # trying to extract the complete transaction here
    tr = []
    current = cspm_tree_node
    last_event = None
    while current is not None:
        if last_event != current.event_no:
            if current.item is not None:
                tr.append([current.item])
        else:
            assert (current.item is not None)
            tr[-1].append(current.item)
        last_event = current.event_no
        current = current.parent_node
    tr.reverse()
    for i in range(0, len(tr)):
        tr[i].reverse()
    return tr


def print_maximal_pattern_with_group_of_patterns(maximal_pattern, pattern_idx_list, group_of_patterns, support):
    # Printing this maximal pattern is covering which patterns
    print("#### Group vs Maximal ####")
    for i in range(0, len(group_of_patterns[support])):
        if i in pattern_idx_list:
            print(group_of_patterns[support][i])
    print("maximal = ", maximal_pattern)


def event_checker(pattern1, pattern2):
    i, j = 0, 0
    while i < len(pattern1) and j < len(pattern2):
        if pattern1[i] == pattern2[j]:
            i += 1
            j += 1
        else:
            i += 1
    if j == len(pattern2):
        return True  # patter2 subset of pattern 1
    return False


def remove_redundant_characters(maximal_pattern, pattern_idx_list, group_of_pattern, support):
    # the characters which are not required are removed from the reported maximal transaction
    bitset = []
    for i in range(0, len(maximal_pattern)):
        bitset.append([])
        for j in range(0, len(maximal_pattern[i])):
            bitset[i].append(0)
    for i in range(0, len(pattern_idx_list)):
        pattern = group_of_pattern[support][pattern_idx_list[i]]
        curr_ev = 0
        for j in range(0, len(pattern)):
            for k in range(curr_ev, len(maximal_pattern)):
                if event_checker(pattern1=maximal_pattern[k], pattern2=pattern[j]) is True:
                    curr_ev = k + 1
                    idx1, idx2 = 0, 0
                    while idx2 < len(pattern[j]):
                        if pattern[j][idx2] == maximal_pattern[k][idx1]:
                            bitset[k][idx1] = 1
                            idx1 += 1
                            idx2 += 1
                        else:
                            idx1 += 1
                    break
    i = 0
    short_maximal_pattern = []
    for i in range(0, len(maximal_pattern)):
        f = False
        for j in range(0, len(maximal_pattern[i])):
            if bitset[i][j] == 1:
                f = True  # this event can be considered
                break
        if f is True:
            short_maximal_pattern.append([])
            for j in range(0, len(maximal_pattern[i])):
                if bitset[i][j] == 1:
                    short_maximal_pattern[-1].append(maximal_pattern[i][j])
    return short_maximal_pattern


def calculate_maximal_pattern_hard_constraint_greedy(group_of_patterns, cspm_root):
    # Each maximal pattern has to be a real pattern occurring in the database
    ct = 0
    set_of_maximal_pattern = {}
    for support in group_of_patterns:
        set_of_maximal_pattern[support] = []
        # Finding the valid projection nodes and storing them
        projection_nodes = []
        leaf_nodes = []
        leaf_node_dict = {}
        heap = []
        root_demo = MaximalHeap_ActualPattern(None)  # root controller
        for i in range(0, len(group_of_patterns[support])):
            projection_nodes.append([])  # holding the projection nodes for ith pattern
            leaf_nodes.append([])  # holding the leaf nodes for ith pattern
            # Extracting the projection nodes
            search_projection_nodes(node=cspm_root, pattern=group_of_patterns[support][i], ev=0, it=0,
                                    projection_nodes=projection_nodes[-1])
            # print(group_of_patterns[support][i])
            # print(projection_nodes[i])
            for j in range(0, len(projection_nodes[i])):
                find_leaf_nodes(current_node=projection_nodes[i][j], leaf_nodes=leaf_nodes[i])
            for j in range(0, len(leaf_nodes[i])):
                if leaf_node_dict.get(leaf_nodes[i][j]) is None:
                    leaf_node_dict[leaf_nodes[i][j]] = MaximalHeap_ActualPattern(cspm_tree_leaf=leaf_nodes[i][j])
                root_demo.insert_pattern(node=leaf_node_dict[leaf_nodes[i][j]],
                                         pattern_idx=i, heap=heap)
        # Greedy Algorithm
        leaf_node_buffer = []
        while len(heap) > 0:
            top = heap[0]  # getting the highest frequency one
            # print("debug ", top.pattern_idx_list, top.pattern_idx_list)
            # root_demo.print_func(heap)
            leaf_node_buffer.append(top.cspm_tree_leaf)
            mm = extract_the_full_transaction(cspm_tree_node=top.cspm_tree_leaf)
            set_of_maximal_pattern[support].append(remove_redundant_characters(maximal_pattern=mm,
                                                                               pattern_idx_list=top.pattern_idx_list,
                                                                               group_of_pattern=group_of_patterns,
                                                                               support=support))

            """                                                                  
            print_maximal_pattern_with_group_of_patterns(maximal_pattern=mm,
                                                         pattern_idx_list=top.pattern_idx_list,
                                                         group_of_patterns=group_of_patterns, support=support)
            """

            for i in range(0, len(top.pattern_idx_list)):
                patt_idx = top.pattern_idx_list[i]  # getting the patterns
                # remove this pattern from the corresponding leaf nodes
                for j in range(0, len(leaf_nodes[patt_idx])):
                    lf = leaf_nodes[patt_idx][j]  # desired leaf node
                    # removing pattern from this leaf node
                    if leaf_node_dict[lf] == top:
                        continue
                    # print("issues ", patt_idx, leaf_node_dict[lf].pattern_idx_list)
                    root_demo.remove_pattern(node=leaf_node_dict[lf], pattern_idx=patt_idx, heap=heap)
                # print("after deletion")
                # root_demo.print_func(heap)
            # print("I CAME HERE")
            root_demo.delete_node(node_idx=0, heap=heap)
    return set_of_maximal_pattern


def print_set_of_maximal_pattern(set_of_maximal_pattern, group_of_pattern):
    for support in set_of_maximal_pattern:
        print(f"{support} {len(group_of_pattern[support])} {len(set_of_maximal_pattern[support])}")
        print(f"{group_of_pattern[support]}")
        print(set_of_maximal_pattern[support])


if __name__ == '__main__':
    pattern_cluster = [
        [[1], [2, 3]],
        [[1, 2, 3]],
        [[1], [4, 5]]
    ]
    # print(calculate_maximal_pattern_light_constraint(pattern_cluster=pattern_cluster))
