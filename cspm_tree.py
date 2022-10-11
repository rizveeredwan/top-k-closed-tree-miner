
from debug_functions import DebugFunctions
debug_obj = DebugFunctions()

# index of nodes to track
global_node_count = 0


class CSPMTree:
    def __init__(self):
        self.node_id = 0  # each node will have a particular node number
        self.item = None  # item
        self.event_no = -1  # event no
        self.parent_node = None
        self.parent_item_bitset = 0  # bitset value
        self.child_link = None  # [item, event_no] combination
        self.count = 0  # how many times this node has been visited

        # for traversal through next link for ancestor nodes
        self.side_next_link_prev = None
        self.side_next_link_next = None

        # next link section #
        self.down_next_link_ptr = None  # {a:st,end; b:st, en}

        # item freq attribute
        self.item_freq = {}

        #############

    def initializing_sp_tree_node(self, item, event_no, parent_node, parent_item_bitset, count):
        global global_node_count
        global_node_count += 1
        # print("Global node count ", global_node_count)
        node = CSPMTree()
        node.node_id = global_node_count
        node.item = item
        node.event_no = event_no
        node.parent_node = parent_node
        node.parent_item_bitset = parent_item_bitset
        node.count = count
        return node

    def add_intermediary_node(self, node1, node2):
        if node1.side_next_link_next is None:
            node1.side_next_link_next = node2
            node2.side_next_link_prev = node1
        if node1.side_next_link_next is not None: # (node1, temp) -> (node1, node2, temp)
            temp = node1.side_next_link_next
            node1.side_next_link_next = node2
            node2.side_next_link_prev = node1
            node2.side_next_link_next = temp
            temp.side_next_link_prev = node2
        return

    def create_links(self, parent, child, link_created=False):
        if parent.down_next_link_ptr is None:
            # assert (child.side_next_link_next is None and child.side_next_link_prev is None)
            parent.down_next_link_ptr= {child.item: [child, child]}
            return True, False # need to send child upward, no link created
        if parent.down_next_link_ptr.get(child.item) is None:
            # assert (child.side_next_link_next is None and child.side_next_link_prev is None)
            parent.down_next_link_ptr[child.item] = [child, child] # a single connection
            return True, False # need to send child upward, no link created
        if parent.down_next_link_ptr[child.item][0] != parent.down_next_link_ptr[child.item][1]: # embeded inside
            #print(child.side_next_link_next, child.side_next_link_prev)
            #print(parent.down_next_link_ptr[child.item][0].node_id, parent.down_next_link_ptr[child.item][1].node_id)
            #print(debug_obj.moves(parent.down_next_link_ptr[child.item][0], parent.down_next_link_ptr[child.item][1]))
            if link_created is False:
                assert (child.side_next_link_next is None and child.side_next_link_prev is None)
                self.add_intermediary_node(node1=parent.down_next_link_ptr[child.item][1], node2=child)
                parent.down_next_link_ptr[child.item][1] = child
                return True, True # need to send upward, link created
            if link_created is True:
                # stretch from end
                if child.side_next_link_prev == parent.down_next_link_ptr[child.item][1]:
                    parent.down_next_link_ptr[child.item][1] = child
                    return True, True  # need to send upward, link created
                if child.side_next_link_next == parent.down_next_link_ptr[child.item][0]:
                    parent.down_next_link_ptr[child.item][0] = child
                    return True, True  # need to send upward, link created
                else:
                    return False, True  # already enclosed, link created
        if parent.down_next_link_ptr[child.item][0] == parent.down_next_link_ptr[child.item][1]: # a single node existed
            if link_created is False:
                assert(child.side_next_link_next is None and child.side_next_link_prev is None)
                self.add_intermediary_node(node1=parent.down_next_link_ptr[child.item][0], node2=child)
                link_created = True
            parent.down_next_link_ptr[child.item][1] = child
            return True, link_created # need to send upward, link created

    def insert(self, sp_tree_node, processed_sequence, event_no, item_no, event_bitset, successors, seq_sum):
        # print("event ", event_no, item_no)
        global global_node_count
        if event_no >= len(processed_sequence):
            return
        if item_no >= len(processed_sequence[event_no]):
            self.insert(sp_tree_node, processed_sequence, event_no + 1, 0, 0, successors, seq_sum)
            return
        item = processed_sequence[event_no][item_no]
        if sp_tree_node.child_link is None:
            sp_tree_node.child_link = {}
        if sp_tree_node.child_link.get(item) is None:
            sp_tree_node.child_link[item] = {}
        node = sp_tree_node.child_link[item].get(event_no)  # 0 based, event_no
        new_node_created = False
        if node is None:
            node = self.initializing_sp_tree_node(item=item, event_no=event_no, parent_node=sp_tree_node,
                                                  parent_item_bitset=event_bitset, count=1)
            sp_tree_node.child_link[item][event_no] = node
            new_node_created = True

        """
        # First, mid, last updating to calculate CETable_s
        self.SequenceSummarizerSequenceExtensionUpdate(seq_sum, item, event_no + actual_event_no + 1)
        # updating the sequence summarizer table to perform CETable_i
        if (item_no >= 1):
            self.SequenceSummarizerItemsetExtensionUpdate(seq_sum, item, event_bitset)
        """
        self.insert(sp_tree_node=node, processed_sequence=processed_sequence, event_no=event_no,
                    item_no=item_no + 1, event_bitset=event_bitset | (1 << item), successors=successors,
                    seq_sum=seq_sum)
        # for upward pass
        if new_node_created is False:
            if successors.get(item) is not None:  # old node no need to update
                del successors[item]
        if new_node_created is True:  # need to set upward to set and establish link
            successors[item] = [node, False]
        # for this node update the information from the bottom
        del_keys = []
        for key in successors:
            child = successors[key][0]
            print(f"parent {sp_tree_node.node_id}, child {child.node_id} key {key} link_created{successors[key][1]}")
            upward_verdict, link_created_verdict = self.create_links(parent=sp_tree_node, child=child, link_created=successors[key][1])
            if upward_verdict is False:
                del_keys.append(key)
            successors[key][1] = link_created_verdict # True/False
            if sp_tree_node.down_next_link_ptr.get(key) is not None:
                print(sp_tree_node.node_id, key, sp_tree_node.down_next_link_ptr[key][0].node_id,
                      sp_tree_node.down_next_link_ptr[key][1].node_id)
                print(debug_obj.moves(sp_tree_node.down_next_link_ptr[key][0], sp_tree_node.down_next_link_ptr[key][1]))
                """
                print(sp_tree_node.node_id, key, sp_tree_node.down_next_link_ptr[key][0].item,
                      sp_tree_node.down_next_link_ptr[key][1].item)
                """
        for key in del_keys:
            del successors[key]
        return