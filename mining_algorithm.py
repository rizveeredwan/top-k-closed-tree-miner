import heapq
from collections import deque

from debug_functions import DebugFunctions
from data_structure import *
from pattern_quality_measure import *

debug = DebugFunctions()


def generate_bitset_from_nodeids(cspm_tree_nodes):
    # generating bitset from node ids
    # complexity: O(1)
    # https://www.quora.com/Why-is-bit-shifting-regarded-as-an-O-1-operation-and-not-O-n-where-n-is-the-number-of-bits-shifted
    value = 0
    for i in range(len(cspm_tree_nodes)):
        value = value | (1 << cspm_tree_nodes[i].node_id)
    return value


def find_last_item_bitset(pattern):
    p = pattern[-1]
    value = 0
    for i in range(0, len(p)):
        value = value | (1 << p[i])
    return value


class MiningAlgorithm:
    def __init__(self):
        self.support_table = {}  # support: { patterns that are closed, candidate node in Caphe,  presence in min heap}

        self.support_min_heap = []

        # CaPHe data structure
        self.caphe = Caphe()

    def pattern_extension(self, cspm_tree_nodes, item, minsup, type_of_extension, last_event_bitset=None):
        queue = deque([])
        current_support = 0
        final_list_head = PatternExtensionLinkedList(None, -1)
        current = final_list_head
        for i in range(0, len(cspm_tree_nodes)):
            n = PatternExtensionLinkedList(node=cspm_tree_nodes[i], level=0)
            current.insert(node=n, prev_node=current)
            current = n
            queue.append(n)  # [node, level, base node number for which searching the solution]
            current_support += cspm_tree_nodes[i].count
        heuristic_support = current_support  # heuristic support for heuristic pruning
        while len(queue) > 0:
            n = queue.popleft()
            cspm_tree_node = n.node
            current_support -= n.node.count  # cspm_tree_support reduction
            if n.level == 0:  # For heuristic calculation
                heuristic_support -= n.node.count
            down_nodes, down_support = n.node.get_next_link_nodes(node=n.node, item=item)
            # print(f"current_support {current_support} down_support {down_support} {minsup} {down_nodes}")
            if current_support + down_support < minsup:
                heuristic_support = heuristic_support + down_support
                return None, heuristic_support, current_support  # no node, no possible extension
            ll_nodes = final_list_head.replace(old_linked_list_node=n, updated_cspm_tree_nodes=down_nodes)
            for i in range(0, len(ll_nodes)):
                current_support += ll_nodes[i].node.count
                if type_of_extension == 0:  # SE
                    if ll_nodes[i].level == 1:  # First level
                        heuristic_support += ll_nodes[i].node.count  # updating heuristic for level 1
                        if ll_nodes[i].node.event_no > cspm_tree_node.event_no:  # condition matched
                            continue
                        else:  # in the same event, need to go forward
                            queue.append(ll_nodes[i])
                elif type_of_extension == 1:  # IE
                    assert (last_event_bitset is not None)
                    if ll_nodes[i].level == 1:  # First level
                        heuristic_support += ll_nodes[i].node.count  # updating heuristic for level 1
                        if ll_nodes[i].node.event_no == cspm_tree_node.event_no:  # condition matched
                            continue
                        else:  # not in the same event, need to go forward
                            queue.append(ll_nodes[i])
                    else:
                        if (ll_nodes[i].node.parent_item_bitset & last_event_bitset) == last_event_bitset:
                            continue  # condition matched
                        else:  # all the desired items not found in the same event
                            queue.append(ll_nodes[i])
        current = final_list_head.next_link
        extended = []
        while current is not None:
            extended.append(current.node)
            current = current.next_link
        return extended, heuristic_support, current_support

    def create_key_support_table(self, support):
        # creating entry in the support table for the first time
        self.support_table[support] = SupportTableEntry()
        self.support_table[support].caphe_node = CapheNode(support=support)
        # conjugate entry in min heap
        heapq.heappush(self.support_min_heap, MinHeap(priority=support))
        # insert this Caphe node in Caphe
        self.caphe.push(caphe_node=self.support_table[support].caphe_node)
        return

    def new_candidate_pattern_addition(self, pattern, support, cspm_tree_nodes, cspm_tree_node_bitset, s_ex, i_ex):
        assert (self.support_table.get(support) is not None)
        pass

    def delete_whole_entry_from_support_table(self, support):
        # all the information deletion from the support table
        # delete from min heap
        heapq.heappop(self.support_min_heap)  # O(logn)
        # delete from caphe, caphe_node
        caphe_node = self.support_table[support].caphe_node
        self.caphe.pop(special_node=caphe_node)  # O(logn)
        del caphe_node
        # delete closed pattern linked list
        if self.support_table[support].closed_patterns is not None:
            del self.support_table[support].closed_patterns
        del self.support_table[support]

    def patterns_quality_check(self, pattern, support, cspm_tree_nodes, cspm_tree_node_bitset, NODE_MAPPER):
        candidacy_flag, closed_flag = True, None
        # a pattern that need to be a candidate or not, that verdict along with closedness
        if self.support_table.get(support) is not None:
            # checking with closed patterns
            L1, L2 = closure_check(linked_list_nodes=self.support_table[support].closed_patterns, p=pattern)
            if len(L1) > 0 and len(L2) > 0:
                problem = 1
                print("Closed Pattern cross presence ", pattern)
                self.support_table[support].closed_patterns.print()
                assert (problem == 0)
            elif len(L1) > 0:
                assert (len(L1) == 1)  # in this case there should be only one that is enclosing
                closed_flag = 0  # can never be closed
                # absorption test
                absorption_status = absorption_check(list_of_ll_nodes=L1, nodes_of_p=cspm_tree_nodes, flag=0,
                                                     NODE_MAPPER=NODE_MAPPER)
                assert (len(absorption_status) == len(L1))
                if absorption_status[0] is True:
                    candidacy_flag = False
            elif len(L2) > 0:  # P has absorbed some
                # remove those closed patterns
                for i in range(0, len(L2)):
                    self.support_table[support].closed_patterns.delete(current=L2[i])
            if candidacy_flag is False:
                # currently, there is no pattern in the closed, that absorbs P
                # search in intermediates
                # check in candidate patterns
                L1, L2 = closure_check(linked_list_nodes=self.support_table[support].caphe_node.pattern_ll_node[1], p=pattern)
                if len(L1) > 0:
                    closed_flag = 0 # P can never be closed pattern
                    # *******can add faster return flag in absorption_status calculation
                    absorption_status = absorption_check(list_of_ll_nodes=L1, nodes_of_p=cspm_tree_nodes, flag=0, NODE_MAPPER=NODE_MAPPER)
                    for i in range(0, len(absorption_status)): # x in L1 encloses P
                        # x in L1 encloses and absorbs P, P is no more needed as candidate, corresponding pattern exists
                        if absorption_status[i] is True:
                            candidacy_flag = False
                            break
                if len(L2) > 0:
                    absorption_status = absorption_check(list_of_ll_nodes=L2, nodes_of_p=cspm_tree_nodes, flag=1,
                                                         NODE_MAPPER=NODE_MAPPER)
                    for i in range(0, len(absorption_status)):
                        if absorption_status[i] is True:
                            # this candidate is not needed any more, as absorbed
                            self.support_table[support].caphe_node.pattern_ll_node[1].delete_node(node=L2[i])
        # True/False: Can be/csn not be candidate, None/0: Can be/can never be closed still
        return candidacy_flag, closed_flag

    def decision_for_each_pattern(self, pattern, support, cspm_tree_nodes, cspm_tree_node_bitset, s_ex, i_ex, K,
                                  NODE_MAPPER):
        # For each pattern the workflow of the decision, where to put, what to set, what to delete
        # print(f"{pattern}, support {support}")
        if len(self.support_table) < K:
            # we still have not received the most frequent top K elements
            if self.support_table.get(support) is None:  # this support does not exist
                # Dictionary entry creation
                self.create_key_support_table(support=support)  # dictionary entry, min heap, caphe node
            # candidate pattern detection and insertion
            candidacy_verdict, closed_possible_flag = self.patterns_quality_check(pattern, support, cspm_tree_nodes,
                                                                                  cspm_tree_node_bitset, NODE_MAPPER)
            if candidacy_verdict is True:  # this has to be inserted as a candidate
                # insert pattern as a candidate in the corresponding caphe node
                caphe_node = self.support_table[support].caphe_node
                assert (caphe_node is not None)
                caphe_node.insert_pattern(caphe_node=caphe_node, pattern=pattern, cspm_tree_nodes=cspm_tree_nodes,
                                          cspm_tree_node_bitset=cspm_tree_node_bitset, s_ex=s_ex, i_ex=i_ex,
                                          flag=closed_possible_flag)
        elif len(self.support_table) == K:
            # the quota already filled up of k unique patterns, might need to delete some
            if self.support_min_heap[0].priority > support:  # no upate required, already have best K values
                assert (self.support_table.get(support) is None)
                return
            elif self.support_min_heap[0].priority < support and self.support_table.get(
                    support) is None:  # the minimum one have less support delete this , insert new
                # this support should not be in the table
                self.delete_whole_entry_from_support_table(support=support)
                # insert new support
                # Dictionary entry creation
                self.create_key_support_table(support=support)  # dictionary entry, min heap, caphe node
                # candidate pattern detection and insertion
                candidacy_verdict, closed_possible_flag = self.patterns_quality_check(pattern=pattern, support=support,
                                                                                      cspm_tree_nodes=cspm_tree_nodes,
                                                                                      cspm_tree_node_bitset=cspm_tree_node_bitset,
                                                                                      NODE_MAPPER=NODE_MAPPER)
                if candidacy_verdict is True:  # this has to be inserted as a candidate
                    # insert pattern as a candidate in the corresponding caphe node
                    caphe_node = self.support_table[support].caphe_node
                    assert (caphe_node is not None)
                    caphe_node.insert_pattern(caphe_node=caphe_node, pattern=pattern, cspm_tree_nodes=cspm_tree_nodes,
                                              cspm_tree_node_bitset=cspm_tree_node_bitset, s_ex=s_ex, i_ex=i_ex,
                                              flag=closed_possible_flag)

            elif self.support_min_heap[0].priority <= support and self.support_table.get(
                    support) is not None:  # the minimum one have less support delete this , insert new
                # this support is already in the table
                # candidate pattern detection and insertion
                candidacy_verdict, closed_possible_flag = self.patterns_quality_check(pattern=pattern, support=support,
                                                                                      cspm_tree_nodes=cspm_tree_nodes,
                                                                                      cspm_tree_node_bitset=cspm_tree_node_bitset,
                                                                                      NODE_MAPPER=NODE_MAPPER)
                if candidacy_verdict is True:  # this has to be inserted as a candidate
                    # insert pattern as a candidate in the corresponding caphe node
                    caphe_node = self.support_table[support].caphe_node
                    assert (caphe_node is not None)
                    caphe_node.insert_pattern(caphe_node=caphe_node, pattern=pattern, cspm_tree_nodes=cspm_tree_nodes,
                                              cspm_tree_node_bitset=cspm_tree_node_bitset, s_ex=s_ex, i_ex=i_ex,
                                              flag=closed_possible_flag)

    def find_i_ex(self, _list, pattern):
        # finding all the items that might extend it as the itemset extension
        last_item = pattern[-1][-1]
        i_ex = []
        for i in range(0, len(_list)):
            if _list[i][0] > last_item:
                i_ex.append(_list[i][0])
        return i_ex

    def remove_caphe_node_from_ds(self, support, caphe_node):
        # both nodes should match
        assert (caphe_node == self.caphe.front())
        self.caphe.pop(special_node=None)  # deleting the current best
        self.support_table[support].caphe_node = None  # no more caphe node for this support

    def return_current_possible_minsup(self, K):
        if len(self.support_min_heap) == K:  # setting up min heap
            minsup = self.support_min_heap[0].priority
        else:
            minsup = 1
        return minsup

    def pattern_update(self, pattern, item, ex_type):
        # ex_type: 0 -> SE, pattern{item}. 1->IE, {pattern, item}
        sup_pattern = []
        for i in range(0, len(pattern)):
            sup_pattern.append([])
            for j in range(0, len(pattern[i])):
                sup_pattern[i].append(pattern[i][j])
        if ex_type == 0:
            sup_pattern.append([item])
        elif ex_type == 1:
            sup_pattern[-1].append(item)
        return sup_pattern

    def find_frequent_itemset(self, cspm_tree_root, K=2, NODE_MAPPER=None):
        minsup = 1  # starting min sup
        # Find frequent 1 itemset
        list_of_items = []
        if cspm_tree_root.down_next_link_ptr is not None:
            for item in cspm_tree_root.down_next_link_ptr:
                # getting the next link nodes node.nl[alpha] = {}
                next_link_nodes, support = cspm_tree_root.get_next_link_nodes(node=cspm_tree_root, item=item)
                # print(cspm_tree_root.node_id, item, next_link_nodes, support)
                # print(f"item = {item}, support = {support}")
                # debug.print_set_of_nodes(nodes=next_link_nodes)
                list_of_items.append([item, support, next_link_nodes])
        # sorting and setting the min sup
        list_of_items.sort(key=lambda x: x[1], reverse=True)
        cnt = 1
        last_idx = len(list_of_items) - 1
        for i in range(1, len(list_of_items)):
            if list_of_items[i][1] != list_of_items[i - 1][1]:
                if cnt < K:
                    cnt += 1
                elif cnt == K:
                    last_idx = i - 1
                    break
        list_of_items = list_of_items[0:last_idx + 1]  # pruning a portion
        s_ex = []
        for i in range(0, len(list_of_items)):
            s_ex.append(list_of_items[i][0])
        # single list of items
        for i in range(0, len(list_of_items)):
            pattern = [[list_of_items[i][0]]]  # [[a]]
            support = list_of_items[i][1]
            cspm_tree_nodes = list_of_items[i][2]
            i_ex = self.find_i_ex(_list=list_of_items, pattern=pattern)
            self.decision_for_each_pattern(pattern=pattern, support=support, cspm_tree_nodes=cspm_tree_nodes,
                                           cspm_tree_node_bitset=None, s_ex=s_ex, i_ex=i_ex, K=K,
                                           NODE_MAPPER=NODE_MAPPER)

        print(len(self.caphe.nodes))
        self.caphe.print()
        while len(self.caphe.nodes) > 0:
            # Front element from caphe
            caphe_node = self.caphe.front()
            print(caphe_node.support)
            # print(caphe_node.print_caphe_node())
            output = caphe_node.pop_last_element(caphe_node, NODE_MAPPER=NODE_MAPPER)
            if output is None:  # all the patterns have been checked
                v = len(self.caphe.nodes)
                self.remove_caphe_node_from_ds(support=caphe_node.support, caphe_node=caphe_node)
                assert (len(self.caphe.nodes) == v - 1)
            else:  # some patterns still exist
                pattern, cspm_tree_nodes, cspm_tree_node_bitset, s_ex, i_ex, flag = output
                support = caphe_node.support
                # if no one has canceled this pattern's closedness, identify it as close
                if flag is None:  # this pattern can be closed (0 means not closed), update that information
                    self.support_table[support].closed_patterns.insert(current=self.support_table[support].closed_patterns,
                                                                    pattern=pattern, cspm_tree_nodes=cspm_tree_nodes,
                                                                    cspm_tree_node_bitset=cspm_tree_node_bitset)
                # checking the extensions, pattern extensions that support min support/minsup
                print(f"pattern {pattern} support {caphe_node.support}")
                last_event_bitset = find_last_item_bitset(pattern=pattern)
                heuristic = {}
                for i in range(0, len(s_ex)):
                    minsup = self.return_current_possible_minsup(K)
                    extended, heuristic_support, ext_support = self.pattern_extension(cspm_tree_nodes=cspm_tree_nodes,
                                                                                      item=s_ex[i], minsup=minsup,
                                                                                      type_of_extension=0,
                                                                                      last_event_bitset=last_event_bitset)
                    heuristic[s_ex[i]] = heuristic_support
                    if extended is not None:  # did not fail minsup, try to add it in the Caphe
                        sup_pattern = self.pattern_update(pattern=pattern, item=s_ex[i], ex_type=0)
                        self.patterns_quality_check(pattern=sup_pattern, support=ext_support, cspm_tree_nodes=extended,
                                                    cspm_tree_node_bitset=None, NODE_MAPPER=NODE_MAPPER)
                        # Debugging the function's quality
                        print("before")
                        self.support_table[support].closed_patterns.print()
                        candidacy_flag, closed_flag = self.patterns_quality_check(pattern=sup_pattern, support=ext_support,
                                                    cspm_tree_nodes=extended, cspm_tree_node_bitset=None, NODE_MAPPER=NODE_MAPPER)
                        print("extension ", extended, heuristic_support, ext_support, sup_pattern, candidacy_flag, closed_flag)
                        print("after")
                        self.support_table[support].closed_patterns.print()
                for i in range(0, len(i_ex)):
                    if heuristic.get(i_ex[i]) is not None:
                        if heuristic[i_ex[i]] < minsup:  # applying heuristic support
                            continue
                    minsup = self.return_current_possible_minsup(K)
                    extended, heuristic_support, ext_support = self.pattern_extension(cspm_tree_nodes=cspm_tree_nodes,
                                                                                      item=i_ex[i], minsup=minsup,
                                                                                      type_of_extension=1,
                                                                                      last_event_bitset=last_event_bitset)
                    if extended is not None:  # did not fail minsup, try to add it in the Caphe
                        sup_pattern = self.pattern_update(pattern=pattern, item=s_ex[i], ex_type=1)
                        self.patterns_quality_check(pattern=sup_pattern, support=ext_support, cspm_tree_nodes=extended,
                                                    cspm_tree_node_bitset=None, NODE_MAPPER=NODE_MAPPER)
                        print("extension ", extended, heuristic_support, ext_support, pattern, s_ex[i])

        print(f"minsup = {minsup}")
        print("DONE")


if __name__ == '__main__':
    pass
