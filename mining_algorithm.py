import heapq
from collections import deque

from debug_functions import DebugFunctions
from data_structure import *

debug = DebugFunctions()


def generate_bitset_from_nodeids(cspm_tree_nodes):
    # generating bitset from node ids
    # complexity: O(1)
    # https://www.quora.com/Why-is-bit-shifting-regarded-as-an-O-1-operation-and-not-O-n-where-n-is-the-number-of-bits-shifted
    value = 0
    for i in range(len(cspm_tree_nodes)):
        value = value | (1 << cspm_tree_nodes[i].node_id)
    return value

class MiningAlgorithm:
    def __init__(self):
        self.support_table = {} # support: { patterns that are closed, candidate node in Caphe,  presence in min heap}

        self.support_min_heap = []

        #CaPHe data structure
        self.caphe = Caphe()


    def pattern_extension(self, cspm_tree_nodes, item, min_sup_threshold, type_of_extension, last_event_bitset=None):
        queue = deque([])
        current_support = 0
        final_list_head = PatternExtensionLinkedList(None,-1)
        current = final_list_head
        for i in range(0, len(cspm_tree_nodes)):
            n = PatternExtensionLinkedList(node=cspm_tree_nodes, level=0)
            current.insert(node=n)
            current = n
            queue.append(n) # [node, level, base node number for which searching the solution]
            current_support += cspm_tree_nodes[i].count
        while len(queue) > 0:
            n = queue.popleft()
            cspm_tree_node = n.node
            current_support -= n.node.count # cspm_tree_support reduction
            down_nodes, down_support = n.node.get_next_link_nodes(node=n.node, item=item)
            if current_support + down_support < min_sup_threshold:
                return None # no node, no possible extension
            ll_nodes = final_list_head.replace(old_linked_list_node=n, updated_cspm_tree_nodes=down_nodes)
            for i in range(0, len(ll_nodes)):
                if type_of_extension == 0: # SE
                    if ll_nodes[i].level == 1: # First level
                        if ll_nodes[i].node.event_no > cspm_tree_node.event_no: # condition matched
                            continue
                        else: # in the same event, need to go forward
                            queue.append(ll_nodes[i])
                    else: # others
                        queue.append(ll_nodes[i])   # keeping the nodes here
                elif type_of_extension == 1: # IE
                    assert(last_event_bitset is not None)
                    if ll_nodes[i].level == 1:  # First level
                        if ll_nodes[i].node.event_no == cspm_tree_node.event_no: # condition matched
                            continue
                        else: # not in the same event, need to go forward
                            queue.append(ll_nodes[i])
                    else:
                        if (ll_nodes[i].node.parent_item_bitset & last_event_bitset) == last_event_bitset:
                            continue # condition matched
                        else:  # all the desired items not found in the same event
                            queue.append(ll_nodes[i])
        current = final_list_head.next_link
        extended = []
        while current is not None:
            extended.append(current.node)
            current = current.next_link
        return extended

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
        assert(self.support_table.get(support) is not None)
        pass
    def new_closed_pattern_addition(self, pattern, support):
        pass
    def delete_whole_entry_from_support_table(self, support):
        # all the information deletion from the support table
        # delete from min heap
        heapq.heappop(self.support_min_heap) # O(logn)
        # delete from caphe, caphe_node
        caphe_node = self.support_table[support].caphe_node
        self.caphe.pop(special_node=caphe_node) # O(logn)
        del caphe_node
        # delete closed pattern linked list
        if self.support_table[support].closed_patterns is not None:
            del self.support_table[support].closed_patterns
        del self.support_table[support]

    def patterns_candidacy_check(self, pattern, support, cspm_tree_nodes, cspm_tree_node_bitset):
        # a pattern that need to be a candidate or not, that verdict
        return True,None # True: Can be candidate, None: Can be closed still

    def decision_for_each_pattern(self, pattern, support, cspm_tree_nodes, cspm_tree_node_bitset, s_ex, i_ex, K):
        # For each pattern the workflow of the decision, where to put, what to set, what to delete
        if len(self.support_table) < K:
            # we still have not received the most frequent top K elements
            if self.support_table.get(support) is None:  # this support does not exist
                # Dictionary entry creation
                self.create_key_support_table(support=support) # dictionary entry, min heap, caphe node
            # candidate pattern detection and insertion
            candidacy_verdict, closed_possible_flag = self.patterns_candidacy_check(pattern, support, cspm_tree_nodes, cspm_tree_node_bitset)
            if candidacy_verdict is True: # this has to be inserted as a candidate
                # insert pattern as a candidate in the corresponding caphe node
                caphe_node = self.support_table[support].caphe_node
                assert(caphe_node is not None)
                caphe_node.insert_pattern(caphe_node=caphe_node, pattern=pattern, cspm_tree_nodes=cspm_tree_nodes,
                                          cspm_tree_node_bitset=cspm_tree_node_bitset, s_ex=s_ex, i_ex=i_ex, flag=closed_possible_flag)
        elif len(self.support_table) == K:
            # the quota already filled up of k unique patterns, might need to delete some
            if self.support_min_heap[0] > support: # no upate required, already have best K values
                assert(self.support_table.get(support) is not None)
                return
            elif self.support_min_heap[0] < support and self.support_table.get(support) is None: # the minimum one have less support delete this , insert new
                # this support should not be in the table
                self.delete_whole_entry_from_support_table(support=support)
                # insert new support
                # Dictionary entry creation
                self.create_key_support_table(support=support)  # dictionary entry, min heap, caphe node
                # candidate pattern detection and insertion
                candidacy_verdict, closed_possible_flag = self.patterns_candidacy_check(pattern=pattern, support=support,
                                                                                        cspm_tree_nodes=cspm_tree_nodes,
                                                                                        cspm_tree_node_bitset=cspm_tree_node_bitset)
                if candidacy_verdict is True:  # this has to be inserted as a candidate
                    # insert pattern as a candidate in the corresponding caphe node
                    caphe_node = self.support_table[support].caphe_node
                    assert (caphe_node is not None)
                    caphe_node.insert_pattern(caphe_node=caphe_node, pattern=pattern, cspm_tree_nodes=cspm_tree_nodes,
                                              cspm_tree_node_bitset=cspm_tree_node_bitset, s_ex=s_ex, i_ex=i_ex,
                                              flag=closed_possible_flag)

            elif self.support_min_heap[0] < support and self.support_table.get(support) is not None: # the minimum one have less support delete this , insert new
                # this support is already in the table
                # candidate pattern detection and insertion
                candidacy_verdict, closed_possible_flag = self.patterns_candidacy_check(pattern=pattern,
                                                                                        support=support,
                                                                                        cspm_tree_nodes=cspm_tree_nodes,
                                                                                        cspm_tree_node_bitset=cspm_tree_node_bitset)
                if candidacy_verdict is True:  # this has to be inserted as a candidate
                    # insert pattern as a candidate in the corresponding caphe node
                    caphe_node = self.support_table[support].caphe_node
                    assert (caphe_node is not None)
                    caphe_node.insert_pattern(caphe_node=caphe_node, pattern=pattern, cspm_tree_nodes=cspm_tree_nodes,
                                              cspm_tree_node_bitset=cspm_tree_node_bitset, s_ex=s_ex, i_ex=i_ex,
                                              flag=closed_possible_flag)

    def find_frequent_itemset(self, cspm_tree_root, K=2, NODE_MAPPER=None):
        minsup = 1 # starting min sup
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
        for i in range(0, len(list_of_items)):
            pattern = [[list_of_items[i][0]]] # [[a]]
            support = list_of_items[i][1]
            cspm_tree_nodes = list_of_items[i][2]


if __name__ == '__main__':
    pass




