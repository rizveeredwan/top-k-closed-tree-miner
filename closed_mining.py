from data_structure import Caphe, SupportTableEntry, CapheNode, MinHeap, PatternExtensionLinkedList
from utilities import enclosure_absorption_check

import heapq
from collections import deque

WORKING_WITH_PATTERN = None


def find_last_item_bitset(last_event):
    value = 0
    for i in range(0, len(last_event)):
        value = value | (1 << last_event[i])
    return value


def check_projection_completeness(projection_status):
    for i in range(0, len(projection_status)):
        if projection_status[i] == 0:
            return False  # Not complete
    return True  # complete


def extend_pattern_string(pattern, item, type_ex):
    # extending pattern string by one length
    new_pattern = []
    for i in range(0, len(pattern)):
        new_pattern.append([])
        for j in range(0, len(pattern[i])):
            new_pattern[i].append(pattern[i][j])
    if type_ex == "SE":
        new_pattern.append([item])
    else:
        new_pattern[-1].append(item)
    return new_pattern


class KCloTreeMiner:
    def __init__(self):
        self.support_table = SupportTableEntry()

        self.support_min_heap = []

        # CaPHe data structure
        self.caphe = Caphe()

        self.mined_pattern = 0
        self.mine_nature = "generic"  # generic, group, unique
        self.closed_pattern_cache = {}

    def find_i_ex(self, _list, pattern):
        # finding all the items that might extend it as the itemset extension
        last_item = pattern[-1][-1]
        i_ex = []
        for i in range(0, len(_list)):
            if _list[i][0] > last_item:
                i_ex.append(_list[i][0])
        return i_ex

    def create_key_support_table(self, support):
        # creating entry in the support table for the first time
        self.support_table.caphe_node_dict[support] = CapheNode(support=support)
        # conjugate entry in min heap
        heapq.heappush(self.support_min_heap, MinHeap(priority=support))
        # insert this Caphe node in Caphe
        self.caphe.push(caphe_node=self.support_table.caphe_node_dict[support])
        return

    def delete_whole_entry_from_support_table(self, support):
        # all the information deletion from the support table and CaPHe
        # delete the smallest support from min heap
        heapq.heappop(self.support_min_heap)  # O(logn)
        # extracting the caphe node and deleting it
        caphe_node = self.support_table.caphe_node_dict[support]
        self.caphe.pop(special_node=caphe_node)  # O(logn)
        del caphe_node
        del self.support_table.caphe_node_dict[support]

    def pattern_extension(self, cspm_tree_nodes, projection_status, item, minsup, type_of_extension,
                          last_event_bitset=None):
        # type_of_extension: SE/IE
        global WORKING_WITH_PATTERN
        queue = deque([])
        current_support = 0
        final_list_head = PatternExtensionLinkedList(node=None, projection_status=None)
        current = final_list_head
        for i in range(0, len(cspm_tree_nodes)):
            assert (projection_status[i] == 0 or projection_status[i] == 1)  # intermediate vs completed
            n = PatternExtensionLinkedList(node=cspm_tree_nodes[i], projection_status=projection_status[i])
            current.insert(node=n, prev_node=current)
            current = n
            if projection_status[i] == 0:
                queue.append(n)  # Each PatternExtensionLinkedList object
            current_support += cspm_tree_nodes[i].count
        # print("length ", len(queue))
        while len(queue) > 0:
            """
            if WORKING_WITH_PATTERN is True:
                print("length ", len(queue))
                final_list_head.print(node=final_list_head)
            """
            if current_support < minsup:  # Fall under expected support threshold
                break  # no node, no possible extension
            n = queue.popleft()
            assert (n.projection_status == 0)  # intermediate processed node
            cspm_tree_node = n.node
            current_support -= n.node.count  # cspm_tree_support reduction
            down_nodes, down_support = n.node.get_next_link_nodes(node=n.node, item=item)
            ll_nodes = final_list_head.replace_with_subtree(old_linked_list_node=n, updated_cspm_tree_nodes=down_nodes)
            # print(f"ll_nodes {len(ll_nodes)}")
            for i in range(0, len(ll_nodes)):
                current_support += ll_nodes[i].node.count
                if type_of_extension == "SE":  # SE
                    if ll_nodes[i].node.event_no > cspm_tree_node.event_no:  # condition matched
                        ll_nodes[i].projection_status = 1  # processed
                    else:  # in the same event, need to go forward
                        queue.append(ll_nodes[i])
                elif type_of_extension == "IE":  # IE
                    assert (last_event_bitset is not None)
                    if (ll_nodes[i].node.parent_item_bitset & last_event_bitset) == last_event_bitset:
                        ll_nodes[i].projection_status = 1  # Processed, condition matched
                    else:  # all the desired items not found in the same event
                        queue.append(ll_nodes[i])
        current = final_list_head.next
        projected_node_list = []
        projected_node_status = []
        while current is not None:
            projected_node_list.append(current.node)
            projected_node_status.append(current.projection_status)
            current = current.next
        # projection nodes, node statuses(0/1) and current support
        return projected_node_list, projected_node_status, current_support

    def remove_smaller_closed_patterns(self, pattern, cspm_tree_nodes, projection_status, caphe_node):
        enclosed = enclosure_absorption_check(pattern=pattern, cspm_tree_nodes=cspm_tree_nodes,
                                              projection_status=projection_status,
                                              caph_node=caphe_node, pattern_type="closed")

        # removing all the 1-length small enclosed patterns
        for i in range(0, len(enclosed)):
            deleted_pb = caphe_node.pop(caphe_node=caphe_node, deleted_pb=enclosed[i], pattern_type="closed",
                                        NODE_MAPPER=None)
            if self.mine_nature == "generic" or self.mine_nature == "unique":
                self.mined_pattern -= 1
            del deleted_pb
        return

    def decision_for_each_pattern(self, pattern, support, cspm_tree_nodes, cspm_tree_node_bitset, projection_status,
                                  s_ex, i_ex, NODE_MAPPER):
        # heap_type = "bounded" means only K unique supports else just put whatever comes
        # For each pattern the workflow of the decision, where to put, what to set, what to delete
        # putting the pattern in the CaPHE
        if self.support_table.caphe_node_dict.get(support) is None:
            self.create_key_support_table(support)  # creating a CaPHe node
        # enclosure, absorption check - small to larger patterns are expanding
        # current pattern might enclose/absorb only one length lesser patterns if projection is complete
        caphe_node = self.support_table.caphe_node_dict.get(support)

        # identify the candidates within same support that are closed
        enclosure_absorption_check(pattern=pattern, cspm_tree_nodes=cspm_tree_nodes,
                                   projection_status=projection_status,
                                   caph_node=caphe_node, pattern_type="candidate")
        # inserting a new candidate in CaPHe
        closed_flag = 1
        pb = caphe_node.insert_pattern(pattern_type="candidate", caphe_node=caphe_node,
                                       pattern=pattern, cspm_tree_nodes=cspm_tree_nodes,
                                       cspm_tree_node_bitset=cspm_tree_node_bitset,
                                       projection_status=projection_status, s_ex=s_ex, i_ex=i_ex,
                                       closed_flag=closed_flag)
        return pb

    def k_clo_tree_miner(self, cspm_tree_root, K=2, NODE_MAPPER=None, mining_type="generic"):
        self.mine_nature = mining_type
        # mining_type = "generic" or "group" or "unique
        # the mining algorithm starting point
        global WORKING_WITH_PATTERN
        # Find frequent 1 itemset
        list_of_items = []
        if cspm_tree_root.down_next_link_ptr is None:
            return None  # Nothing is in the tree
        for item in cspm_tree_root.down_next_link_ptr:
            # getting the next link nodes node.nl[alpha] = {}
            next_link_nodes, support = cspm_tree_root.get_next_link_nodes(node=cspm_tree_root, item=item)
            projection_status = [1 for i in range(0, len(next_link_nodes))]
            list_of_items.append([item, support, next_link_nodes, projection_status])
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
        list_of_items = list_of_items[0:last_idx + 1]  # pruning a portion of the highest K unique supports
        s_ex = []
        for i in range(0, len(list_of_items)):
            s_ex.append(list_of_items[i][0])
        # single list of items
        for i in range(0, len(list_of_items)):
            pattern = [[list_of_items[i][0]]]  # [[a]]
            support = list_of_items[i][1]
            cspm_tree_nodes = list_of_items[i][2]
            projection_status = list_of_items[i][3]
            i_ex = self.find_i_ex(_list=list_of_items, pattern=pattern)
            self.decision_for_each_pattern(pattern=pattern, support=support, cspm_tree_nodes=cspm_tree_nodes,
                                           cspm_tree_node_bitset=None, projection_status=projection_status, s_ex=s_ex,
                                           i_ex=i_ex, NODE_MAPPER=NODE_MAPPER)

        iteration = 0
        while self.mined_pattern < K and len(self.caphe.nodes) > 0:
            print(f"ITERATION STARTED")
            iteration += 1
            caphe_node = self.caphe.front()  # CaPHe node extraction
            pb = caphe_node.pop(caphe_node=caphe_node, deleted_pb=None, pattern_type="candidate",
                                NODE_MAPPER=None)  # pattern extraction
            if pb is None:  # No more candidates
                self.caphe.pop()
                if self.mine_nature == "group":
                    self.mined_pattern += 1
                continue  # with next highest support
            else:
                # print("trying with  ", pb.pattern, caphe_node.support, pb.projection_status)
                # self.caphe.print()
                verdict = check_projection_completeness(projection_status=pb.projection_status)
                if verdict is False:
                    # parent's projection is not complete
                    if len(pb.pattern[-1]) == 1:  # SE
                        type_of_extension = "SE"
                        last_event_bitset = 0
                    else:
                        type_of_extension = "IE"
                        last_event_bitset = find_last_item_bitset(
                            last_event=pb.pattern[-1][0:-1])  # except the last item all the remaining items
                    projection, projection_status, current_support = self.pattern_extension(
                        cspm_tree_nodes=pb.cspm_tree_nodes,
                        projection_status=pb.projection_status,
                        item=pb.pattern[-1][-1], minsup=caphe_node.support, type_of_extension=type_of_extension,
                        last_event_bitset=last_event_bitset)
                    if caphe_node.support > current_support > 0 and len(projection) > 0:
                        # it falls behind min_sup, try to add back in CaPHe
                        self.decision_for_each_pattern(pattern=pb.pattern, support=current_support,
                                                       cspm_tree_nodes=projection,
                                                       cspm_tree_node_bitset=None, projection_status=projection_status,
                                                       s_ex=pb.s_ex, i_ex=pb.i_ex, NODE_MAPPER=NODE_MAPPER)
                        continue  # start trying with the next pattern
                    else:  # it has full-filled minsup, updating the projection and projection status
                        pb.cspm_tree_nodes = projection
                        pb.cspm_tree_node_bitset = None
                        pb.projection_status = projection_status

                if len(pb.cspm_tree_nodes) == 0:
                    # print no valid projection node to work with
                    continue
                # its projection is done, it might remove some already found closed patterns

                print(f"starting pattern {pb.pattern} {caphe_node.support} {pb.projection_status}")
                assert (len(pb.cspm_tree_nodes) > 0)
                # Here came so we can make extensions
                last_event_bitset = 0
                new_s_ex, new_i_ex = [], []
                s_ex_pbs, i_ex_pbs = [], []
                if pb.s_ex_needed == 1:
                    for i in range(0, len(pb.s_ex)):
                        projection, projection_status, current_support = self.pattern_extension(
                            cspm_tree_nodes=pb.cspm_tree_nodes,
                            projection_status=[0 for c in range(len(pb.cspm_tree_nodes))],
                            item=pb.s_ex[i], minsup=caphe_node.support,
                            type_of_extension="SE",
                            last_event_bitset=last_event_bitset)
                        print(f" SE extensions  {pb.s_ex[i]} {current_support} {projection_status}")
                        if current_support == caphe_node.support:
                            pb.closed_flag = 0  # can never be closed
                        if caphe_node.support >= current_support > 0 and len(projection) > 0:  # it failed to satisfy
                            new_pattern = extend_pattern_string(pattern=pb.pattern, item=pb.s_ex[i], type_ex="SE")
                            new_pb = self.decision_for_each_pattern(
                                pattern=new_pattern,
                                support=current_support,
                                cspm_tree_nodes=projection,
                                cspm_tree_node_bitset=None, projection_status=projection_status,
                                s_ex=None, i_ex=None, NODE_MAPPER=None)
                            s_ex_pbs.append(new_pb)
                            new_s_ex.append(pb.s_ex[i])
                else:
                    new_s_ex = pb.s_ex
                # IE
                last_event_bitset = find_last_item_bitset(last_event=pb.pattern[-1])
                for i in range(0, len(pb.i_ex)):
                    projection, projection_status, current_support = self.pattern_extension(
                        cspm_tree_nodes=pb.cspm_tree_nodes,
                        projection_status=[0 for c in range(len(pb.cspm_tree_nodes))],
                        item=pb.i_ex[i], minsup=caphe_node.support,
                        type_of_extension="IE",
                        last_event_bitset=last_event_bitset)
                    print(f" IE extensions  {pb.i_ex[i]} {current_support} {projection_status}")
                    if current_support == caphe_node.support:
                        pb.closed_flag = 0  # can never be closed
                    if caphe_node.support >= current_support > 0 and len(projection) > 0:  # it failed to satisfy
                        new_pattern = extend_pattern_string(pattern=pb.pattern, item=pb.i_ex[i], type_ex="IE")
                        new_pb = self.decision_for_each_pattern(
                            pattern=new_pattern,
                            support=current_support,
                            cspm_tree_nodes=projection,
                            cspm_tree_node_bitset=None, projection_status=projection_status,
                            s_ex=None, i_ex=None, NODE_MAPPER=None)
                        i_ex_pbs.append(new_pb)
                        new_i_ex.append(pb.i_ex[i])

            if pb.closed_flag == 1:  # pb is identified as closed pattern
                if self.mine_nature == "generic" or self.mine_nature == "unique":
                    self.mined_pattern += 1
                caphe_node.insert_pattern(pattern_type="closed", caphe_node=caphe_node, pattern=pb.pattern,
                                          cspm_tree_nodes=pb.cspm_tree_nodes, cspm_tree_node_bitset=None,
                                          projection_status=pb.projection_status, s_ex=None, i_ex=None, closed_flag=1)
                # A closed pattern will enclose smaller sub patterns that have same support ar it
                self.remove_smaller_closed_patterns(pattern=pb.pattern, cspm_tree_nodes=pb.cspm_tree_nodes,
                                                    projection_status=pb.projection_status, caphe_node=caphe_node)
                if self.mine_nature == "unique":
                    # removing all the CSPs
                    empty_caphe_nodes = []
                    for sup in self.support_table.caphe_node_dict:
                        if sup < caphe_node.support:
                            self.remove_smaller_closed_patterns(pattern=pb.pattern, cspm_tree_nodes=pb.cspm_tree_nodes,
                                                                projection_status=pb.projection_status,
                                                                caphe_node=self.support_table.caphe_node_dict[sup])
                            if self.support_table.caphe_node_dict[sup].stored_patterns[0] is None and self.support_table.caphe_node_dict[sup].stored_patterns[1] is None:
                                empty_caphe_nodes.append(sup)
                    itr = 0
                    while itr < len(empty_caphe_nodes):
                        del self.support_table.caphe_node_dict[empty_caphe_nodes[itr]]
                        itr += 1

            # updating the s_ex and i_ex blocks
            for i in range(0, len(s_ex_pbs)):
                new_pb = s_ex_pbs[i]
                new_pb.s_ex = new_s_ex
                new_pb.i_ex = []
                for j in range(0, len(new_s_ex)):
                    if new_s_ex[j] > new_pb.pattern[-1][-1]:
                        new_pb.i_ex.append(new_s_ex[j])
            for i in range(0, len(i_ex_pbs)):
                new_pb = i_ex_pbs[i]
                new_pb.s_ex = new_s_ex
                new_pb.i_ex = []
                for j in range(0, len(new_i_ex)):
                    if new_i_ex[j] > new_pb.pattern[-1][-1]:
                        new_pb.i_ex.append(new_i_ex[j])
            """
            if iteration == 50:
                break
            """
            print("ITERATION ENDED")
            # self.caphe.print()
        print("Printing all the closed patterns")
        self.caphe.print_all_closed_patterns(self.support_table)


if __name__ == "__main__":
    _list = [1, 2, 3, 4]
    bitset = [1 for i in range(len(_list))]
    print(bitset)
