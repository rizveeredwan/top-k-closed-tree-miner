import functools
from pattern_quality_measure_older import same_subtree_checking


class DebugFunctions:
    def __int__(self):
        pass

    def DebugPrintNextLink(self, node, down_nodes, down_nodes_codes=None):
        # print next links
        down_nodes[node.node_id] = {}
        if down_nodes_codes is not None:
            down_nodes_codes[node.node_id] = {}
        if node.down_next_link_ptr is not None:
            for key in node.down_next_link_ptr:
                down_nodes[node.node_id][key] = []
                if down_nodes_codes is not  None:
                    down_nodes_codes[node.node_id][key] = []
                st = node.down_next_link_ptr[key][0]
                en = node.down_next_link_ptr[key][1]
                #print(st, en)
                nxt = st
                #print("started ")
                while True:
                    down_nodes[node.node_id][key].append(nxt.node_id)
                    down_nodes_codes[node.node_id][key].append(nxt.subtree_detection_code)
                    if (nxt == en):
                        break
                    nxt = nxt.side_next_link_next
        if node.child_link is not None:
            for item in node.child_link:
                for event in node.child_link[item]:
                    self.DebugPrintNextLink(node.child_link[item][event], down_nodes, down_nodes_codes)
        return

    def sanity_test_next_links(self, node):
        down_nodes1 = {}
        down_nodes_codes = {}
        self.bruteforce_nextlink_gen(node, down_nodes1)
        down_nodes2 = {}
        self.DebugPrintNextLink(node, down_nodes2, down_nodes_codes)
        print(down_nodes1)
        print(down_nodes2)
        print(down_nodes_codes)
        for n1 in down_nodes1:
            assert(down_nodes2.get(n1) is not None)
            for it in down_nodes1[n1]:
                assert(down_nodes2[n1].get(it) is not None) # item exists
                down_nodes1[n1][it].sort()
                down_nodes2[n1][it].sort()
                print(n1, it, down_nodes1[n1][it], down_nodes2[n1][it])

    def bruteforce_nextlink_gen(self, node, down_nodes):
        down_nodes[node.node_id] = {}
        _dict = {}
        if node.child_link is not None:
            for item in node.child_link:
                for event_no in node.child_link[item]:
                    child = node.child_link[item][event_no]
                    _dict = self.bruteforce_nextlink_gen(child, down_nodes)
                    for key in _dict:
                        if down_nodes[node.node_id].get(key) is None:
                            down_nodes[node.node_id][key] = []
                        for i in range(0, len(_dict[key])):
                            if _dict[key][i] not in down_nodes[node.node_id][key]:
                                down_nodes[node.node_id][key].append(_dict[key][i])
        if node.item != "":
            _dict[node.item] = [node.node_id]
            for key in down_nodes[node.node_id]:
                if key != node.item:
                    if _dict.get(key) is None:
                        _dict[key] = []
                    for i in range(0, len(down_nodes[node.node_id][key])):
                        _dict[key].append(down_nodes[node.node_id][key][i])
        return _dict

    def moves(self, st, en):
        _list = []
        while True:
            _list.append(st.node_id)
            st = st.side_next_link_next
            if st == en:
                _list.append(en.node_id)
                break
            if st == None:
                break
        return _list

    def print_set_of_nodes(self, nodes):
        for i in range(0, len(nodes)):
            print(f"node={nodes[i].node_id}, support={nodes[i].count} label={nodes[i].item} event_no={nodes[i].event_no} "
                  f"parent_item_bitset={nodes[i].parent_item_bitset}")

    def print_ll_nodes_pattern(self, list_off_ll_nodes):
        for i in range(0, len(list_off_ll_nodes)):
            print(f"id={list_off_ll_nodes[i].node_id} pattern = {list_off_ll_nodes[i].pattern}")


def print_subtree_detection_codes(cspm_tree_nodes_list):
    for i in range(0, len(cspm_tree_nodes_list)):
        print(f"{i}: node id {cspm_tree_nodes_list[i].node_id} subtree_detection_code = {cspm_tree_nodes_list[i].subtree_detection_code}")


def pattern_sort_func(a, b):
    if a[0] > b[0]:
        return -1
    elif a[0] == b[0]:
        if a[1] < b[1]:
            return -1
        else:
            return 1
    else:
        return 1


def print_all_the_candidates(support_table):
    for support in support_table:
        if support_table[support].caphe_node is not None:
            print(f"support = {support}")
            support_table[support].caphe_node.print_caphe_node()


def print_all_the_closed(support_table, specific=None):
    if specific is not None:
        print(f"#####only one will be printed, support = {specific}")
        support_table[specific].closed_patterns_with_trie[0].print_patterns(type=0)
    else:
        for support in support_table:
            if support_table[support].closed_patterns_with_trie[0] is not None:
                print(f"support = {support}")
                support_table[support].closed_patterns_with_trie[0].print_patterns(type=0)


def checking_the_nodes_order(pattern, cspm_tree_nodes):
    print(f"pattern = {pattern}")
    for i in range(0, len(cspm_tree_nodes)-1):
        prev = cspm_tree_nodes[i].subtree_detection_code[0:len(cspm_tree_nodes[i].subtree_detection_code)-cspm_tree_nodes[i].depth+1]
        current = cspm_tree_nodes[i+1].subtree_detection_code[0:len(cspm_tree_nodes[i+1].subtree_detection_code)-cspm_tree_nodes[i+1].depth+1]
        v = same_subtree_checking(pattern_node=cspm_tree_nodes[i+1], super_pattern_node=cspm_tree_nodes[i])
        print(f"{v} {prev} {current} {cspm_tree_nodes[i].depth} {cspm_tree_nodes[i+1].depth}")
        if v < 0:
            continue
        else:
            print(f"problem {prev} {cspm_tree_nodes[i].depth} {current} {cspm_tree_nodes[i+1].depth}")
            print_subtree_detection_codes(cspm_tree_nodes_list=cspm_tree_nodes)
            v = 1
            assert(v==0)

def print_support_min_heap(support_min_heap):
    save = []
    for i in range(0, len(support_min_heap)):
        save.append(support_min_heap[i].priority)
    print(save)


def print_sanity_check_pattern_trie(head, tail):
    # trying to check if all the links have been perfectly established
    start = head
    while start is not None:
        print(f"WOW CHOLE {start.pattern}")
        if start.next is None: # Tail checking
            assert(start == tail)
        else:
            assert(start.next.prev == start)
        start = start.next


def print_pattern_from_ll_nodes(_list):
    # any sort of linked list of nodes
    for i in range(0, len(_list)):
        print(f"{_list[i].pattern}")

def searching_a_pattern_in_ll(start, pattern):
    verdict = False
    while start is not None:
        if start.pattern is not None:
            if(str(start.pattern) == str(pattern)):
                return True
        start = start.next
    return False
